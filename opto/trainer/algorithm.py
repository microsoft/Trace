from opto import trace
from opto.optimizers import OptoPrime
from opto.trainer.loader import DataLoader
import numpy as np
from opto.trainer.utils import async_run


# TODO clean up and refactor this file


class AbstractAlgorithm:  # TODO
    """ Abstract base class for all algorithms. """
    def __init__(self, *args, **kwargs):
        pass

    def train(self, *args, **kwargs):
        pass


@trace.bundle()
def concat_list_as_str(*items):
    """ Concatenate the items into a single string """
    output = ''
    for i, item in enumerate(items):
        output += f'ID {[i]}: {item}\n'
    return output


class BasicAlgorithm(AbstractAlgorithm):


    def __init__(
            self,
            agent,  # trace.model
            logger = None,  # a logger that provides `log(name, data, step, **kwargs)`` method to log the training process
            *args,
            **kwargs,
            ):

        self.agent = agent
        self.logger = logger

    @staticmethod
    def evaluate(agent, teacher, inputs, infos, min_score=0):
        """ Evaluate the agent on the inputs and return the scores """
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


    # TODO write it as a class?
    def train(self,
              teacher, # teacher to provide feedback teacher(x, student_answer, info) -> score, feedback
              train_dataset,  # dataset of (x, info) pairs
              *,
              num_epochs = 1,  # number of training epochs
              logger = None,  # a logger that provides `log(name, data, step, **kwargs)`` method to log the training process
              batch_size = 1,  # batch size for updating the agent
              test_dataset = None, # dataset of (x, info) pairs to evaluate the agent
              eval_frequency = 1, # frequency of evaluation
              log_frequency = 1,  # frequency of logging
              update_score_threshold = 1,  # only update the agent if the score is below this threshold
              stop_score_threshold = float("inf"),  # stop training if the score is above this threshold
              min_score = 0,  # minimum score to update the agent
              verbose = False,  # whether to print the output of the agent
              ):
        # TODO aysnc forward

        agent = self.agent
        logger = self.logger
        loader = DataLoader(train_dataset)

        n_updates = 0  # number of updates
        n_iters = 0 # number of iterations (Note: n_updates <= n_iters)
        last_test_n = None

        train_scores = []
        for i in range(num_epochs):

            # Train agent
            targets, feedbacks, scores = [], [], []
            for x, info in loader:
                # Forward and compute feedback
                try:
                    target = agent(x)
                    score, feedback = teacher(x, target.data, info)
                except trace.ExecutionError as e:
                    target = e.exception_node
                    score, feedback = min_score, target.create_feedback('full')

                train_scores.append(score)

                # minibatch
                scores.append(score)
                targets.append(target)
                feedbacks.append(feedback)

                # Update the agent when the batch is full
                update_agent = False
                if len(targets)>=batch_size:
                    if np.mean(scores) < update_score_threshold:
                        update_agent = True
                    else:  # reset the batch and build a new batch
                        targets, feedbacks, scores = [], [], []

                if update_agent:
                    # Evaluate the agent before learning
                    if n_updates == 0:
                        test_scores = self.evaluate(agent, teacher, test_dataset['inputs'], test_dataset['infos'], min_score=min_score)
                        logger.log('Average test score', np.mean(test_scores), n_iters, 'green')

                    # TODO Different ways to concat and do minibatching
                    # Concatenate the targets and feedbacks into a single string
                    target = concat_list_as_str(*targets)
                    feedback = concat_list_as_str(*feedbacks).data  # str

                    # Update the agent
                    self.update(target, feedback, verbose=verbose)
                    n_updates += 1
                    targets, feedbacks, scores = [], [], []
                    # Evaluate the agent after update
                    if test_dataset is not None and n_updates % eval_frequency == 0:
                        test_scores = self.evaluate(agent, teacher, test_dataset['inputs'], test_dataset['infos'])
                        logger.log('Average test score', np.mean(test_scores), n_iters, 'green')

                # Logging
                if n_iters % log_frequency == 0:
                    print(f"Epoch: {i}. Iteration: {n_iters}")
                    logger.log("Average train score", np.mean(train_scores), n_iters)
                    if update_agent:
                        print(f"Number of updates: {n_updates}")
                        for p in agent.parameters():
                            logger.log(f"Parameter: {p.name}", p.data, n_iters, 'red')

                    if score > stop_score_threshold:
                        print(f"Stopping training at iteration {n_iters} with mean score {np.mean(scores)}")
                        return

                n_iters += 1

    def update(self, *args, **kwargs):
        """ Subclasses should implement this method to update the agent. """
        raise NotImplementedError



class DirectUpdate(BasicAlgorithm):
    """ Directly update the agent using the optimizer. """

    def __init__(
            self,
            agent,  # trace.model
            optimizer,
            logger = None,  # a logger that provides `log(name, data, step, **kwargs)`` method to log the training process
            ):
        super().__init__(agent, logger)
        self.optimizer = optimizer

    def update(self, target, feedback, verbose=False):
        self.optimizer.zero_feedback()
        self.optimizer.backward(target, feedback)
        self.optimizer.step(verbose=verbose)