import numpy as np
import copy
from typing import Union
from opto import trace
from opto.trainer.algorithms.algorithm import AlgorithmBase
from opto.trainer.loader import DataLoader
from opto.trainer.utils import async_run
from opto.optimizers.utils import print_color


def evaluate(agent, guide, inputs, infos, min_score=None, num_threads=None, description=None):
    """ Evaluate the agent on the inputs and return the scores

    Args:
        agent: The agent to evaluate
        guide: The guide to use for evaluation
        inputs: List of inputs to evaluate on
        infos: List of additional information for each input
        min_score: Minimum score to return when an exception occurs
        num_threads: Maximum number of threads to use for parallel evaluation
        description: Description to display in the progress bar
    """

    def evaluate_single(i):
        try:
            output = agent(inputs[i]).data
            score = guide.metric(inputs[i], output, infos[i])
        except:
            score = min_score
        return score

    N = len(inputs)
    assert len(inputs) == len(infos), "Inputs and infos must have the same length"
    # Use asyncio if num_threads is not None and > 1
    use_asyncio = num_threads is not None and num_threads > 1
    if use_asyncio:
        # Use provided description or generate a default one
        eval_description = description or f"Evaluating {N} examples"
        scores = async_run([evaluate_single] * N, [(i,) for i in range(N)],
                          max_workers=num_threads,
                          description=eval_description) # list of tuples
    else:
        scores = [evaluate_single(i) for i in range(N)]
    return scores

def standard_optimization_step(agent, x, guide, info, min_score=0):
    """ Forward and compute feedback.

        Args:
            agent: trace.Module
            x: input
            guide: (question, student_answer, info) -> score, feedback
            info: additional information for the guide
            min_score: minimum score when exception happens

        Returns:
            target: output of the agent
            score: score from the guide
            feedback: feedback from the guide
        """
    try:
        target = agent(x)
        score, feedback = guide(x, target.data, info)
    except trace.ExecutionError as e:
        target = e.exception_node
        score, feedback = min_score, target.create_feedback('full')
    return target, score, feedback


