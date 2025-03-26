# -*- coding: utf-8 -*-
"""
Samplestats
"""


class SampleStats:
    """
    Store sampled values and give access to statistics on these values
    """

    def __init__(self):
        self.maxvalues = None  # Int
        self.values = []  # [Ints or Floats]
        self.average = None  # Float

    def set_maxvalues(self, maxvalues):
        """
        Set maximum number of values to maintain in history
        """
        self.maxvalues = maxvalues

    def add_value(self, value):
        """
        Add a numeric value to the stored samples
        """
        if len(self.values) + 1 > self.maxvalues:
            self.values.remove(self.values[0])
        self.values.append(value)

    def compute_average(self):
        """
        Compute, store and return average of stored samples
        """
        # FIXME: add slicing support:
        if len(self.values) == 0:
            raise RuntimeError("Add values first !")
        self.average = sum(self.values) / len(self.values)
        return self.average

    def clear(self):
        """
        Erase store samples
        """
        self.values = []
