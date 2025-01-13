from opto.optimizers import OptoPrime


class AbstractAlgorithm:  # TODO
    """ Abstract base class for all algorithms. """
    def __init__(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class DirectUpdate(AbstractAlgorithm):
    """ Directly update the agent using the optimizer. """

    def __init__(self, optimizer):
        self.optimizer = optimizer

    def update(self, target, feedback, verbose=False):
        self.optimizer.zero_feedback()
        self.optimizer.backward(target, feedback)
        self.optimizer.step(verbose=verbose)