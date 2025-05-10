from dataclasses import dataclass

@dataclass
class Task:
    task_name:str
    wcet:float
    period:float
    component_id:str
    priority:int|None
    

