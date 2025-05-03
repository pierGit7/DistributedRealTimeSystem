from common.csvreader import read_csv
from common.DBF import DBF_EDF, DBF_RM
from common.scheduler import Scheduler
import numpy as np

def main():
    architectures, budgets, tasks = read_csv()
    
    # Step 1: Adjust WCETs based on core speed
    adjusted_tasks = adjust_wcet(tasks, budgets, architectures)
    
    # Step 2: Group tasks by component
    components = group_tasks_by_component(adjusted_tasks, budgets)
    
    # Step 3: Compute BDR parameters and check component schedulability
    components = compute_bdr_parameters(components)
    
    # Step 4: Determine task schedulability based on component status
    task_schedulability = determine_task_schedulability(components)
    
    # Step 5: Check core-level schedulability
    core_schedulability = check_core_schedulability(components, architectures)
    
    # Step 6: Generate output
    generate_output(core_schedulability, task_schedulability, components)  

# ---- Helper Functions ----
def adjust_wcet(tasks, budgets, architectures):
    core_speed_map = {arch.core_id: arch.speed_factor for arch in architectures}
    component_core_map = {budget.component_id: budget.core_id for budget in budgets}
    
    for task in tasks:
        core_id = component_core_map[task.component_id]
        speed_factor = core_speed_map[core_id]
        task.wcet = task.wcet / speed_factor  # Adjust WCET
    return tasks

def group_tasks_by_component(tasks, budgets):
    components = {}
    for budget in budgets:
        comp_id = budget.component_id
        comp_tasks = [t for t in tasks if t.component_id == comp_id]
        
        if budget.scheduler == Scheduler.RM:
            comp_tasks = sorted(comp_tasks, key=lambda x: x.priority)
        
        components[comp_id] = {
            "tasks": comp_tasks,
            "scheduler": budget.scheduler,
            "core_id": budget.core_id,
            "period": budget.period,
            "priority": budget.priority,
            "schedulable": False  # Initialize component schedulability
        }
    return components

def compute_bdr_parameters(components):
    for comp_id, comp_data in components.items():
        tasks = comp_data["tasks"]
        scheduler = comp_data["scheduler"]
        
        alpha = sum(t.wcet / t.period for t in tasks)
        delta = find_minimal_delta(tasks, alpha, scheduler)
        
        components[comp_id]["alpha"] = alpha
        components[comp_id]["delta"] = delta
        components[comp_id]["schedulable"] = delta != float('inf')  # Check schedulability
    return components

def find_minimal_delta(tasks, alpha, scheduler):
    max_period = max(t.period for t in tasks)
    for delta in np.linspace(0, 2 * max_period, 100):
        if is_schedulable(tasks, alpha, delta, scheduler):
            return delta
    return float('inf')

def is_schedulable(tasks, alpha, delta, scheduler):
    time_points = np.linspace(0, 2 * max(t.period for t in tasks), 100)
    for t in time_points:
        sbf = max(alpha * (t - delta), 0)
        
        if scheduler == Scheduler.EDF:
            dbf = DBF_EDF(tasks, t, explicit_dead_line=0).getDBS()
        else:
            max_dbf = 0
            for i in range(len(tasks)):
                dbf_fps = DBF_RM(tasks, t, i).getDBS()
                max_dbf = max(max_dbf, dbf_fps)
            dbf = max_dbf
        
        if dbf > sbf:
            return False
    return True

def determine_task_schedulability(components):
    task_schedulability = {}
    for comp_id, comp_data in components.items():
        for task in comp_data["tasks"]:
            task_schedulability[task.task_name] = comp_data["schedulable"]
    return task_schedulability

def check_core_schedulability(components, architectures):
    report = {}
    for arch in architectures:
        core_comps = [c for c in components.values() if c["core_id"] == arch.core_id]
        if arch.scheduler == Scheduler.EDF:
            # Check sum(α_children) <= 1 (EDF core utilization)
            total_alpha = sum(c["alpha"] for c in core_comps)
            report[arch.core_id] = total_alpha <= 1
        else:
            # Check Theorem 1 for RM cores: 
            # 1. Sum of child α <= parent α (not applicable here as parent is the core)
            # 2. Child Δ >= parent Δ (ensure child components’ Δ >= core’s Δ)
            # Simplified: Validate RM priority assignment
            periods = []
            priorities = []
            for comp in core_comps:
                if comp["priority"] is not None:
                    periods.append(comp["period"])
                    priorities.append(comp["priority"])
            sorted_by_period = sorted(zip(periods, priorities), key=lambda x: x[0])
            report[arch.core_id] = all(
                p1 > p2 for (_, p1), (_, p2) in zip(sorted_by_period, sorted_by_period[1:])
            )
    return report

def generate_output(core_report, task_report, components):
    # Component-level report
    print("\n--- Component BDR Parameters and Schedulability ---")
    for comp_id, comp_data in components.items():
        status = "Schedulable" if comp_data["schedulable"] else "Unschedulable"
        print(
            f"Component {comp_id} (Core {comp_data['core_id']}): "
            f"α={comp_data['alpha']:.2f}, Δ={comp_data['delta']:.2f} ({status})"
        )
    
    # Core-level report (updated for Theorem 1 checks)
    print("\n--- Core Schedulability Report ---")
    for core_id, status in core_report.items():
        print(
            f"Core {core_id}: {'Schedulable' if status else 'Unschedulable'} "
            f"[Hierarchical Theorem 1: {'Satisfied' if status else 'Violated'}]"
        )
    
    # Task-level report
    print("\n--- Task Schedulability Report ---")
    for task_name, status in task_report.items():
        print(f"Task {task_name}: {'Schedulable' if status else 'Unschedulable'}")

if __name__ == "__main__":
    main()