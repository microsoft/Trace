# 🤯 Finally: Emergent Behaviors

In the previous two sections, we showed how to decorate Python functions for Trace to optimize and how to create an RL agent using Trace. 
Now, we will demonstrate how Trace can be used to create interactive agents that learn emergent behaviors in a multi-agent environment.

```python
import opto.trace as trace
from opto.trace import node, bundle, model, GRAPH
from opto.optimizers import OptoPrime
```

## 🏠 VirtualHome

