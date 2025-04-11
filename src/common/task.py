from dataclasses import dataclass

from src.common.scheduler import Scheduler

@dataclass
class Task:
    task_name:str
    wcet:int
    period:int
    component_id:str
    priority:int|None
    

