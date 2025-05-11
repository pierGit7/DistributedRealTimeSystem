# common/DBF.py

import math
from typing import Sequence

class DBF:
    @staticmethod
    def dbf_edf(tasks: Sequence, interval: float) -> float:
        """
        Demand Bound Function under EDF for implicit-deadline tasks:
            dbfEDF(W, interval) = sum(floor(interval / period) * wcet)
        """
        total_demand = 0.0
        for task in tasks:
            executions = math.floor(interval / task.period)
            total_demand += executions * task.wcet
        return total_demand

    @staticmethod
    def dbf_edf_explicit(tasks: Sequence, interval: float) -> float:
        """
        Demand Bound Function under EDF for explicit-deadline tasks:
            dbfEDF(W, interval) = sum(floor((interval + period - deadline) / period) * wcet)
        """
        total_demand = 0.0
        for task in tasks:
            deadline = getattr(task, 'deadline', task.period)
            job_count = math.floor((interval + task.period - deadline) / task.period)
            if job_count > 0:
                total_demand += job_count * task.wcet
        return total_demand

    @staticmethod
    def dbf_rm(tasks: Sequence, interval: float, index: int) -> float:
        """
        Demand Bound Function under RM/DM for the task at 'index':
            dbfRM(W, interval, i) = wcet_i + sum(ceil(interval / period_k) * wcet_k)
            for all tasks k with higher priority (lower index).
        """
        # demand from the task itself
        demand = tasks[index].wcet
        # plus interference from all higher-priority tasks
        for higher in tasks[:index]:
            invocations = math.ceil(interval / higher.period)
            demand += invocations * higher.wcet
        return demand
