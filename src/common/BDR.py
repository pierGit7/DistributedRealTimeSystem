"""
Bounded Delay Resource (BDR) model with SBF and conversion to periodic supply task.
"""
class BDR:
    def __init__(self, alpha, delta):
        self.alpha = alpha
        self.delta = delta

    def sbf(self, t):
        """
        Supply Bound Function for BDR resource R = (alpha, delta).
        Returns minimum resource supply in any interval of length t.
        """
        if t < self.delta:
            return 0.0
        return self.alpha * (t - self.delta)

    def to_periodic_task(self):
        """
        Convert BDR interface (alpha, delta) into an equivalent periodic
        supply task (budget, period) via the Half-Half Theorem.
        budget = alpha * delta / (2 * (1 - alpha))
        period = delta / (2 * (1 - alpha))
        """
        if self.alpha >= 1.0:
            # full processor, budgets equal
            return {'budget': 1.0, 'period': 1.0}
        C = self.alpha * self.delta / (2 * (1 - self.alpha))
        T = self.delta / (2 * (1 - self.alpha))
        return {'budget': C, 'period': T}