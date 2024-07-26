# 🤯 Finally: Emergent Behaviors

In the previous two sections, we showed how to decorate Python functions for Trace to optimize and how to create an RL agent using Trace. 
Now, we will demonstrate how Trace can be used to create interactive agents that learn emergent behaviors in a multi-agent environment.

```python
import opto.trace as trace
from opto.trace import node, bundle, model, GRAPH
from opto.optimizers import OptoPrime
```

## 🏠 VirtualHome

VirtualHome is a Unity engine based simulation environment that creates a home-like enviornment where multiple agents need to collaboratively solve a 
series of tasks, ranging from book reading, putting empty plates in a dishwasher, to preparing food.
[Prior work](https://organized-llm-agents.netlify.app/) observed "naturally" occurring organizational behavior in LLM-based agents when they were asked to have a few rounds of discussion, before carrying out the tasks in the environment.
It's hard to determine whether the behavior of LLM agents is a result of emergence or if it's due to inherent biases towards hierarchical organizational
behaviors because they are trained on human data.

```{image} ../images/virtualhome_image.png
:alt: fishy
:align: center
```
(Image credit: [Virtual Home Project Page](http://virtual-home.org/))

```python
import json
import random
from examples.virtualhome import LLMCallable, BaseUtil

@model
class TraceAgent(LLMCallable, BaseUtil):
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