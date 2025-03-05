import warnings
from opto import trace
from opto.trace.modules import Module
from opto.trainer.utils import async_run


class AbstractAlgorithm:
    """ Abstract base class for all algorithms. """

    def __init__(self, agent, *args, **kwargs):
        self.agent = agent

    def train(self, *args, **kwargs):
        """ Train the agent. """
        pass


class BaseAlgorithm(AbstractAlgorithm):
    """
        We define the API of algorithms to train an agent from a dataset of (x, info) pairs.

        agent: trace.Module (e.g. constructed by @trace.model)
        teacher: (question, student_answer, info) -> score, feedback (e.g. info can contain the true answer)
        train_dataset: dataset of (x, info) pairs
    """

    def __init__(self,
                 agent,  # trace.model
                 *args,
                 **kwargs):
        assert isinstance(agent, Module), "Agent must be a trace Module. Getting {}".format(type(agent))
        super().__init__(agent, *args, **kwargs)

    def train(self,
              guide,
              train_dataset,  # dataset of (x, info) pairs
              **kwargs
              ):
        raise NotImplementedError
