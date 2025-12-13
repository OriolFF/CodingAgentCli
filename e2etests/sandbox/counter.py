class Counter:
    def __init__(self, initial_value=0):
        self._count = initial_value

    def increment(self):
        self._count += 1

    def decrement(self):
        self._count -= 1

    def reset(self):
        self._count = 0

    def get_count(self):
        return self._count