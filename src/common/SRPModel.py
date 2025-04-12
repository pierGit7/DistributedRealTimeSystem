from dataclasses import dataclass

@dataclass
class SRPModel:
    # Start Index (Si) and End Index (Ei) for resource access
    resource_access: list[tuple[int, int]]
    period: int 
    