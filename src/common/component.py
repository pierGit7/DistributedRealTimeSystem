from common.scheduler import Scheduler

class Component:
    """
    Stores the budget and timing settings for a component in the system. The budget 
    controls how long a component can run, similar to a time allowance.

    Attributes:
        component_id (str): Name/ID of the component (example: "Camera1")
        scheduler (Scheduler): How tasks are ordered - either EDF or RM scheduling
        budget (int): How long the component can run (in time units) before it must pause
        period (int): How often the runtime budget refreshes (in time units)
        core_id (int): Which CPU core this component runs on
        priority (int | None): How important this component is compared to others
                              (used for RM scheduling, None for EDF)
                              Lower number means higher priority
    """
    def __init__(self, component_id: str, scheduler: Scheduler, budget: int, 
                 period: int, core_id: int, priority: int | None):
        self.id = component_id
        self.scheduler = scheduler
        self.budget = budget
        self.period = period
        self.core_id = core_id
        self.priority = priority
        self.remaining_budget = budget
        self.jobs_queue = []
