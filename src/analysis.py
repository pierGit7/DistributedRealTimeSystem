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
    core_speed_map = {arch.core_id: arch.speed_factor for arch in architectures}
    component_core_map = {budget.component_id: budget.core_id for budget in budgets}

    for task in tasks:
        core_id = component_core_map[task.component_id]
        task.wcet = task.wcet / core_speed_map[core_id]  # Adjust WCET
    return tasks


def group_tasks_by_component(tasks, budgets):
    components = {}
    for budget in budgets:
        comp_id = budget.component_id
        comp_tasks = [t for t in tasks if t.component_id == comp_id]

        components[comp_id] = {
            "tasks": comp_tasks,
            "scheduler": budget.scheduler,
            "core_id": budget.core_id,
            "period": budget.period,  
            "budget": budget.budget,  
            "priority": budget.priority,
            "bdr": None,
            "supply": None,
            "schedulable": True,
        }
    return components

def analyze_components(components):
    def calculate_bdr(comp):
        """Calculate BDR interface using PRM-to-BDR conversion or task-derived values"""
        if comp["budget"] and comp["period"]:
            alpha = comp["budget"] / comp["period"]
            delta = 2 * (comp["period"] - comp["budget"])
            return BDR(alpha, delta)
        return BDR.from_tasks(comp["tasks"], comp["scheduler"])

    def get_time_points(tasks, scheduler, task_idx=None):
        """Get critical time points for schedulability analysis"""
        if scheduler == Scheduler.RM:
            # RM: Check up to current task's period with higher-priority tasks
            periods = [t.period for t in tasks[:task_idx+1]]
            max_t = tasks[task_idx].period
            return sorted({k*T for T in periods for k in range(1, int(max_t//T)+1)})
        
        # EDF: Use hyperperiod
        periods = [t.period for t in tasks]
        hyper = reduce(lcm, periods)
        return sorted({k*T for T in periods for k in range(1, hyper//T + 1)})

    def is_schedulable(task_idx, tasks, bdr, scheduler):
        """Check if task at index meets demand <= supply at all critical points"""
        time_points = get_time_points(tasks, scheduler, task_idx)
        for t in time_points:
            demand = DBF.dbf_edf(tasks, t) if scheduler == Scheduler.EDF \
                  else DBF.dbf_rm(tasks, t, task_idx)
            if demand > bdr.sbf(t):
                return False
        return True

    # Main analysis flow
    for comp in components.values():
        # 1. Calculate BDR interface and supply parameters
        comp["bdr"] = calculate_bdr(comp)
        comp["supply"] = comp["bdr"].supply_task_params()

        # 2. Check schedulability for all tasks
        tasks = comp["tasks"]
        all_schedulable = True
        
        for idx, task in enumerate(tasks):
            task.schedulable = is_schedulable(idx, tasks, comp["bdr"], comp["scheduler"])
            all_schedulable &= task.schedulable
            
        comp["schedulable"] = all_schedulable

    return components


def hierarchical_check_by_core(components):
    # Helper to mark component and tasks as unschedulable
    def mark_unschedulable(components):
        for comp in components:
            comp["schedulable"] = False
            for task in comp["tasks"]:
                task.schedulable = False

    # Group components per core
    core_map = {}
    for comp in components.values():
        core_map.setdefault(comp["core_id"], []).append(comp)

    for core_id, comps in core_map.items():
        # Create supply tasks
        supply_tasks = [
            (type('SupplyTask', (), {
                'wcet': comp["supply"][0],
                'period': comp["supply"][1],
                'deadline': comp["supply"][1],
                'priority': comp["priority"] if comp["scheduler"] == Scheduler.RM else None
            }), comp)
            for comp in comps
        ]

        # Check Theorem 1 (BDR interface compatibility)
        parent_bdr = BDR(1.0, 0.0)  # Full CPU resource
        child_bdrs = [comp["bdr"] for comp in comps]
        if not BDR.can_schedule_children(parent_bdr, child_bdrs):
            mark_unschedulable([comp for _, comp in supply_tasks])
            continue

        # Get core-level scheduler (default EDF)
        core_sched = comps[0].get('core_scheduler', Scheduler.EDF)

        # EDF: Utilization test
        if core_sched == Scheduler.EDF:
            utilization = sum(t.wcet/t.period for t, _ in supply_tasks)
            if utilization > 1.0:
                mark_unschedulable([comp for _, comp in supply_tasks])

        # RM: DBF test at deadlines
        else:
            sorted_tasks = sorted(supply_tasks, key=lambda x: x[0].priority)
            for idx, (task, comp) in enumerate(sorted_tasks):
                if DBF.dbf_rm([t[0] for t in sorted_tasks], task.period, idx) > task.period:
                    mark_unschedulable([comp])

    return components


def write_solution(components, filename="solution.csv"):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['task_name', 'component_id', 'task_schedulable', 'component_schedulable'])
        for comp_id, comp in components.items():
            comp_ok = 1 if comp['schedulable'] else 0
            for t in comp['tasks']:
                task_ok = 1 if getattr(t, 'schedulable', False) else 0
                writer.writerow([t.task_name, comp_id, task_ok, comp_ok])


def print_results(components):
    for comp_id, comp in components.items():
        print(f"Component {comp_id}: schedulable = {comp['schedulable']}")
        print(f"  BDR interface (alpha,delta) = ({comp['bdr'].rate:.4f}, {comp['bdr'].delay:.4f})")
        print(f"  Supply task (Q,P)         = ({comp['supply'][0]:.4f}, {comp['supply'][1]:.4f})")
        for t in comp['tasks']:
            print(f"    Task {t.task_name:20} schedulable = {t.schedulable}")
        print()  # Add a newline after each component
    print()


def main():
    if len(sys.argv) != 4:
        print("Usage: python analysis.py <architecture.csv> <budgets.csv> <tasks.csv>")
        sys.exit(1)

    architectures, budgets, tasks = read_csv()
    tasks = adjust_wcet(tasks, budgets, architectures)
    components = group_tasks_by_component(tasks, budgets)

    components = analyze_components(components)
    components = hierarchical_check_by_core(components)

    print_results(components)
    write_solution(components)


if __name__ == '__main__':
    main()
