from opto.optimizers import OptoPrime
from opto import trace
from opto.trainer.utils import async_run
from opto.trainer.algorithm import DirectUpdate
import numpy as np




@trace.bundle()
def concat_list_as_str(*items):
    """ Concatenate the items into a single string """
    output = ''
    for i, item in enumerate(items):
        output += f'ID {[i]}: {item}\n'
    return output




class DataLoader:

    def __init__(self, dataset, batch_size=1, replacement=False, shuffle=True):
        """ Initialize the data loader

        Args:
            dataset: the dataset to load (a dict of inputs and infos)
            batch_size: the number of samples to load in each batch
            replacement: whether to sample with replacement
            shuffle: whether to shuffle the dataset after each epoch
        """
        assert isinstance(dataset, dict), "Dataset must be a dict"
        assert 'inputs' in dataset and 'infos' in dataset, "Dataset must have 'inputs' and 'infos' key"
        assert len(dataset['inputs']) == len(dataset['infos']), "Inputs and infos must have the same length"

        self.dataset = dataset
        self.batch_size = batch_size
        self.replacement = replacement
        self.shuffle = shuffle
        self._indices = self._update_indices()

    def __iter__(self):
        indices = self._indices
        for i in range(0, len(indices), self.batch_size):
            xs = [ self.dataset['inputs'][ind]  for ind in indices[i:i + self.batch_size] ]
            infos = [self.dataset['infos'][ind] for ind in indices[i:i + self.batch_size] ]
            yield xs, infos

        if self.shuffle:
            self._indices = self._update_indices()

    def _update_indices(self):
        N = len(self.dataset['inputs'])
        return np.random.choice(N, size=N, replace=self.replacement)




def evaluate(agent, teacher, inputs, infos, min_score=0):
    """ Evaluate the agent on the inputs and return the scores """
    def evaluate_single(i):
        try:
            output = agent(inputs[i])
            score, feedback = teacher(output, infos[i])
        except trace.ExecutionError as e:
            output = e.exception_node
            score, feedback = min_score, output.create_feedback('full')
        return score, feedback

    N = len(inputs)
    assert len(inputs) == len(infos), "Inputs and infos must have the same length"
    results = async_run([evaluate_single]*N, [(i,) for i in range(N)]) # list of tuples
    scores = [r[0] for r in results]
    return scores



# TODO write it as a class?
def train(agent,  # trace.model
          teacher, # teacher to provide feedback
          train_dataset,  # dataset of (x, info) pairs
          *,
          num_epochs = 1,  # number of training epochs
          logger = None,  # a logger that provides `log(name, data, step, **kwargs)`` method to log the training process
          batch_size = 1,  # batch size for updating the agent
          algorithm = None,  # algorithm to update the agent
          test_dataset = None, # dataset of (x, info) pairs to evaluate the agent
          eval_frequency = 1, # frequency of evaluation
          log_frequency = 1,  # frequency of logging
          update_score_threshold = 1,  # only update the agent if the score is below this threshold
          stop_score_threshold = float("inf"),  # stop training if the score is above this threshold
          min_score = 0,  # minimum score to update the agent
          ):
    # TODO aysnc forward

    if algorithm is None:
        algorithm = DirectUpdate(optimizer=OptoPrime(agent.parameters()))
    loader = DataLoader(train_dataset, batch_size=batch_size)

    n_updates = 0  # number of updates
    n_iters = 0 # number of iterations (Note: n_updates <= n_iters)
    last_test_n = None

    train_scores = []
    for i in range(num_epochs):

        # Train agent
        targets, feedbacks = [], []
        for x, info in loader:


            # Forward and compute feedback
            try:
                target = agent(x)
                score, feedback = teacher(target.data, info)
            except trace.ExecutionError as e:
                target = e.exception_node
                score, feedback = min_score, target.create_feedback('full')
            train_scores.append(score)

            # Only update the agent if there is a mistake
            if score < update_score_threshold: # mistake the agent learn
                targets.append(target)
                feedbacks.append(feedback)

            # Update the agent when the batch is full
            update_agent = len(targets)>=batch_size
            if update_agent:

                # Evaluate the agent before learning
                if n_updates == 0:
                    test_scores = evaluate(agent, teacher, test_dataset['inputs'], test_dataset['infos'], min_score=min_score)
                    logger.log('Average test score', np.mean(test_scores), n_updates, 'green')

                # Concatenate the targets and feedbacks into a single string
                target = concat_list_as_str(*targets)
                feedback = concat_list_as_str(*feedbacks).data  # str

                # Update the agent
                algorithm.update(target, feedback, verbose='output')
                n_updates += 1
                targets, feedbacks = [], []

                # Evaluate the agent after update
                if test_dataset is not None and n_updates % eval_frequency == 0:
                    test_scores = evaluate(agent, teacher, test_dataset['inputs'], test_dataset['infos'])
                    logger.log('Average test score', np.mean(test_scores), n_updates, 'green')

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