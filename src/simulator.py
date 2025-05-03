import random as rand
import numpy as np

from common.csvreader import read_cores
from common.csvreader import read_budgets
from common.csvreader import read_tasks
from common.component import Component
from common.scheduler import Scheduler
from common.core import Core
from common.task import Task
from common.csvoutput import TaskResult

CLOCK_TICK = 1
SIMULATION_ITERATIONS = 100
LOWER_BOUND_PERCENTAGE = 1

class Simulator:
    def __init__(self, cores:Core, components:Component, tasks:Task):
        self.cores:list[Core] = cores
        self.tasks:list[Task] = tasks
        self.components:list[Component] = components
        self._fill_component_task_queues()
        self._adjust_task_wcet()

        self.task_start_times: dict[str, float] = {}  # task_id -> start time
        self.task_response_times: dict[str, list[float]] = {}  # task_id -> list of response times
        self.task_deadlines: dict[str, list[bool]] = {}  # task_id -> list of deadline met flags

        for task in self.tasks:
            self.task_start_times[task.id] = 0
            self.task_response_times[task.id] = []
            self.task_deadlines[task.id] = []

    def run(self):
        print("Running simulation...")

        t = 0  # Simulation time in us
        
        # Initialize response time tracking
        for task in self.tasks:
            self.task_response_times[task.id] = []
            self.task_deadlines[task.id] = []

        self._generate_execution_time()
        simulation_iteration = 0

        while simulation_iteration < SIMULATION_ITERATIONS:            
            print(f"\nTime step: {t}")
            terminated = True
            
            # --- Phase 1: Reset budgets for components whose period renews at time `t` ---
            for component in self.components:
                if t % component.period == 0:
                    print(f"Replenishing budget for component {component.id} to {component.budget}")
                    component.remaining_budget = component.budget  # Replenish

            # --- Phase 2: Core-level scheduling (pick which component runs) ---
            for core in self.cores:
                if self._is_core_empty(core.id):
                    print(f"Core {core.id} has no more assigned task, skipping...")
                    continue

                terminated = False

                print(f"\nScheduling for Core {core.id}:")

                
                # Get components assigned to this core with remaining budget
                eligible_components = [
                    c for c in self.components 
                    if c.core_id == core.id and c.remaining_budget > 0 and len(c.task_queue) > 0
                ]
                print(f"Eligible components: {[c.id for c in eligible_components]}")
                if not eligible_components:
                    print(f"No eligible components for Core {core.id}, skipping...")
                    continue


                if core.scheduler == Scheduler.EDF:
                    next_component = min(eligible_components, key=lambda c: c.period)  # Earliest deadline
                elif core.scheduler == Scheduler.RM:
                    next_component = min(eligible_components, key=lambda c: c.priority)  # Highest priority
                else:
                    next_component = None  # No valid scheduler found
                
                print(f"Selected component {next_component.id} for execution")
                task_to_run = next_component.task_queue[0]  # Get highest-priority task without removing
                print(f"Running task {task_to_run.id}, remaining time: {task_to_run.remaining_time}")
                
                # Track start time when task begins
                if task_to_run.remaining_time == task_to_run.wcet:
                    self.task_start_times[task_to_run.id] = t

                task_to_run.remaining_time -= CLOCK_TICK  # Simulate task execution
                if task_to_run.remaining_time <= 0:
                    # Task completed, remove it from the queue
                    response_time = t - self.task_start_times[task_to_run.id]
                    if response_time == 0:
                        response_time = CLOCK_TICK
                    
                    self.task_response_times[task_to_run.id].append(response_time)
                    
                    # Check if completed within period/deadline
                    deadline_met = t <= task_to_run.period
                    self.task_deadlines[task_to_run.id].append(deadline_met)
                    
                    _ = next_component.task_queue.pop(0) # Pop from the head of the queue
                next_component.remaining_budget -= CLOCK_TICK  # Consume budget

            if terminated:
                print("---------------------------------------------------------")
                print("Iteration ", simulation_iteration, " terminated!")
                print("---------------------------------------------------------")
                simulation_iteration += 1
                t = 0
                self._generate_execution_time()
                self._fill_component_task_queues()
            else:
                t += CLOCK_TICK

        print("---------------------------------------------------------")
        print("Simulation finished. Simulation time:", t)
        print("---------------------------------------------------------")

    def generate_output_file(self, filename: str):
        """Generate a CSV output file with task simulation results.
            
        Args:
            filename: Path to the output CSV file
        """
        task_results = self.get_task_results()
        
        # Create CSV file
        with open(filename, 'w') as f:
            # Write header
            f.write("Task,Component,Task Schedulable,Avg Response Time,Max Response Time,Component Schedulable\n")
            
            # Write data for each task
            for result in task_results:
                f.write(f"{result.task_name},{result.component_id},{result.task_schedulable},"
                        f"{result.avg_response_time:.2f},{result.max_response_time:.2f},"
                        f"{result.component_schedulable}\n")
        
    def _fill_component_task_queues(self):
        for component in self.components:
            # Get tasks assigned to this component
            tasks_for_component = [
                task for task in self.tasks if task.component_id == component.id
            ]
            
            if component.scheduler == "RM":
                tasks_for_component.sort(key=lambda t: t.priority)
            else:
                tasks_for_component.sort(key=lambda t: t.period)

            component.task_queue = tasks_for_component

    def _adjust_task_wcet(self):
        """
        Adjust the WCET of tasks based on the speed factor of the core they are assigned to.
        """
        for component in self.components:
            core = next((c for c in self.cores if c.id == component.core_id), None)
            if not core:
                continue

            for task in component.task_queue:
                task.wcet = task.wcet / core.speed_factor
                task.remaining_time = task.wcet

    def _generate_execution_time(self):
        """
        Generate execution time for each task based on its WCET and the speed factor of the core.
        """
        for task in self.tasks:
            # Avionics (DO-178C): Typically ≥80% to ensure strict deadline guarantees.
            lower_bound = task.wcet * LOWER_BOUND_PERCENTAGE
            task.remaining_time = self._generate_normal_exec_time(lower_bound, task.wcet)

    def _generate_normal_exec_time(self,lower_bound, wcet):
        """
        Generate execution time following a normal distribution bounded between WCET and lower_bound.

        The function uses a normal distribution with:
        - mean: average of WCET and lower_bound ((wcet + lower_bound)/2)
        - standard deviation: (wcet - lower_bound)/6 to ensure ~99.7% of values fall within ±3σ

        The while loop ensures the generated execution time stays within the specified bounds
        by rejecting and regenerating values that fall outside [lower_bound, wcet].

        Parameters
        ----------
        wcet : float
            Worst Case Execution Time - upper bound for execution time
        lower_bound : float
            Minimum possible execution time - lower bound

        Returns
        -------
        float
            A randomly generated execution time that follows a normal distribution
            and falls between lower_bound and wcet inclusive

        Notes
        -----
        - Using (wcet - lower_bound)/6 as std dev ensures most values (~99.7%) 
          fall within the desired range, minimizing rejections in the while loop
        - The distribution is symmetrical around the mean, creating a bell curve
          between lower_bound and wcet
        """
        mean = (wcet + lower_bound) / 2
        std_dev = (wcet - lower_bound) / 6
        while True:  # Ensure value stays within bounds
            exec_time = np.random.normal(mean, std_dev)
            if lower_bound <= exec_time <= wcet:
                return exec_time    

    def _is_core_empty(self, core_id):
        """
        Check if all components assigned to the specified core have empty task queues.
        
        Args:
            core_id: The ID of the core to check
            
        Returns:
            bool: True if no tasks remain for any component on this core, False otherwise
        """
        return all(
            len(component.task_queue) == 0
            for component in self.components 
            if component.core_id == core_id
        )

    def get_task_results(self) -> list[TaskResult]:
        """Get the simulation results for all tasks.
        
        Returns:
            List[TaskResult]: Results for each task including response times and schedulability.
        """
        results = []
        for task in self.tasks:
            response_times = self.task_response_times.get(task.id, [])
            deadline_flags = self.task_deadlines.get(task.id, [])
            
            if response_times:
                avg_response = sum(response_times) / len(response_times)
                max_response = max(response_times)
                # Task is schedulable only if ALL instances met their deadlines
                task_schedulable = all(deadline_flags)
            else:
                avg_response = 0.0
                max_response = 0.0
                task_schedulable = False
            
            # Get component for this task
            component = next(c for c in self.components if c.id == task.component_id)
            
            # A component is schedulable if all its tasks are schedulable
            component_tasks = [t for t in self.tasks if t.component_id == component.id]
            component_schedulable = all(
                all(self.task_deadlines.get(t.id, [])) 
                for t in component_tasks
            )
            
            results.append(TaskResult(
                task_name=task.id,
                component_id=task.component_id,
                task_schedulable=task_schedulable,
                avg_response_time=avg_response,
                max_response_time=max_response,
                component_schedulable=component_schedulable
            ))
        
        return results

def main():
    # Base path for test case files
    base_path = 'data/testcases/7-unschedulable-test-case'
    
    # Read architectures
    architecture_path = f'{base_path}/architecture.csv'
    cores = read_cores(architecture_path)
    print("Architectures:")
    for core in cores:
        print(core)
    
    # Read tasks
    tasks_path = f'{base_path}/tasks.csv'
    tasks = read_tasks(tasks_path)
    print("\nTasks:")
    for task in tasks:
        print(task)
    
    # Read components
    budgets_path = f'{base_path}/budgets.csv'
    components = read_budgets(budgets_path)
    print("\nBudgets:")
    for component in components:
        print(component)

    simulator = Simulator(cores, components, tasks)
    simulator.run()

    simulator.generate_output_file("output.csv")

if __name__ == "__main__":
    main()