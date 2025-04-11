from dataclasses import dataclass

from src.common.scheduler import Scheduler

@dataclass
class Architecture:
    core_id:int
    speed_factor:float
    scheduler: Scheduler
