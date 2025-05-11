# common/BDR.py

import math
from typing import List, Tuple
from functools import reduce

from common.DBF import DBF
from common.scheduler import Scheduler


def lcm(a: int, b: int) -> int:
    """Compute least common multiple of two integers."""
    return abs(a * b) // math.gcd(a, b)


class BDR:
    def __init__(self, rate: float, delay: float):
        """
        Bounded-Delay Resource model:
          rate  – long-term supply rate (0 < rate <= 1)
          delay – maximum startup delay
        """
        self.rate = rate
        self.delay = delay

    def sbf(self, interval: float) -> float:
        """
        Supply Bound Function (Eq. 6):
          sbf(interval) = 0,                          if interval < delay
                          rate * (interval - delay), otherwise
        """
        if interval < self.delay:
            return 0.0
        return self.rate * (interval - self.delay)

    @staticmethod
    def can_schedule_children(parent: "BDR", children: List["BDR"]) -> bool:
        """
        Theorem 1: A parent BDR can host these child interfaces iff
          1) sum(child.rate) <= parent.rate
          2) child.delay > parent.delay  for every child
        """
        if sum(c.rate for c in children) > parent.rate:
            return False
        if any(c.delay <= parent.delay for c in children):
            return False
        return True

    def supply_task_params(self) -> Tuple[float, float]: 
        """
        Theorem 3 (Half-Half): Transform this BDR interface into a periodic supply task.
        Returns (budget, period):
          period = delay / (2 * (1 - rate))
          budget = rate * period
        Special-case: if rate == 1.0, returns (1.0, 1.0) for full CPU.
        """
        if self.rate >= 1.0:
            return 1.0, 1.0
        if self.rate == 0.0:
            return self.rate, 0.0
        denom = 2.0 * (1.0 - self.rate)
        period = self.delay / denom
        budget = self.rate * period
        return budget, period

