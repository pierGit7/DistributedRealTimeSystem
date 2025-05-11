from dataclasses import dataclass

from common.scheduler import Scheduler

@dataclass
class Budget:
    component_id: str
    scheduler:Scheduler
    budget:float
    period:float
    core_id:int
    priority:int|None
