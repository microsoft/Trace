import atexit
import copy
import os
import pickle
import re
from collections import defaultdict
from difflib import SequenceMatcher

import autogen

import opto.trace as trace
from opto.trace.nodes import node


class LLMCallable:
    def __init__(self, config_list=None, max_tokens=1024, verbose=False):
        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        self.llm = autogen.OpenAIWrapper(config_list=config_list)
        self.max_tokens = max_tokens
        self.verbose = verbose

    def call_llm(self, user_prompt):
        """
        Sends the constructed prompt (along with specified request) to an LLM.
        """
        system_prompt = "You are a helpful assistant.\n"
        if self.verbose not in (False, "output"):
            print("Prompt\n", system_prompt + user_prompt)

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        try:
            response = self.llm.create(
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception:
            response = self.llm.create(messages=messages, max_tokens=self.max_tokens)
        response = response.choices[0].message.content

        if self.verbose:
            print("LLM response:\n", response)
        return response


class BaseUtil:

    def extract_actions(self, text):
        pattern = re.compile(r'([A-Z])\. (\[.*?\](?: <.*?> \(\d+\))?(?:: .*?)?)')
        matches = pattern.findall(text)
        actions = {letter: action for letter, action in matches}
        return actions

    def unify_and_match_action(self, action_str, available_actions):
        # Remove trailing periods and leading action letters if present
        action_str = action_str.strip('.')

        # Check if action_str is just a letter
        if len(action_str) == 1 and action_str in available_actions:
            return available_actions[action_str]

        # Extract the actual action part from complex strings
        match = re.search(r'\[(.*?)\] <(.*?)> \((.*?)\)', action_str)
        if match:
            action_type, action_object, action_id = match.groups()
            action = f"[{action_type}] <{action_object}> ({action_id})"

            # Check for an exact match in available actions
            if action in available_actions.values():
                return action

            # Fuzzy match if exact match is not found
            return self.fuzzy_match_action(action, available_actions)

        return action_str  # Return the cleaned up action string if no complex format is detected

    def fuzzy_match_action(self, returned_action, available_actions):
        # Extract the action and object id from the returned action
        returned_match = re.search(r'\[(.*?)\] <(.*?)> \((.*?)\)', returned_action)
        if not returned_match:
            return None

        returned_action_type, returned_object, returned_id = returned_match.groups()

        # Initialize best match variables
        best_match = None
        highest_ratio = 0

        # Iterate over available actions to find the closest match
        for action in available_actions.values():
            match = re.search(r'\[(.*?)\] <(.*?)> \((.*?)\)', action)
            if match:
                action_type, action_object, action_id = match.groups()
                if action_id == returned_id and action_object == returned_object:
                    ratio = SequenceMatcher(None, returned_action_type, action_type).ratio()
                    if ratio > highest_ratio:
                        highest_ratio = ratio
                        best_match = action

        return best_match


def env_fn(env_id, env_task_set, executable_args, args):
    # from envs.unity_environment import UnityEnvironment

    return UnityEnvironment(num_agents=args.agent_num,
                            max_episode_length=args.max_episode_length,
                            port_id=env_id,
                            env_task_set=env_task_set,
                            agent_goals=['LLM' for i in range(args.agent_num)],
                            observation_types=[args.obs_type for i in range(args.agent_num)],
                            use_editor=args.use_editor,
                            executable_args=executable_args,
                            base_port=args.base_port if args.base_port is not None else np.random.randint(11000, 13000),
                            seed=args.seed,
                            recording_options={'recording': True if args.gen_video else False,
                                               'output_folder': args.record_dir,
                                               'file_name_prefix': args.mode,
                                               'cameras': 'PERSON_FROM_BACK',
                                               'modality': 'normal'}
                            )


class VirtualHomeEnv:
    def __init__(self, max_number_steps, run_id, env_fn, agent_fn, num_agents, record_dir='out', debug=False,
                 run_predefined_actions=False, comm=False, args=None):
        print("Init Env")
        self.converse_agents = []
        self.comm_cost_info = {
            "converse": {"overall_tokens": 0, "overall_times": 0},
            "select": {"tokens_in": 0, "tokens_out": 0}
        }

        self.dict_info = {}
        self.dict_dialogue_history = defaultdict(list)
        self.LLM_returns = {}

        self.arena_id = run_id
        self.env_fn = env_fn
        self.agent_names = ["Agent_{}".format(i + 1) for i in range(len(agent_fn))]

        self.prompt_template_path = args.prompt_template_path
        self.organization_instructions = args.organization_instructions

        env_task_set = pickle.load(open(args.dataset_path, 'rb'))

        # skipped a lot of logging

        args.record_dir = f'../test_results/{args.mode}'
        print("mode: {}".format(args.mode))
        os.path(args.record_dir).mkdir(parents=True, exist_ok=True)

        if "image" in args.obs_type or args.gen_video:
            os.system("Xvfb :94 & export DISPLAY=:94")
            import time
            time.sleep(3)  # ensure Xvfb is open
            os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
            executable_args = {
                'file_name': args.executable_file,
                'x_display': '94',
                'no_graphics': False,
                'timeout_wait': 5000,
            }
        else:
            executable_args = {
                'file_name': args.executable_file,
                'no_graphics': True,
                'timeout_wait': 500,
            }

        self.executable_args = executable_args
        self.args = args
        self.env_task_set = env_task_set

        env = env_fn(run_id, env_task_set, executable_args, args)
        self.env = env
        self.max_episode_length = self.env.max_episode_length
        self.max_number_steps = max_number_steps
        self.run_predefined_actions = run_predefined_actions
        atexit.register(self.close)

        self.agents = []
        self.num_agents = num_agents

        self.dialogue_history_len = 30

        for i in range(self.num_agents):
            self.agents.append(virtualhome_agent.LLM_agent(agent_id=i + 1, args=args))

    def reset(self, task_id=None, reset_seed=1111):
        self.cnt_duplicate_subgoal = 0
        self.cnt_nouse_subgoal = 0
        self.dict_info = {}
        self.dict_dialogue_history = defaultdict(list)
        self.LLM_returns = {}
        self.converse_agents = []
        self.comm_cost_info = {
            "converse": {"overall_tokens": 0, "overall_times": 0},
            "select": {"tokens_in": 0, "tokens_out": 0}
        }
        for i in range(self.num_agents):
            # reset conversable agents
            pass

        ob = None
        while ob is None:
            ob = self.env.reset(task_id=task_id, reset_seed=reset_seed)

        for it, agent in enumerate(self.agents):
            agent.reset(ob[it], self.env.all_containers_name, self.env.all_goal_objects_name, self.env.all_room_name,
                        self.env.room_info, self.env.goal_spec[it])

        # return observation required for planning
        obs = self.env.get_observations()
        agent_goal_specs = {}
        agent_goal_descs = {}
        agent_infos = {}
        agent_obs_descs = {}
        agent_obs = obs

        for it in range(self.num_agents):
            goal_spec = self.env.get_goal(self.env.task_goal[it], self.env.agent_goals[it])
            agent_goal_specs[it] = goal_spec
            info = self.agents[it].obs_processing(obs[it], goal_spec)

            agent_obs_descs[it] = self.agents[it].get_obs_forLLM_plan()
            agent_infos[it] = info
            agent_goal_descs[it] = self.agents[it].LLM.goal_desc

        # use these two, we can generate plans...
        return agent_obs, agent_obs_descs, agent_goal_specs, agent_goal_descs, agent_infos

    def close(self):
        self.env.close()

    def get_port(self):
        return self.env.port_number

    def reset_env(self):
        self.env.close()
        self.env = env_fn(self.arena_id, self.env_task_set, self.executable_args, self.args)

    def env_step(self, dict_actions):
        try:
            step_info = self.env.step(dict_actions)
        except Exception as e:
            print("Exception occurs when performing action: ", dict_actions)
            raise Exception

        return step_info

    def parse_send_message(self, input_string):
        # Define the regex pattern
        pattern = r'\[send_message\] <(?P<teammate_name>.*?)> \((?P<teammate_agent_id>.*?)\): (?P<message>.*)'

        # Search for the pattern in the input string
        match = re.search(pattern, input_string)

        # Check if the pattern was found and extract the groups
        if match:
            teammate_name = match.group('teammate_name')
            teammate_agent_id = match.group('teammate_agent_id')
            message = match.group('message')
            return teammate_name, teammate_agent_id, message
        else:
            return None, None, None

    def step(self, plans, agent_infos, LM_times, agent_obs, agent_goal_specs,
             prev_agent_obs_desc):

        dict_actions = {}

        # if neither agent's observation text is changing, we execute the same action
        # until it changes (sticky_action)

        # we set it to -1 reward if the action is invalid
        max_sticky_steps = 10
        while max_sticky_steps > 0:

            # sticky action option here
            break_loop = False

            for it, agent in enumerate(self.agents):
                dict_actions[it], self.dict_info[it] = agent.get_action(plans[it], agent_infos[it], LM_times[it],
                                                                        agent_obs[it], agent_goal_specs[it],
                                                                        dialogue_history=self.dict_dialogue_history)

            # one round of message sending, we check if any agent chooses to send message
            for it, agent in enumerate(self.agents):
                if dict_actions[it] is None:
                    continue

                if dict_actions[it].startswith('[send_message]'):
                    # send message to the other agents
                    teammate_name, teammate_agent_id, message = self.parse_send_message(dict_actions[it])
                    if teammate_name is not None:
                        # format of the message is: sender to receiver: message
                        self.dict_dialogue_history[teammate_name].append(
                            f"You send_message to {teammate_name}: {message}")
                        self.dict_dialogue_history[self.agent_names[it]].append(
                            f"{self.agent_names[it]} send_message to You: {message}")
                        # add to each agent's dialogue history
                        agent.dialogue_history.append(f"You send_message to {teammate_name}: {message}")
                        self.agents[int(teammate_agent_id) - 1].dialogue_history.append(
                            f"{self.agent_names[it]} send_message to You: {message}")

                    dict_actions[it] = None  # action is none
                    break_loop = True  # we continue exchanging messages

            step_info = self.env_step(dict_actions)
            # determine if both agents are seeing the same

            # obs is None by default for Unity env
            obs = self.env.get_observations()
            step_info = [obs, step_info[1], step_info[2], step_info[3], step_info[4]]
            agent_obs, reward, done, infos, messages = step_info

            agent_obs_descs = {}
            # we explicitly process it before generating the description
            for it in range(len(self.agents)):
                self.agents[it].obs_processing(agent_obs[it], agent_goal_specs[it])

            for it in range(len(self.agents)):
                agent_obs_descs[it] = self.agents[it].get_obs_forLLM_plan()

            if done:
                break

            # compare progress text with the original one (where we started)
            # compare the available actions
            # if both are the same, we continue without getting back to the LLM Agent

            for it in range(len(self.agents)):
                text = prev_agent_obs_desc[it]['prompts']
                pattern = r'(step \d+)'
                text = re.sub(pattern, f'step X', text)
                pattern = r'Progress:.*|Available actions:.*(?:\n.*\w.*)+'
                matches = re.findall(pattern, text)

                new_text = agent_obs_descs[it]['prompts']
                pattern = r'(step \d+)'
                new_text = re.sub(pattern, f'step X', new_text)
                pattern = r'Progress:.*|Available actions:.*(?:\n.*\w.*)+'
                new_matches = re.findall(pattern, new_text)

                if matches != new_matches:
                    break_loop = True
                    break

            if break_loop:
                break

            max_sticky_steps -= 1
            print("Performing the same action again...sticky counter is: ", max_sticky_steps)

        return step_info, agent_obs_descs, dict_actions, self.dict_info


class TracedEnv:
    def __init__(self, args):
        # find a way to turn off video recording to make it go faster

        # this is a deterministic environment
        args.comm = False

        args.prompt_template_path = "/piech/u/anie/Organized-LLM-Agents/envs/cwah/LLM/prompt_multi_comm.csv"

        args.action_history_len = 20
        args.dialogue_history_len = 30

        args.max_number_steps = 250
        args.run_id = 0
        args.agent_fn = [0] * 2
        args.num_agents = 2

        self.obs = None
        self.args = args
        self.env = TraceVirtualHome(args.max_number_steps, args.run_id,
                                    env_fn, args.agent_fn, args.num_agents, args=args)

        atexit.register(self.close)

    def close(self):
        self.env.close()
        del self.env

    def reset_env(self):
        self.env.close()
        self.env = TraceVirtualHome(self.args.max_number_steps, self.args.run_id,
                                    env_fn, self.args.agent_fn, self.args.num_agents, args=self.args)

    def reset(self, task_id=8):
        # doing the same wrapped approach as metaworld

        # TODO: increment run_id, make sure recording works for different driectory
        # or turn off video recording...
        try:
            agent_obs, agent_obs_descs, agent_goal_specs, agent_goal_descs, agent_infos = self.env.reset(
                task_id=task_id)
        except:
            self.reset_env()
            agent_obs, agent_obs_descs, agent_goal_specs, agent_goal_descs, agent_infos = self.env.reset(
                task_id=task_id)

        @bundle()
        def reset(agent_idx):
            return agent_obs_descs[agent_idx]['prompts']

        agent_obs_descs_node = {}
        for i in range(len(agent_obs_descs)):
            agent_obs_descs_node[i] = agent_obs_descs[i]
            agent_obs_descs_node[i]['prompts'] = reset(i)

        self.obs = agent_obs_descs_node

        return agent_obs, agent_obs_descs_node, agent_goal_specs, agent_goal_descs, agent_infos

    def step(self, plans, agent_infos, LM_times, agent_obs, agent_goal_specs, agent_obs_descs):
        # we are shielding a lot of the environment away...
        # we might get a different chain for each agent...that might be easier?
        # try:
        controls = {}
        for i in range(len(plans)):
            controls[i] = plans[i].data  # hard coded conversion
            # agent_obs_descs = [agent_obs_descs[i].data for i in range(len(agent_obs_descs))]
            agent_obs_descs[i]['prompts'] = agent_obs_descs[i]['prompts'].data

        # print(controls)

        try:
            step_info, next_agent_obs_descs, dict_actions, dict_info = self.env.step(controls, agent_infos, LM_times,
                                                                                     agent_obs,
                                                                                     agent_goal_specs, agent_obs_descs)
        except (
                Exception
        ) as e:
            e_node = trace.nodes.ExceptionNode(
                e,
                inputs={"actions": node(controls)},
                description="[exception] The operator step raises an exception.",
                name="exception_step",
            )
            raise trace.ExecutionError(e_node)

        self.obs = next_agent_obs_descs

        # have to add allow_external_dependencies, why metaworld is fine?
        @bundle(allow_external_dependencies=True)
        def step(action, agent_idx):
            """
            Take action in the environment and return the next observation
            """
            return next_agent_obs_descs[agent_idx]['prompts']

        next_obs = {}
        for i in range(len(next_agent_obs_descs)):
            next_obs[i] = next_agent_obs_descs[i]
            next_obs[i]['prompts'] = step(plans[i], i)

        return step_info, next_obs, dict_actions, dict_info


def record_info(agents, traj, log, step_info, next_agent_obs_descs, dict_actions, dict_info,
                agent_obs, reward, done, infos, messages, plans, agent_goal_specs):
    for i in range(len(agents)):

        traj[i]['observation'].append(next_agent_obs_descs[i])  # "prompts" node can be back-propped
        traj[i]['action'].append(dict_actions[i])
        traj[i]['reward'].append(reward)
        traj[i]['termination'].append(done)
        traj[i]['plans'].append(plans[i])
        traj[i]['parameters'].append(agents[i].plan.data)
        traj[i]['goal_specs'].append(copy.copy(agent_goal_specs[i]))
        traj[i]['info'].append(dict_info[i])

        unpacked_next_agent_obs_descs = {}
        for key in next_agent_obs_descs[i]:
            if key != 'prompts':
                unpacked_next_agent_obs_descs[key] = next_agent_obs_descs[i][key]
            else:
                unpacked_next_agent_obs_descs[key] = next_agent_obs_descs[i][key].data

        log[i]['observation'].append(unpacked_next_agent_obs_descs)
        log[i]['action'].append(dict_actions[i])
        log[i]['reward'].append(reward)
        log[i]['termination'].append(done)
        log[i]['plans'].append(plans[i].data)
        log[i]['parameters'].append(agents[i].plan.data)
        log[i]['goal_specs'].append(copy.copy(agent_goal_specs[i]))


def dynamic_rollout(env, agents, optimizers, horizon=10, task_id=8):
    LM_times = {0: 0, 1: 0}

    log_dict = dict(observation=[], plans=[], parameters=[], goal_specs=[],
                    action=[], reward=[], termination=[], truncation=[],
                    success=[], input=[], info=[])

    traj, log = {}, {}
    for i in range(len(agents)):
        traj[i] = copy.copy(log_dict)
        log[i] = copy.copy(log_dict)

    agent_obs, agent_obs_descs, agent_goal_specs, agent_goal_descs, agent_infos = env.reset(task_id=task_id)
    for i in range(len(agents)):
        traj[i]['observation'].append(agent_obs_descs[i])

    for h in range(horizon):
        plans = {}
        errors = {}
        for i in range(len(agents)):
            agent = agents[i]
            try:
                plans[i] = agent(agent_obs_descs[i]['prompts'])
            except trace.ExecutionError as e:
                errors[i] = e
                plans[i] = None
                break

        if len(errors) == 0:
            step_info, next_agent_obs_descs, dict_actions, dict_info = env.step(plans, agent_infos, LM_times, agent_obs,
                                                                                agent_goal_specs, agent_obs_descs)
            agent_obs, reward, done, infos, messages = step_info
            record_info(agents, traj, log, step_info, next_agent_obs_descs, dict_actions, dict_info,
                        agent_obs, reward, done, infos, messages, plans, agent_goal_specs)

            agent_obs_descs = next_agent_obs_descs
        else:
            break

        # optimize
        if len(optimizers) != 0:
            for i in range(len(agents)):
                optimizer = optimizers[i]
                target = traj[i]['observation'][-1]['prompts']
                optimizer.zero_feedback()
                feedback = f"Task Return: {sum(traj[i]['reward'])}"

                print(f"Step: {h}")
                print(f"Feedback: {feedback}")
                print(f"Parameter:\n {agents[i].plan.data}")

                optimizer.backward(target, feedback)
                optimizer.step(verbose=False)

                log[i]['optimizer_log'].append(optimizer.log)
        else:
            print(f"Step: {h}")
            feedback = f"Task Return: {sum(traj[0]['reward'])}"
            print(f"Feedback: {feedback}")

        # detach
        for i in range(len(agents)):
            traj[i]['observation'][-1]['prompts'] = node(traj[i]['observation'][-1]['prompts'].data)

        if done:
            print("Succeeded all tasks, environment terminated")
            break

    return traj, log
