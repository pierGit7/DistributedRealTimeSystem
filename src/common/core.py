from dataclasses import dataclass

from common.scheduler import Scheduler

@dataclass
class Core:
    """
    A class representing a processing core architecture with its properties and scheduling capabilities.
    Attributes:
        core_id (int): The unique identifier for the core.
        speed_factor (float): A numerical value representing the core's speed relative to a nominal speed.
            1.0 represents the nominal speed. A value of 0.5 indicates a core that is 50% slower,
            and a value of 1.2 indicates a core that is 20% faster. The WCET of tasks assigned to
            a core must be adjusted by dividing the nominal WCET by the speed_factor.
        scheduler (Scheduler): The scheduler instance responsible for managing task execution on this core.
    """
    id:int
    speed_factor:float
    scheduler: Scheduler
