import warnings
from opto import trace
from opto.trace.modules import Module
from opto.trainer.utils import async_run
import os


class AbstractAlgorithm:
    """ Abstract base class for all algorithms. """

    def __init__(self, agent, *args, **kwargs):
        self.agent = agent

    def train(self, *args, **kwargs):
        """ Train the agent. """
        pass


class AlgorithmBase(AbstractAlgorithm):
    """
        We define the API of algorithms to train an agent from a dataset of (x, info) pairs.

        agent: trace.Module (e.g. constructed by @trace.model)
        teacher: (question, student_answer, info) -> score, feedback (e.g. info can contain the true answer)
        train_dataset: dataset of (x, info) pairs
    """

    def __init__(self,
                 agent,  # trace.model
                 num_threads: int = None,   # maximum number of threads to use for parallel execution
                 *args,
                 **kwargs):
        assert isinstance(agent, Module), "Agent must be a trace Module. Getting {}".format(type(agent))
        super().__init__(agent, *args, **kwargs)
        self.num_threads = num_threads

    def _use_asyncio(self, threads=None):
        """Determine whether to use asyncio based on the number of threads.
        
        Args:
            threads: Number of threads to use. If None, uses self.num_threads.
            
        Returns:
            bool: True if parallel execution should be used, False otherwise.
        """
        effective_threads = threads or self.num_threads
        return effective_threads is not None and effective_threads > 1

    def save_agent(self, save_path, iteration=None):
        """Save the agent to the specified path.
        
        Args:
            save_path: Path to save the agent to.
            iteration: Current iteration number (for logging purposes).
            
        Returns:
            str: The path where the agent was saved.
        """
        # Create directory if it doesn't exist
        directory = os.path.dirname(save_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        # Save the agent
        self.agent.save(save_path)
        
        # Log if we have a logger and iteration is provided
        if hasattr(self, 'logger') and iteration is not None:
            self.logger.log('Saved agent', save_path, iteration, color='blue')
            
        return save_path

    def train(self,
              guide,
              train_dataset,  # dataset of (x, info) pairs
              num_threads: int = None,  # maximum number of threads to use (overrides self.num_threads)
              **kwargs
              ):
        raise NotImplementedError
