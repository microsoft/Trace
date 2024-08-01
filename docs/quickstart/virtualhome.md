# 🤯 Finally: Emergent Behaviors

In the previous two sections, we showed how to decorate Python functions for Trace to optimize and how to create an RL agent using Trace.
Now, we will demonstrate how Trace can be used to create interactive agents that learn emergent behaviors in a multi-agent environment.

```python
import opto.trace as trace
from opto.trace import node, bundle, model, GRAPH
from opto.optimizers import OptoPrime
```

## 🏠 VirtualHome

[VirtualHome](http://virtual-home.org/) is a Unity engine based simulation environment that creates a home-like environment where multiple agents need to collaboratively solve a
series of tasks, ranging from book reading, putting empty plates in a dishwasher, to preparing food.

```{image} ../images/virtualhome/virtualhome_image.png
:alt: virtual-home
:align: center
```
(Image credit: [Virtual Home Project Page](http://virtual-home.org/))

LLM agents have been observed to have "natural" organizational behavior in LLM-based agents when they were asked to have a few rounds of discussion, before carrying out the tasks in the environment ([Prior work](https://organized-llm-agents.netlify.app/)).
However, it's hard to determine whether the behavior of LLM agents is a result of emergence or if it's due to inherent biases towards hierarchical organizational
behaviors because they are trained on human data.

In this section, we show that how to create multiple agents using Trace, and through optimization, we can observe emergent behaviors in these agents.
We first construct an agent.

```{tip}
We can define a class that inherits from multiple other classes and still use `@model` to decorate it and capture its behavior.
```

The observation of the agent and the action they can take in virtual home can be expressed in text. We follow the convention from [Guo et al. (2024)](https://arxiv.org/abs/2403.12482)
with minor modifications and here is an example:

```text
I'm Agent_2. I'm in a hurry to finish the housework with my friends Agent_1 together.
Given our shared goal, dialogue history, and my progress and previous actions,
please help me choose the best available action to achieve the goal as soon as possible.
Note that I can hold two objects at a time and there are no costs for holding objects.
All objects are denoted as <name> (id), such as <table> (712). Be aware that exploring
or checking the items in another room may cost some time to walk there.

Goal: Find and put 1 apple, 1 wine, 1 pudding onto the <coffeetable> (268).

Progress: This is step 0. I'm holding nothing. I'm in the bedroom, where I found an unchecked container <cabinet> (216). I don't know where Agent_1 is. The livingroom is unexplored. The kitchen is unexplored. The bathroom is unexplored.

Dialogue history:

Previous actions: [goexplore] <bedroom> (210)
Available actions:
A. [goexplore] <livingroom> (267)
B. [goexplore] <kitchen> (11)
C. [goexplore] <bathroom> (172)
D. [gocheck] <cabinet> (216)

Response format:
{"thoughts" : "thoughts content",
"action" : "choose one action from the available actions above"}

Note: You must respond in the json format above. The action choice must be the same as one of the available actions.
If there's nothing left to do, the action can be "None". If you choose [send_message], you must also generate the actual message.
```

## Agent Architecture

For the Trace optimized agent, we additionally add `Plan:$PLAN` right below `Goals`. The agent stores a plan in its python class object (which serves as its **memory**),
and when it needs to produce an action, it will replace `$PLAN$` with the current plan.
Trace optimizer will update the **plan** based on the feedback from the environment and the current progress.

```python
import json
import random
from examples.virtualhome import LLMCallable, BaseUtil

@model
class Agent(LLMCallable, BaseUtil):
    def __init__(self, verbose=False):
        super().__init__(verbose=verbose)
        self.plan = node("", trainable=True,
                         description="This represents the current plan of the agent.")

    def __call__(self, obs):
        obs = obs.replace("$PLAN$", self.plan)
        action = self.act(obs)
        return action

    @bundle()
    def act(self, obs):
        """
        Call the LLM to produce the next action for the agent
        """
        response = self.call_llm(obs)
        available_actions = self.extract_actions(obs)
        plan = json.loads(response)
        if 'action' in plan:
            action = plan['action']
        else:
            action = ""

        if '[send_message]' not in action:
            action = self.unify_and_match_action(action, available_actions)

            # if the matched failed, we randomly choose an action.
            if action not in available_actions.values():
                action = random.choice(list(available_actions.values()))

        return action
```

## Multi-Agent Synchronous Optimization

In a multi-agent environment, we can create multiple agents and let them interact with each other.
We take a synchronous approach, where all agents take actions after observing the current state of the environment, and their
actions are executed together. To make the simulation faster, we implement a sticky-action mechanism, where if the environment
observation is the same as the previous observation, we repeat the previous action without making another LLM call.

```{note}
The full virtualhome environment requires Unity engine executable and is not included in the Trace package.
This code is for demo purposes only.
```

We first create two agents and their corresponding optimizers.
```python
agent1 = Agent()
agent2 = Agent()

optimizer1 = OptoPrime([agent1.plan])
optimizer2 = OptoPrime([agent2.plan])

agents = [agent1, agent2]
```

We then run the simulation for a fixed number of steps. In each step, we observe the environment, and each agent produces an action based on its observation.

```python
from examples.virtualhome import VirtualHomeEnv

horizon = 50

env = VirtualHomeEnv()

# we specify a task in this environment
agent_obs, agent_obs_descs, agent_goal_specs, agent_goal_descs, agent_infos = env.reset(task_id=8)

for h in range(horizon):
    plans, errors = {}, {}
    for i in range(len(agents)):
        agent = agents[i]
        try:
            plans[i] = agent(agent_obs_descs[i])
        except trace.ExecutionError as e:
            errors[i] = e
            plans[i] = None
            break

    if len(errors) == 0:
        step_info, next_agent_obs_descs, dict_actions, dict_info = env.step(plans)
        _, reward, done, infos, messages = step_info

    for i in range(len(agents)):
        optimizer = optimizers[i]
        optimizer.zero_feedback()
        feedback = f"Task Return: {sum(reward[i]['reward'])}"

        print(f"Step: {h}")
        print(f"Feedback: {feedback}")

        optimizer.backward(next_agent_obs_descs[i], feedback)
        optimizer.step(verbose=False)

        # now we detach the graph for the next step
        agent_obs_descs[i] = next_agent_obs_descs[i].detach()
```

```{note}
Here we see an interesting case of optimization. In this environment, the observation an agent sees is the result of the agent's previous action.
Therefore, we can directly call `backward` on the next observation.
```

```{tip}
To learn more about how to use Trace to create an agent in an interactive environment, check out the [Meta-World](https://microsoft.github.io/Trace/examples/robotics/metaworld.html) example.
```

## Results

We compare with the baseline ReAct agents that only outputs `thoughts` before taking an action.
This table shows that when Trace optimizes and updates the plan of the agents, they can learn to coordinate with each other and achieve the shared goal more efficiently.

```{warning}
This figure is not to show that other style of agent architecture cannot achieve similar results.
We are using this example to demonstrate how easy it is to specify an RL agent using Trace and how Trace can optimize individual agents in a multi-agent environment.
```

```{image} ../images/virtualhome/virtualhomes.png
---
alt: task-reward
align: center
---
```
```{div} align-center
(**Figure**: *Lower number indicates faster task completion. We do not count sending a message as an action -- although if an action sends a message, it cannot perform another action in the same round.
The number of action describes the total number of actions from both agents.*)
```

## Emergent Pro-Social Behaviors

We also found out that Trace-optimized agents develop pro-social behaviors, under the optimization procedure.
The agents will learn to coordinate with each other to achieve the shared goal, but will choose not to communicate when they need to be more efficient.
Although there are many caveats to this toy experiment, emergence of behaviors through optimization can be achieved via Trace.

````{dropdown} Click to reveal some optimized plans and actions
```{card}
**Agent 2, Step 3**
^^^
{bdg-primary}`Plan` As I'm currently in the kitchen and have access to several unexplored kitchen cabinets, my strategy should be to first check the nearest kitchen cabinet (75) and proceed sequentially to optimize task completion time and reduce unnecessary movement.
+++
{bdg-primary}`Action` Executing script: `<character2> [walktowards] <kitchencabinet> (77)`
```

```{card}
**Agent 2, Step 7**
^^^
{bdg-primary}`Plan` Since I'm in the kitchen with necessary items around and unchecked kitchen containers like <kitchencabinet> (79) and <kitchencabinet> (80) available, I should check these first and involve discussions with Agent_1 to decide if we should either explore further or require assistance in any tasks.
+++
{bdg-primary}`Action` Executing script: `<character2> [send_message] <Agent_1> (1): Let's divide our search. Can you explore the bathroom while I check the fridge here in the kitchen?`
```

After a few more steps of searching and finding the necessary items, Agent 1 came up with a different plan.
Note that unfortunately Agent 1 doesn't realize its own "plan" cannot be read/accessed by Agent 2.

```{card}
**Agent 1, Step 10**
^^^
{bdg-primary}`Plan` Since we're both capable of handling two items and are already in the kitchen, let's bypass extended communication and each take direct actions towards goal completion. Please `[gocheck] <microwave> (109)` for any plates, while I handle the `[<stove> (105)]`. This coordinated effort should swiftly meet our objective.
+++
{bdg-primary}`Action` Executing script: `<character1> [walktowards] <stove> (105)`
```

After finding all the items in the kitchen, some objects are still missing. Now the plan is to conduct a larger search.

```{card}
**Agent 2, Step 17**
^^^
{bdg-primary}`Plan` Given the current situation to find 1 cutleryfork and 2 plates, continue searching in the living room as it is still unexplored and this area might provide necessary items. With careful navigation and effective search, locate containers that might hide these kitchen items. If the living room doesn't yield results, transition to the bedroom without further delays to continue the search.
+++
{bdg-primary}`Action` Executing script: `<character2> [walktowards] <livingroom> (267)`
```
````

We show that this pro-social behavior does not happen across all tasks. For example, in two other tasks -- `read book` and `prepare food` -- the agents do not communicate with each other at all.
This can be attributed to many reasons, but we will stop our investigation here.
When we optimize our agents through Trace, the emergent behaviors will change according to different tasks. This is very different from explicitly requiring the agent to communicate with each other.

```{image} ../images/virtualhome/virtualhomes_messages.png
---
alt: messages
align: center
---
```

## Recording of Agent Behavior

We show three videos of how Trace-optimized agents accomplished Task 2 (Put Dishwasher). We present the top-down birdseye view, and what each agent sees in their own perspective.

``````{grid}
:gutter: 0
````{grid-item}
```{figure} ../images/virtualhome/task2.gif
```
````
````{grid-item}
```{figure} ../images/virtualhome/agent1_task2.gif
```
````
````{grid-item}
```{figure} ../images/virtualhome/agent2_task2.gif
```
````
``````

## What's Next?

In this tutorial, we showed how to create two agents and have them interact with each other in a multi-agent environment.
If you are interested in knowing how to use Trace for your own projects, continue learning the basics of Trace.

```{note}
To learn more about how to trace through agent-environment interactions, check out the [Meta-World](https://microsoft.github.io/Trace/examples/robotics/metaworld.html) example.
```

```{note}
To see another example of multi-agent interaction in a different environment, check out the [Negotiation Arena](https://microsoft.github.io/Trace/examples/game/negotiation_arena.html) example.
```
