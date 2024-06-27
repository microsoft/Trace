import llfbench
import opto.trace as trace
from opto.trace.optimizers import FunctionOptimizer
from llfbench.agents.utils import set_seed
from collections import defaultdict
import copy
import pickle

# Config
horizon = 20
seed = 0
env_name = "llf-metaworld-pick-place-v2"

set_seed(seed)
env = llfbench.make(env_name)
env.seed(seed)


@trace.bundle()
def reset(n_outputs=2):
    """
    Reset the environment and return the initial observation and info.
    """
    return env.reset()  # obs, info


@trace.bundle(n_outputs=5)
def step(action):
    """
    Take action in the environment and return the next observation, reward, done, and info.
    """
    return env.step(action)  # next_obs, reward, termination, truncation, info


def user_feedback(obs, action, next_obs):
    """
    Provide feedback to the user.
    """
    return f"Taking action {action.data} at observation {obs['observation'].data} resulted in next observation {next_obs['observation'].data}. Recieved feedback {next_obs['feedback'].data}."


# ### Optimization for single step
# def single_step():
#     optimizer = trace.optimizers.FunctionOptimizer(controller.parameters())

#     obs, info = reset()
#     optimizer.objective = f"{optimizer.default_objective} Hint: {obs['instruction']}"

#     sum_of_rewards = 0
#     for _ in range(horizon):
#         try:
#             action = controller(
#                 obs["observation"].detach()
#             )  # Need a new node; otherwise, it would be back-propagated across time.
#             next_obs, reward, termination, truncation, info = step(action)
#             feedback = user_feedback(obs, action, next_obs)  # not traced
#             obs = next_obs
#             target = obs["observation"]
#         except trace.TraceExecutionError as e:
#             feedback = str(e)
#             target = e.exception_node

#         # Optimization step
#         optimizer.zero_feedback()
#         optimizer.backward(target, feedback)  # obs = next obs
#         optimizer.step(verbose=True)

#         sum_of_rewards = reward + sum_of_rewards
#         if termination or truncation:
#             break

#     return optimizer, sum_of_rewards


def rollout(obs, horizon, controller):
    # Reset the env outside
    # Rollout for horizon steps

    buffer = defaultdict(list)
    for _ in range(horizon):
        action = controller(obs["observation"])
        next_obs, reward, termination, truncation, info = step(action)
        feedback = user_feedback(obs, action, next_obs)  # not traced
        obs = next_obs
        buffer["observation"].append(obs)
        buffer["action"].append(action)
        buffer["reward"].append(reward)
        buffer["termination"].append(termination)
        buffer["truncation"].append(truncation)
        buffer["info"].append(info)
        buffer["feedback"].append(feedback)
        done = termination or truncation
        if done:
            break
    return buffer, done


### Optimization for multi step
def multi_step(controller, n_iterations=50, rollout_horizon=3, horizon=30):
    optimizer = trace.optimizers.FunctionOptimizer(controller.parameters())
    checkpoints = defaultdict(list)
    data = list()
    traj = defaultdict(list)
    done = True
    for i in range(n_iterations):  # iterations
        error = None
        try:  # Trace the rollout; detach init_obs to avoid back-propagating across time.
            if (len(traj["action"]) % horizon == 0) or done:
                traj = defaultdict(list)
                data.append(traj)
                init_obs, info = reset()
                # not traced
                instruction = init_obs["instruction"].data
                hint = (
                    instruction
                    + "The controller should be a function that depends on the observation, not just outputing a constant action."
                )
                optimizer.objective = f"{optimizer.default_objective} Hint: {hint}"
            buffer, done = rollout(init_obs.detach(), rollout_horizon, controller)

        except trace.TraceExecutionError as e:
            error = e

        if error is None:
            feedback = "\n".join(buffer["feedback"])
            target = buffer["observation"][-1]["observation"]  # last observation
        else:
            feedback = str(error)
            target = error.exception_node

        # Optimization
        optimizer.zero_feedback()
        optimizer.backward(target, feedback)  # obs = next obs
        optimizer.step(verbose=True)

        # Log
        if error is None:
            for key in buffer:  # Update log data
                traj[key].extend([d.data if isinstance(d, trace.Node) else d for d in buffer[key]])

            print(f"Sum of rewards so far: {sum([r for r in traj['reward']])}")
        print("Parameters:")
        for p in optimizer.parameters:
            print(p.data)

        checkpoints["variables"].append(copy.deepcopy(controller))

    return optimizer, checkpoints, data


# Need ablation of not tracing step and reset
# Need ablation of ignoring some info in propagated feedback
# Need to test backward across time.


@trace.bundle(trainable=True)
def controller(obs):
    """
    The controller takes in an observation and returns an action.
    """
    return env.action_space.sample()


optimizer, checkpoints, data = multi_step(controller, n_iterations=50, rollout_horizon=3, horizon=30)
results = {"checkpoints": checkpoints, "data": data}

for traj in data:
    print(f"Sum of rewards: {sum(traj['reward'])}")


with open("results.pkl", "wb") as f:
    pickle.dump(data, f)
