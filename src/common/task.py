from dataclasses import dataclass

@dataclass
class Task:
    task_name:str
    wcet:int
    period:int
    component_id:str
    priority:int|None
    

