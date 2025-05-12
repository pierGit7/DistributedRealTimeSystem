from enum import Enum

from common.task import Task

class Scheduler(Enum):
    RM = "Rate Monotonic"
    EDF = "Earliest Deadline First"
