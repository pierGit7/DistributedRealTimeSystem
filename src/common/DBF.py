"""
Compute Demand Bound Functions (DBF) for EDF and RM scheduling.
"""
import math

class DBF:
    @staticmethod
    def dbf_edf(tasks, t):
        """
        Demand bound function under EDF for implicit-deadline tasks.
        tasks: list of dicts or objects with 'wcet' and 'period'
        """
        total = 0.0
        for task in tasks:
            C = task['wcet'] if isinstance(task, dict) else task.wcet
            T = task['period'] if isinstance(task, dict) else task.period
            total += math.floor(t / T) * C
        return total

    @staticmethod
    def dbf_edf_explicit(tasks, t):
        """
        DBF under EDF for tasks with explicit deadlines.
        tasks: list of dicts or objects with 'wcet', 'period', and 'deadline'
        """
        total = 0.0
        for task in tasks:
            C = task['wcet'] if isinstance(task, dict) else task.wcet
            T = task['period'] if isinstance(task, dict) else task.period
            D = task.get('deadline', T) if isinstance(task, dict) else getattr(task, 'deadline', T)
            total += math.floor((t + T - D) / T) * C
        return total

    @staticmethod
    def dbf_rm(tasks, t, idx):
        """
        DBF under RM (fixed-priority) for task at index idx.
        tasks: list of dicts or objects sorted by priority (shorter period => higher priority)
        idx: index of the task in question
        Returns: C_i + sum_{higher priority k} ceil(t/T_k)*C_k
        """
        C_i = tasks[idx]['wcet'] if isinstance(tasks[idx], dict) else tasks[idx].wcet
        demand = C_i
        for k in range(idx):
            task_k = tasks[k]
            C_k = task_k['wcet'] if isinstance(task_k, dict) else task_k.wcet
            T_k = task_k['period'] if isinstance(task_k, dict) else task_k.period
            demand += math.ceil(t / T_k) * C_k
        return demand