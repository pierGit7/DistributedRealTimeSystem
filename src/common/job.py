class Job:
    def __init__(self, task, release_time: int, execution_time: float):
        self.id = f"{task.id}_{release_time}"
        self.task_id = task.id
        self.priority = task.priority
        self.release_time: int = release_time
        self.execution_time: float = execution_time
        self.remaining_time: float = execution_time
        self.absolute_deadline: int = release_time + task.period + self.execution_time * 0.0001 # Tie-breaker
        self.start_time: int = -1

    # Make it sortable for priority queues if needed (e.g., for EDF)
    def __lt__(self, other):
        # Example for EDF: earlier deadline is higher priority
        if self.absolute_deadline != other.absolute_deadline:
            return self.absolute_deadline < other.absolute_deadline
        # Tie-breaking (e.g., by original task priority if RM, or by release time)
        # For pure EDF, could be arbitrary or based on task ID for determinism
        return self.task_template.priority < other.task_template.priority # Assuming lower prio number is higher

    def __repr__(self):
        return (f"Job(id={self.id}, task={self.task_template.id}, release={self.release_time}, "
                f"deadline={self.absolute_deadline}, rem={self.remaining_time:.2f})")