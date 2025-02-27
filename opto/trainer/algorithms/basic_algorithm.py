import numpy as np
import copy
from opto import trace
from opto.trainer.algorithms.algorithm import BaseAlgorithm
from opto.trainer.loader import DataLoader


@trace.bundle()
def concat_list_as_str(*items):
    """ Concatenate the items into a single string """
    output = ''
    for i, item in enumerate(items):
        output += f'ID {[i]}: {item}\n'
    return output


class MinibatchUpdate(BaseAlgorithm):
    """ Minibatched optimization algorithm.

        The computed output of each instance in the minibatch is aggregated and a batched feedback is provided to update the agent.
    """

    def __init__(self,
                 agent,
                 optimizer,
                 logger=None,
                 *args,
                 **kwargs,
                 ):
        super().__init__(agent)
        self.optimizer = optimizer
        # The logger needs to provide `log(name, data, step, **kwargs)`` method to log the training process.
        self.logger = logger
        self.n_iters = 0  # number of iterations

    def evaluate(self, agent, guide, xs, infos, min_score=None):
        """ Evaluate the agent on the given dataset. """
        test_scores = super().evaluate(agent, guide, xs, infos, min_score=min_score)
        test_scores = [s for s in test_scores if s is not None]
        if all([s is not None for s in test_scores]):
            self.logger.log('Average test score', np.mean(test_scores), self.n_iters, color='green')
        return test_scores

    def train(self,
              guide,
              train_dataset,
              *,
              num_epochs=1,  # number of training epochs
              batch_size=1,  # batch size for updating the agent
              test_dataset=None,  # dataset of (x, info) pairs to evaluate the agent
              eval_frequency=1,  # frequency of evaluation
              log_frequency=None,  # frequency of logging
              min_score=None,  # minimum score to update the agent
              verbose=False,  # whether to print the output of the agent
              ):
        """
                Given a dataset of (x, info) pairs, the algorithm will:
                1. Forward the agent on the inputs and compute the feedback using the teacher.
                2. Update the agent using the feedback.
                4. Evaluate the agent on the test dataset and log the results.
                5. Stop training if the score is above the threshold.
        """

        log_frequency = log_frequency or eval_frequency  # frequency of logging (default to eval_frequency)

        # Evaluate the agent before learning
        if eval_frequency > 0:
            self.evaluate(self.agent, guide, test_dataset['inputs'], test_dataset['infos'],
                          min_score=min_score)  # and log

        loader = DataLoader(train_dataset, batch_size=batch_size)
        train_scores = []
        for i in range(num_epochs):

            # Train agent
            for xs, infos in loader:

                # Forward and compute feedback for each instance in the minibatch
                targets, feedbacks, scores = [], [], []
                for x, info in zip(xs, infos):  # # TODO async forward
                    target, score, feedback = self.step(self.agent, x, guide, info)
                    scores.append(score)
                    targets.append(target)
                    feedbacks.append(feedback)
                    train_scores.append(score)  # persist across iterations for logging

                # Concatenate the targets and feedbacks into a single string
                target = concat_list_as_str(*targets)
                feedback = concat_list_as_str(*feedbacks).data  # str

                # Update the agent
                self.update(target, feedback, verbose=verbose)
                self.n_iters += 1

                # Evaluate the agent after update
                if test_dataset is not None and self.n_iters % eval_frequency == 0:
                    self.evaluate(self.agent, guide, test_dataset['inputs'], test_dataset['infos'],
                                  min_score=min_score)  # and log

                # Logging
                if self.n_iters % log_frequency == 0:
                    print(f"Epoch: {i}. Iteration: {self.n_iters}")
                    self.logger.log("Average train score", np.mean(train_scores), self.n_iters)
                    for p in self.agent.parameters():
                        self.logger.log(f"Parameter: {p.name}", p.data, self.n_iters, color='red')

    def update(self, target, feedback, verbose=False):
        """ Subclasses can implement this method to update the agent. """
        self.optimizer.zero_feedback()
        self.optimizer.backward(target, feedback)
        self.optimizer.step(verbose=verbose)


class BasicSearch(MinibatchUpdate):
    """ A basic search algorithm that calls the optimizer multiple times to get candidates and selects the best one based on validation set. """

    def train(self,
              teacher, # teacher to provide feedback
              train_dataset,  # dataset of (x, info) pairs to train the agent
              *,
              validate_dataset = None, # dataset of (x, info) pairs to evaluate the agent for candidate selection
              validate_teacher = None,  #  to provide scores for the validation set
              num_proposals = 4,  # number of proposals to get from the optimizer
              num_epochs = 1,  # number of training epochs
              batch_size = 1,  # batch size for updating the agent
              test_dataset = None, # dataset of (x, info) pairs to evaluate the agent
              eval_frequency = 1, # frequency of evaluation
              log_frequency = None,  # frequency of logging
              min_score = None,  # minimum score to update the agent
              verbose = False,  # whether to print the output of the agent
              ):

        self.num_proposals = num_proposals
        self.validate_dataset = validate_dataset or train_dataset  # default to train_dataset
        self.validate_teacher = validate_teacher or teacher
        self.min_score = min_score
        self.current_score = None

        return super().train(teacher, train_dataset, num_epochs=num_epochs, batch_size=batch_size,
                      test_dataset=test_dataset, eval_frequency=eval_frequency, log_frequency=log_frequency,
                      min_score=min_score, verbose=verbose)

    def validate(self):
        """ Validate the agent on the validation dataset. """
        scores = BaseAlgorithm.evaluate(
                    self.agent,
                    self.validate_teacher,
                    self.validate_dataset['inputs'],
                    self.validate_dataset['infos'],
                    min_score=self.min_score)
        if all([s is not None for s in scores]):
            score = np.mean(scores)
        else:
            score = - np.inf
        return score

    def update(self, target, feedback, verbose=False):
        """ Subclasses can implement this method to update the agent. """
        self.optimizer.zero_feedback()
        self.optimizer.backward(target, feedback)

        # Ask the optimizer multiple times to propose updates
        # TODO perhaps we can ask for multiple updates in one query or use different temperatures in diffeernt queries
        candidates = []
        for _ in range(self.num_proposals):  # TODO async
            backup_dict = {p: copy.deepcopy(p.data) for p in self.agent.parameters()}  # backup the current value
            update_dict = self.optimizer.step(verbose=verbose)
            score = self.validate()  # check the score on the validation set
            candidates.append((score, update_dict))
            self.optimizer.update(backup_dict)  # restore the backup

        # Include the current parameter as a candidate
        if self.current_score is None:
            self.current_score = self.validate()
        candidates.append((self.current_score, backup_dict))

        # Find the candidate with the best score
        best_score, best_update = max(candidates, key=lambda x: x[0])
        self.current_score = best_score

        if verbose:
            print(f"Best score: {best_score} out of scores {[c[0] for c in candidates]}")
            print(f"Selected Update:\n{best_update}")

        # Make the best update
        self.optimizer.update(best_update)
