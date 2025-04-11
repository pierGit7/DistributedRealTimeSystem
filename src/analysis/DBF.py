from abc import ABC, abstractmethod
from common.task import Task

class DBF():
    def __init__(self, tasks: list[Task], time_interval: float, explicit_dead_line: float = 0):
        self.explicit_dead_line = explicit_dead_line
        self.tasks = tasks
        self.time_interval = time_interval
    @abstractmethod
    def getDBS(self) -> float: ...
    
class DBF_EDF(DBF):
    def __init(self, tasks: list[Task], time_interval: float, explicit_dead_line: float = 0):
        super().__init__(tasks, time_interval, explicit_dead_line)
        
    def getDBS(self) -> float:
        """
        Calculate the Demand Bound Function (DBF) for a set of tasks.
        The DBF is computed as the sum of the workload contributions of all tasks
        within a specified time interval. Each task contributes to the DBF based
        on its worst-case execution time (WCET) and period.
        Returns:
            float: The computed DBF value for the set of tasks.
        """
        
        dbs: float = 0
        for task in self.tasks:
            num = (self.time_interval + (task.period * self.explicit_dead_line) - self.explicit_dead_line)
            dbs += (num / task.period) * task.wcet
        return dbs
    
class DBF_FPS(DBF):
    def __init(self, tasks: list[Task], time_interval: float, task_index: int):
        self.task_index = task_index    
        super().__init__(tasks, time_interval)
        
    def getDBS(self) -> float:
        """
        Calculate the Demand Bound Function (DBF) for a set of tasks.
        The DBF is computed as the sum of the workload contributions of all tasks
        within a specified time interval. Each task contributes to the DBF based
        on its worst-case execution time (WCET) and period.
        Returns:
            float: The computed DBF value for the set of tasks.
        """
        
        my_task = self.tasks[self.task_index]
        higher_priority_tasks = [task for task in self.tasks if task.priority > self.tasks[self.task_index].priority]
        dbs: float = my_task.wcet
        for task in higher_priority_tasks:
            dbs += (self.time_interval / task.period) * task.wcet
        return dbs
    