class Minibatch(AlgorithmBase):
    """ General minibatch optimization algorithm. This class defines a general training and logging routine using minimbatch sampling."""

    def __init__(self,
                 agent,
                 optimizer,
                 num_threads: int = None,   # maximum number of threads to use for parallel execution
                 logger=None,
                 *args,
                 **kwargs,
                 ):
        super().__init__(agent, num_threads=num_threads, logger=logger, *args, **kwargs)
        self.optimizer = optimizer
        self.n_iters = 0  # number of iterations


    def train(self,
              guide,
              train_dataset,
              *,
              ensure_improvement: bool = False,  # whether to check the improvement of the agent
              improvement_threshold: float = 0.,  # threshold for improvement
              num_epochs: int = 1,  # number of training epochs
              batch_size: int = 1,  # batch size for updating the agent
              test_dataset = None,  # dataset of (x, info) pairs to evaluate the agent
              eval_frequency: int = 1,  # frequency of evaluation
              log_frequency: Union[int, None] = None,  # frequency of logging
              save_frequency: Union[int, None] = None,  # frequency of saving the agent
              save_path: str = "checkpoints/agent.pkl",  # path to save the agent
              min_score: Union[int, None] = None,  # minimum score to update the agent
              verbose: Union[bool, str] = False,  # whether to print the output of the agent
              num_threads: int = None,  # maximum number of threads to use (overrides self.num_threads)
              **kwargs
              ):
        """
            Given a dataset of (x, info) pairs, the algorithm will:
            1. Forward the agent on the inputs and compute the feedback using the guide.
            2. Update the agent using the feedback.
            3. Evaluate the agent on the test dataset and log the results.
        """

        log_frequency = log_frequency or eval_frequency  # frequency of logging (default to eval_frequency)
        num_threads = num_threads or self.num_threads  # Use provided num_threads or fall back to self.num_threads
        use_asyncio = self._use_asyncio(num_threads)

        test_scores = []

        # Evaluate the agent before learning
        if eval_frequency > 0:
            test_score = self.evaluate(self.agent, guide, test_dataset['inputs'], test_dataset['infos'],
                          min_score=min_score, num_threads=num_threads,
                          description=f"Evaluating agent (iteration {self.n_iters})")  # and log
            test_scores.append(test_score)
            self.logger.log('Average test score', test_score, self.n_iters, color='green')

        # Save the agent before learning if save_frequency > 0
        if save_frequency is not None and save_frequency > 0:
            self.save_agent(save_path, self.n_iters)

        # TODO random sampling with replacement
        loader = DataLoader(train_dataset, batch_size=batch_size)
        train_scores = []
        test_score = None

        for i in range(num_epochs):
            # Train agent
            for xs, infos in loader:
                # Backup the current value of the parameters
                backup_dict = {p: copy.deepcopy(p.data) for p in self.agent.parameters()}

                # Forward the agent on the inputs and compute the feedback using the guide
                if use_asyncio: # Run forward asynchronously
                    outputs = async_run([self.forward]*len(xs),
                                       [(self.agent, x, guide, info) for x, info in zip(xs, infos)],
                                       max_workers=num_threads,
                                       description=f"Forward pass (batch size: {len(xs)})")  # async forward
                else: # Run forward sequentially
                    outputs = [self.forward(self.agent, x, guide, info) for x, info in zip(xs, infos) ]

                # Update the agent
                score = self.update(outputs, verbose=verbose)

                # Reject the update if the score on the current batch is not improved
                if ensure_improvement:
                    changes = any([backup_dict[p] != p.data for p in self.agent.parameters() ])
                    if changes: # Only check improvement if there're changes in the parameters for efficiency
                        if not self.has_improvement(xs, guide, infos, score, outputs, backup_dict,
                                               threshold=improvement_threshold, num_threads=num_threads):
                            self.optimizer.update(backup_dict) # Restore the backup

                self.n_iters += 1

                # Evaluate the agent after update
                if test_dataset is not None and self.n_iters % eval_frequency == 0:
                    test_score = self.evaluate(self.agent, guide, test_dataset['inputs'], test_dataset['infos'],
                                  min_score=min_score, num_threads=num_threads,
                                  description=f"Evaluating agent (iteration {self.n_iters})")  # and log
                    test_scores.append(test_score)
                    self.logger.log('Average test score', test_score, self.n_iters, color='green')

                # Save the agent
                if save_frequency is not None and save_frequency > 0 and self.n_iters % save_frequency == 0:
                    self.save_agent(save_path, self.n_iters)

                # Logging
                if score is not None:  # so that mean can be computed
                    train_scores.append(score)
                if self.n_iters % log_frequency == 0:
                    print(f"Epoch: {i}. Iteration: {self.n_iters}")
                    self.logger.log("Instantaneous train score", score, self.n_iters)
                    self.logger.log("Average train score", np.mean(train_scores), self.n_iters)
                    for p in self.agent.parameters():
                        self.logger.log(f"Parameter: {p.name}", p.data, self.n_iters, color='red')

        return train_scores, test_scores # test_score

    def evaluate(self, agent, guide, xs, infos, min_score=None, num_threads=None, description=None):
        """ Evaluate the agent on the given dataset. """
        num_threads = num_threads or self.num_threads  # Use provided num_threads or fall back to self.num_threads
        test_scores = evaluate(agent, guide, xs, infos, min_score=min_score, num_threads=num_threads,
                              description=description)
        if all([s is not None for s in test_scores]):
            return np.mean(test_scores)

    def has_improvement(self, xs, guide, infos, current_score, current_outputs, backup_dict, threshold=0, num_threads=None, *args, **kwargs):
        # This function can be overridden by subclasses to implement their own improvement check.
        """ Check if the updated agent is improved compared to the current one.

            Args:
                xs: inputs
                infos: additional information for the guide
                current_score: current score of the agent
                current_outputs: outputs of the agent, guide interaction
                backup_dict: backup of the current value of the parameters
                improvement_threshold: threshold for improvement
                num_threads: maximum number of threads to use
        """
        num_threads = num_threads or self.num_threads  # Use provided num_threads or fall back to self.num_threads
        new_score = self.evaluate(self.agent, guide, xs, infos, num_threads=num_threads,
                                 description=f"Checking improvement (iteration {self.n_iters})",
                                 *args, **kwargs)  # evaluate the updated agent
        if new_score is None or new_score <= current_score - threshold:
            print_color(f"Update rejected: Current score {current_score}, New score {new_score}", 'red')
            return False
        else:
            print_color(f"Update accepted: Current score {current_score}, New score {new_score}", 'green')
            return True


    def forward(self, agent, x, guide, info):
        """ Forward the agent on the input and compute the feedback using the guide.
            Args:
                agent: trace.Module
                x: input
                guide: (question, student_answer, info) -> score, feedback
                info: additional information for the guide
            Returns:
                outputs that will be used to update the agent
        """
        raise NotImplementedError("Subclasses must implement this method")

    def update(self, outputs, verbose=False):
        """ Subclasses can implement this method to update the agent.
            Args:
                outputs: returned value from self.step
                verbose: whether to print the output of the agent
            Returns:
                score: average score of the minibatch of inputs
        """
        raise NotImplementedError("Subclasses must implement this method")



@trace.bundle()
def batchify(*items):
    """ Concatenate the items into a single string """
    output = ''
    for i, item in enumerate(items):
        output += f'ID {[i]}: {item}\n'
    return output


