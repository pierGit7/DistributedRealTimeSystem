class Task:
    def __init__(self, task_name: str, wcet: int, period: int, component_id: str, priority: int | None):
        self.id = task_name
        self.wcet = wcet
        self.period = period
        self.component_id = component_id
        self.priority = priority

        self.remaining_time = self.wcet
        

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.id == other.id and
                self.wcet == other.wcet and
                self.period == other.period and
                self.component_id == other.component_id and
                self.priority == other.priority)

    def __repr__(self):
        return f"Task(task_name='{self.id}', wcet={self.wcet}, period={self.period}, component_id='{self.component_id}', priority={self.priority})"