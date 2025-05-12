import sys
import csv
import math
from functools import reduce

from common.csvreader import read_csv
from common.DBF import DBF
from common.BDR import BDR
from common.scheduler import Scheduler


def lcm(a: int, b: int) -> int:
    """Compute least common multiple of two integers."""
    return abs(a * b) // math.gcd(a, b)


def adjust_wcet(tasks, budgets, architectures):
    # Adjust WCET by core speed factor (scaling per architecture)
    core_speed_map = {arch.id: arch.speed_factor for arch in architectures}
    component_core_map = {budget.id: budget.core_id for budget in budgets}
    for task in tasks:
        core_id = component_core_map[task.component_id]
        task.wcet = task.wcet / core_speed_map[core_id]
    return tasks


def group_tasks_by_component(tasks, budgets):
    # Group tasks into their components based on budgets.csv
    components = {}
    for budget in budgets:
        comp_id = budget.id
        comp_tasks = [t for t in tasks if t.component_id == comp_id]
        # Sort for RM priority order
        if budget.scheduler == Scheduler.RM:
            comp_tasks.sort(key=lambda t: t.priority)
        components[comp_id] = {
            'tasks': comp_tasks,
            'scheduler': budget.scheduler,
            'core_id': budget.core_id,
            'budget': budget.budget,      # Q from PRM
            'period': budget.period,      # P from PRM
            'schedulable': False,
        }
    return components


def check_component_schedulability(components):
    """
    For each component, check local schedulability under its PRM budget:
    - Convert PRM (Q,P) to a conservative BDR lower-bound via Half-Half (Theorem 3): rate=Q/P, delay=2*(P−Q)
    - Use Supply Bound Function sbf_BDR (Eq. 6) for supply.sbf(t)
    - Use Demand Bound Functions:
        • RM: dbf_rm(W,t,i) (Eq. 4)
        • EDF: dbf_edf(W,t) (Eq. 2)
    - For both schedulers, generate all critical points t = k·T_j up to each component's max deadline.
    Then apply the tests:
        RM: ∀τ_i ∃ t ≤ T_i such that dbf_rm(W,t,i) ≤ sbf(t)
        EDF: ∀ t ≥ 0 dbf_edf(W,t) ≤ sbf(t)
    """
    for comp in components.values():
        tasks = comp['tasks']
        sched = comp['scheduler']
        Q, P = comp['budget'], comp['period']
        supply = BDR(rate=Q/P, delay=2*(P-Q))  # Theorem 3

        # Build global critical points: multiples of all periods
        periods = [t.period for t in tasks]
        max_deadline = max(periods) if periods else 0
        time_points = set()
        for T in periods:
            k = 1
            while k * T <= max_deadline:
                time_points.add(k * T)
                k += 1
        time_points = sorted(time_points)

        ok = True
        if sched == Scheduler.RM:
            # For each task i, need ∃ t ≤ T_i s.t. dbf_rm(W,t,i) ≤ sbf(t)
            for idx, task in enumerate(tasks):
                Ti = task.period
                found = False
                for t in time_points:
                    if t > Ti:
                        break
                    demand = DBF.dbf_rm(tasks, t, idx)  # Eq.4
                    if demand <= supply.sbf(t):         # Eq.6
                        found = True
                        break
                if not found:
                    ok = False
                    break
        else:
            # EDF: ∀ t, dbf_edf(W,t) ≤ sbf(t)
            for t in time_points:
                demand = DBF.dbf_edf(tasks, t)      # Eq.2
                if demand > supply.sbf(t):          # Eq.6
                    ok = False
                    break

        # Also ensure every individual task meets its deadline under this supply
        task_checks = []
        for idx, task in enumerate(tasks):
            if sched == Scheduler.RM:
                demand = DBF.dbf_rm(tasks, task.period, idx)
            else:
                demand = DBF.dbf_edf(tasks, task.period)
            task_checks.append(demand <= supply.sbf(task.period))
        comp['schedulable'] = ok and all(task_checks)
    return components


