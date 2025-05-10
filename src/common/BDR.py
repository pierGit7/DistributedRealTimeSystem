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

    @classmethod
    def from_tasks(cls, tasks: List, scheduler: Scheduler) -> "BDR":
        """
        Derive a BDR interface (rate, delay) for a given task set and scheduler.
        1) rate = total utilization = sum(wcet/period)
        2) delay = max(0, min_t [t - dbf(W,t)/rate]) over all critical points
        Critical points are multiples of task periods up to the hyperperiod.
        """
        if not tasks:
            return cls(0.0, 0.0)
        # compute rate (availability factor)
        rate = sum(task.wcet / task.period for task in tasks)

        # sort tasks by priority for RM
        if scheduler == Scheduler.RM:
            sorted_tasks = sorted(tasks, key=lambda t: t.priority)
            periods = [t.period for t in sorted_tasks]
            max_period = max(periods) if periods else 0
            # Generate time points up to max_period
            time_points = set()
            for T in periods:
                k = 1
                while (t := k * T) <= max_period:
                    time_points.add(t)
                    k += 1
            time_points = sorted(time_points)
        else:
            # EDF: use hyperperiod
            periods = [int(t.period) for t in tasks]
            hyper = reduce(lcm, periods, 1)
            time_points = sorted({k * T for T in periods for k in range(1, (hyper // T) + 1)})

        # compute partition delay
        if rate > 0:
            slacks = []
            for t in time_points:
                if scheduler == Scheduler.EDF:
                    demand = DBF.dbf_edf(tasks, t)
                else:
                    demand = max(DBF.dbf_rm(sorted_tasks, t, idx)
                                 for idx in range(len(sorted_tasks)))
                slacks.append(t - demand / rate)
            delay = max(0.0, min(slacks)) 
        else:
            delay = 0.0

        return cls(rate, delay)
