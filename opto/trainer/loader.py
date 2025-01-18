import numpy as np




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