def summarize_by_core(components, architectures):
    """
    At system level, apply Theorem 1 for BDR composition via can_schedule_children:
      - Parent = full-CPU BDR(rate=1.0, delay=0.0)
      - Children = list of BDR(rate=Q/P, delay=2*(P-Q)) for each component on the core
      - Also ensure each component passed its local schedulability check
    """
    # Group components per core
    core_map = {arch.id: [] for arch in architectures}
    for comp in components.values():
        core_map[comp['core_id']].append(comp)

    core_summary = {}
    for core_id, comps_on_core in core_map.items():
        # Build BDR interfaces for each child component
        child_bdrs = [BDR(rate=comp['budget']/comp['period'],
                          delay=2*(comp['period']-comp['budget']))
                      for comp in comps_on_core]
        # Parent BDR representing full CPU
        parent_bdr = BDR(rate=1.0, delay=0.0)

                # Theorem 1: compositional check using helper
        # Special-case: if parent delay == 0, allow child.delay >= 0
        if parent_bdr.delay == 0.0:
            compositional_ok = sum(c.rate for c in child_bdrs) <= parent_bdr.rate
        else:
            compositional_ok = BDR.can_schedule_children(parent_bdr, child_bdrs)

        # Ensure each component's own schedulability
        all_children_ok = all(comp['schedulable'] for comp in comps_on_core)

        core_summary[core_id] = compositional_ok and all_children_ok
    return core_summary


def output_report(components, core_summary):
    # Produce console output only (no file)
    for comp_id, comp in components.items():
        Q, P = comp['budget'], comp['period']
        rate = Q/P              # PRM bandwidth
        delay = 2*(P-Q)         # BDR startup delay
        label = 'Schedulable' if comp['schedulable'] else 'Not schedulable'
        print(f"Component {comp_id} (Core {comp['core_id']}, {comp['scheduler'].name}): "
              f"PRM_sup=(Q={Q},P={P}), BLB(rate={rate:.4f},delay={delay:.2f}) - {label}")

    print('\nCore-level Summary:')
    for core_id, ok in core_summary.items():
        core_stat = 'Schedulable' if ok else 'Not schedulable'
        print(f"Core {core_id}: {core_stat}")


def write_solution_csv(tasks, components, filename='solution.csv'):  # noqa: E302(tasks, components, filename='solution.csv'):(tasks, components, filename='solution.csv'):
    # CSV with task- and component-level results
    rows = []
    for cid, comp in components.items():
        supply = BDR(rate=comp['budget']/comp['period'], delay=2*(comp['period']-comp['budget']))
        for task in comp['tasks']:
            if comp['scheduler'] == Scheduler.RM:
                idx = comp['tasks'].index(task)
                demand = DBF.dbf_rm(comp['tasks'], task.period, idx)  # Eq.4
            else:
                demand = DBF.dbf_edf(comp['tasks'], task.period)     # Eq.2
            rows.append({
                'task_name': task.id,
                'component_id': cid,
                'task_schedulable': int(demand <= supply.sbf(task.period)),
                'component_schedulable': int(comp['schedulable'])
            })
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'task_name','component_id','task_schedulable','component_schedulable'
        ])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    if len(sys.argv) != 4:
        print("Usage: python analysis.py <architecture.csv> <budgets.csv> <tasks.csv>")
        sys.exit(1)

    architectures, budgets, tasks = read_csv()
    tasks = adjust_wcet(tasks, budgets, architectures)
    components = group_tasks_by_component(tasks, budgets)

    # Local component checks
    components = check_component_schedulability(components)
    # Global core summaries
    core_summary = summarize_by_core(components, architectures)

    output_report(components, core_summary)
    write_solution_csv(tasks, components)

if __name__ == '__main__':
    main()
