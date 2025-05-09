# common/BDR.py

class BDR:
    def __init__(self, alpha: float, delta: float):
        self.alpha = alpha
        self.delta = delta

    def sbf(self, t: float) -> float:
        """Supply Bound Function: amount of service by time t."""
        if t < self.delta:
            return 0.0
        return self.alpha * (t - self.delta)

    def to_supply_task(self) -> tuple[float,float]:
        """
        Theorem 3 (half–half): turn a BDR(alpha, delta) into a 
        periodic supply‐task (C_s, T_s) with
            T_s = delta / (2*(1-alpha))
            C_s = alpha * T_s

        If alpha == 1.0, the denominator goes to zero.  We special‐case
        that to mean “full CPU” (i.e. a 100% server).  A simple
        periodic model for 100% server is C_s = 1.0, T_s = 1.0.
        """
        if self.alpha >= 1.0:
            # full‐capacity server: always able to supply t units by t
            return 1.0, 1.0

        denom = 2.0 * (1.0 - self.alpha)
        T_s = self.delta / denom
        C_s = self.alpha * T_s
        return C_s, T_s

    @staticmethod
    def can_schedule_children(parent: "BDR", children: list["BDR"]) -> bool:
        """
        Theorem 1: A parent BDR can host these children iff
          1) sum(alpha_i) <= alpha_parent
          2) delta_i > delta_parent  for all i
        """
        if sum(c.alpha for c in children) > parent.alpha:
            return False
        if any(c.delta <= parent.delta for c in children):
            return False
        return True
