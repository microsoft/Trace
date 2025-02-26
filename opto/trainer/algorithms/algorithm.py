from opto import trace
from opto.trace.modules import Module
from opto.trainer.utils import async_run
from opto.trainer.guide import SimpleReferenceGuide

class AbstractAlgorithm:
    """ Abstract base class for all algorithms. """
    def __init__(self, *args, **kwargs):
        pass

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
        self.agent = agent

    @staticmethod
    def evaluate(agent, teacher, inputs, infos, min_score=None):
        """ Asynchronously evaluate the agent on the inputs and return the scores """
        def evaluate_single(i):
            try:
                output = agent(inputs[i])
                score, _ = teacher(inputs[i], output, infos[i])
            except:
                score = min_score
            return score

        N = len(inputs)
        assert len(inputs) == len(infos), "Inputs and infos must have the same length"
        scores = async_run([evaluate_single]*N, [(i,) for i in range(N)]) # list of tuples
        return scores

    @staticmethod
    def step(agent, x, teacher, info, min_score=0):
        """ Forward and compute feedback.

            Args:
                agent: trace.Module
                x: input
                teacher: (question, student_answer, info) -> score, feedback
                info: additional information for the teacher
                min_score: minimum score when exception happens

            Returns:
                target: output of the agent
                score: score from the teacher
                feedback: feedback from the teacher
         """
        try:
            target = agent(x)
            score, feedback = teacher(x, target.data, info)
        except trace.ExecutionError as e:
            target = e.exception_node
            score, feedback = min_score, target.create_feedback('full')
        return target, score, feedback


    def train(self,
              teacher,
              train_dataset,  # dataset of (x, info) pairs
              ):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        """ Subclasses should implement this method to update the agent. """
        raise NotImplementedError

def exact_match_metric(question, student_answer, info):
    """ Exact match metric """
    return float(student_answer == info)

class BaseAlgorithmV2(AbstractAlgorithm):
    """
    Very similar to above, except it separates teacher into two parts:
    1. metric (for score)
    2. guide (for feedback)
    """

    def __init__(self,
                 agent,
                 *args,
                 **kwargs):
        super().__init__(agent, *args, **kwargs)

    @staticmethod
    def evaluate(agent, metric, inputs, infos, min_score=None):
        """ Asynchronously evaluate the agent on the inputs and return the scores """
        def evaluate_single(i):
            try:
                output = agent(inputs[i])
                score = metric(inputs[i], output, infos[i])
            except:
                score = min_score
            return score

        N = len(inputs)
        assert len(inputs) == len(infos), "Inputs and infos must have the same length"
        scores = async_run([evaluate_single]*N, [(i,) for i in range(N)]) # list of tuples
        return scores

    @staticmethod
    def step(agent, x, info, metric, guide, min_score=0):
        """ Forward and compute feedback.

            Args:
                agent: trace.Module
                x: input (question/query/state/task)
                metric: (question, student_answer, info) -> score
                guide: (question, student_answer, info) -> feedback
                info: additional information for the teacher
                min_score: minimum score when exception happens

            Returns:
                target: output of the agent
                score: score from the teacher
                feedback: feedback from the teacher
         """
        try:
            target = agent(x)
            score = metric(x, target.data, info)
            feedback = guide(x, target.data, info)
        except trace.ExecutionError as e:
            target = e.exception_node
            score, feedback = min_score, target.create_feedback('full')
        return target, score, feedback


    def train(self,
              train_dataset,  # dataset of (x, info) pairs
              guide=SimpleReferenceGuide(),
              metric=exact_match_metric
              ):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        """ Subclasses should implement this method to update the agent. """
        raise NotImplementedError
    
class BaseRLAlgorithm(AbstractAlgorithm):
    raise NotImplementedError
