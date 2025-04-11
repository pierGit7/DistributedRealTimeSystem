from enum import Enum

class Scheduler(Enum):
    RM = "Rate Monotonic"
    EDF = "Earliest Deadline First"
