import logging


class ModuleFilter(logging.Filter):
    def __init__(self, exclude=None):
        super().__init__()
        self.exclude = set(exclude) if exclude else set()

    def filter(self, record):
        return record.module not in self.exclude
