class FIFOBuffer:
    # A basic FIFO buffer
    def __init__(self, size: int):
        self.size = size
        self.buffer = []

    def add(self, item):
        if self.size > 0:
            self.buffer.append(item)
            self.buffer = self.buffer[-self.size:]

    def __iter__(self):
        return iter(self.buffer)

    def __len__(self):
        return len(self.buffer)