class MinibatchAlgorithm(Minibatch):
    """
        The computed output of each instance in the minibatch is aggregated and a batched feedback is provided to update the agent.
    """

    def forward(self, agent, x, guide, info):
        return standard_optimization_step(agent, x, guide, info)  # (score, target, feedback)

    def update(self, outputs, *args, **kwargs):
        """ Subclasses can implement this method to update the agent.
            Args:
                outputs: returned value from self.step
                verbose: whether to print the output of the agent
            Returns:
                score: average score of the minibatch of inputs

        """
        scores, targets, feedbacks = [], [], []
        # Concatenate the targets and feedbacks into a single string
        for target, score, feedback in outputs:
            scores.append(score)
            targets.append(target)
            feedbacks.append(feedback)
        target = batchify(*targets)
        feedback = batchify(*feedbacks).data  # str
        average_score = np.mean(scores) if all([s is not None for s in scores]) else None

        fig = target.backward(visualize=True, retain_graph=True)
        fig.render("minibatch.pdf")

        # Update the agent using the feedback
        self.optimizer.zero_feedback()
        self.optimizer.backward(target, feedback)
        self.optimizer_step(*args, **kwargs)  # update the agent

        return average_score  # return the average score of the minibatch of inputs

    def optimizer_step(self, bypassing=False, *args, **kwargs):
        """ Subclasses can implement this method to update the agent. """
        # We separate this method from the update method to allow subclasses to implement their own optimization step.
        return self.optimizer.step(*args, bypassing=bypassing, **kwargs)


class BasicSearchAlgorithm(MinibatchAlgorithm):
    """ A basic search algorithm that calls the optimizer multiple times to get candidates and selects the best one based on validation set. """

    def train(self,
              guide, # guide to provide feedback
              train_dataset,  # dataset of (x, info) pairs to train the agent
              *,
              validate_dataset = None, # dataset of (x, info) pairs to evaluate the agent for candidate selection
              validate_guide = None,  #  to provide scores for the validation set
              num_proposals = 4,  # number of proposals to get from the optimizer
              num_epochs = 1,  # number of training epochs
              batch_size = 1,  # batch size for updating the agent
              test_dataset = None, # dataset of (x, info) pairs to evaluate the agent
              eval_frequency = 1, # frequency of evaluation
              log_frequency = None,  # frequency of logging
              min_score = None,  # minimum score to update the agent
              verbose = False,  # whether to print the output of the agent
              num_threads = None,  # maximum number of threads to use
              **kwargs
              ):

        self.num_proposals = num_proposals
        self.validate_dataset = validate_dataset or train_dataset  # default to train_dataset
        self.validate_guide = validate_guide or guide
        self.min_score = min_score
        self.current_score = None

        return super().train(guide, train_dataset, num_epochs=num_epochs, batch_size=batch_size,
                      test_dataset=test_dataset, eval_frequency=eval_frequency, log_frequency=log_frequency,
                      min_score=min_score, verbose=verbose, num_threads=num_threads, **kwargs)

    # This code should be reusable for other algorithms
    def optimizer_step(self, bypassing=False, verbose=False, *args, **kwargs):
        """ Use the optimizer to propose multiple updates and select the best one based on validation score. """

        def validate():
            """ Validate the agent on the validation dataset. """
            scores = evaluate(self.agent,
                              self.validate_guide,
                              self.validate_dataset['inputs'],
                              self.validate_dataset['infos'],
                              min_score=self.min_score,
                              num_threads=self.num_threads,
                              description="Validating proposals")
            return np.mean(scores) if all([s is not None for s in scores]) else -np.inf

        # TODO perhaps we can ask for multiple updates in one query or use different temperatures in different queries
        # Generate different proposals
        step_kwargs = dict(bypassing=True, verbose='output')  # we don't print the inner full message
        use_asyncio = self._use_asyncio()
        if use_asyncio:
            update_dicts = async_run([super().optimizer_step]*self.num_proposals,
                                    kwargs_list=[step_kwargs] * self.num_proposals,
                                    max_workers=self.num_threads,
                                    description=f"Generating {self.num_proposals} proposals")  # async step
        else:
            update_dicts = [self.optimizer.step(**step_kwargs) for _ in range(self.num_proposals)]

        # Validate the proposals
        candidates = []
        backup_dict = {p: copy.deepcopy(p.data) for p in self.agent.parameters()}  # backup the current value
        for update_dict in update_dicts:
            if len(update_dict) == 0:
                continue
            self.optimizer.update(update_dict)  # set the agent with update_dict
            score = validate()  # check the score on the validation set
            candidates.append((score, update_dict))
            self.optimizer.update(backup_dict)  # restore the backup

        # Include the current parameter as a candidate
        if self.current_score is None:
            self.current_score = validate()
        candidates.append((self.current_score, backup_dict))

        # Find the candidate with the best score
        best_score, best_update = max(candidates, key=lambda x: x[0])
        self.current_score = best_score

        if verbose:
            print_color(f"Best score: {best_score} out of scores {[c[0] for c in candidates]}", 'green')
            print(f"Selected Update:\n{best_update}")

        # Make the best update
        self.optimizer.update(best_update)

        # Logging
        self.logger.log('Validation score', best_score, self.n_iters, color='green')