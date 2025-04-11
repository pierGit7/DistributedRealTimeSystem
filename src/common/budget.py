from dataclasses import dataclass

from assignment.simulator.src.scheduler import Scheduler

@dataclass
class Budget:
    component_id: str
    scheduler:Scheduler
    budget:int
    period:int
    core_id:int
    priority:int|None
