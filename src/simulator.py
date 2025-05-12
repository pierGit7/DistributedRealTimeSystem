import random as rand
import numpy as np

from common.csvreader import read_csv
from common.component import Component
from common.scheduler import Scheduler
from common.core import Core
from common.task import Task
from common.job import Job
from common.csvoutput import TaskResult

CLOCK_TICK = 1
SIMULATION_ITERATIONS = 10
LOWER_BOUND_PERCENTAGE = 1

class Simulator:
    def __init__(self, cores:Core, components:Component, tasks:Task):
        self.cores:list[Core] = cores
        self.tasks:list[Task] = tasks
        self.components:list[Component] = components
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

        simulation_iteration = 0
        hyperperiod = self._get_hyperperiod()

        while simulation_iteration < SIMULATION_ITERATIONS:
            # Progress tracking every 10,000 iterations
            if t % 10_000 == 0:
                progress = (t % hyperperiod) / hyperperiod * 100
                print(f"Time: {t}, Progress: {progress:.2f}%")

            # --- Phase 1 Release tasks ---
            for task in self.tasks:
                if t % task.period == 0:
                    self.release_task(t, task)

            # --- Phase 2: Reset budgets ---
            for component in self.components:
                if t % component.period == 0:
                    component.remaining_budget = component.budget

            # --- Phase 3: Core-level scheduling ---
            for core in self.cores:
                eligible_components = [
                    c for c in self.components
                    if c.core_id == core.id and c.remaining_budget > 0 and len(c.jobs_queue) > 0
                ]

                if not eligible_components:
                    continue

                if core.scheduler == Scheduler.EDF:
                    next_component = min(
                        eligible_components,
                        key=lambda c: c.jobs_queue[0].absolute_deadline
                    )
                elif core.scheduler == Scheduler.RM:
                    next_component = min(eligible_components, key=lambda c: c.priority)
                else:
                    next_component = None

                job_to_run = next_component.jobs_queue[0]

                if job_to_run.remaining_time == job_to_run.execution_time:
                    job_to_run.start_time = t

                job_to_run.remaining_time -= CLOCK_TICK
                
                if job_to_run.remaining_time <= 0:
                    response_time = (t + CLOCK_TICK) - job_to_run.start_time
                    self.task_response_times[job_to_run.task_id].append(response_time)
                    self.task_deadlines[job_to_run.task_id].append(t <= job_to_run.absolute_deadline)
                    _ = next_component.jobs_queue.pop(0)
                next_component.remaining_budget -= CLOCK_TICK

            if t != 0 and t % hyperperiod == 0:
                print(f"\nIteration {simulation_iteration} completed!")
                print(f"Summary:")
                print(f"- Total time steps: {t}")
                print(f"- Hyperperiod: {hyperperiod}")
                print("-" * 50)
                simulation_iteration += 1
                t = 0
                self._clear_component_queues()
            else:
                t += CLOCK_TICK

        print("-" * 50)
        print(f"Simulation finished. Total simulation time: {t}")
        print("-" * 50)

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

    def _release_jobs_if_due(self, current_time: int):
        """
        Checks all task templates and releases new jobs if their period is met.
        Args:
            current_time: The current simulation time (t).
        """
        for task in self.tasks: # self.tasks stores Task templates
            if current_time % task.period == 0:
                # 1. Get the component for this task template
                component = next(
                    (c for c in self.components if c.id == task.component_id),
                    None
                )
                if not component:
                    raise(f"Warning: Component {task.component_id} not found for task {task.id}")

                actual_execution_time = self._generate_execution_time(task)
                new_job = Job(task, current_time, actual_execution_time)
                self._schedule(component, new_job) # Assuming _schedule_job takes (Component, Job)

    def _adjust_task_wcet(self):
        """
        Adjust the WCET of tasks based on the speed factor of the core they are assigned to.
        """
        for component in self.components:
            core = next((c for c in self.cores if c.id == component.core_id), None)
            if not core:
                continue

            for task in self.tasks:
                if task.component_id != component.id:
                    continue

                # Adjust WCET based on the speed factor of the core
                task.wcet = task.wcet / core.speed_factor
                task.remaining_time = task.wcet

    def _clear_component_queues(self):
        """
        Clear the task queues of all components.
        """
        for component in self.components:
            component.jobs_queue.clear()
            component.remaining_budget = component.budget

    def _generate_execution_time(self, task:Task):
        """
        Generate execution time for each task based on its WCET and the speed factor of the core.
        """
        # Avionics (DO-178C): Typically ≥80% to ensure strict deadline guarantees.
        lower_bound = task.wcet * LOWER_BOUND_PERCENTAGE
        return self._generate_normal_exec_time(lower_bound, task.wcet)

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
            len(component.jobs_queue) == 0
            for component in self.components
            if component.core_id == core_id
        )

    def release_task(self, t: int, task: Task):
        """Releases a single task if its period is met."""
        component = next(c for c in self.components if c.id == task.component_id)
        existing_job = next(
            (j for j in component.jobs_queue if j.task_id == task.id),
            None
        )
        if existing_job:
            self.task_deadlines[task.id].append(
                t <= existing_job.absolute_deadline and
                existing_job.remaining_time <= 0
            )
            
        execution_time = self._generate_execution_time(task)
        job = Job(task, t, execution_time)
        job.release_time = t
        # component = next(c for c in self.components if c.id == task.component_id) # Already found
        self._schedule(t, component, job)

    def _schedule(self, current_time: int, component: Component, job: Job):
        """
        Schedule the tasks for a given component based on its scheduling policy.
        First removes any existing instance of the task from queue before scheduling new instance.

        Args:
            current_time: Current simulation time
            component: The component whose tasks are to be scheduled
            task: Task to be scheduled
        """
        # Remove existing instance of task if present
        component.jobs_queue = [j for j in component.jobs_queue if j.task_id != job.task_id]

        insert_idx = 0
        match component.scheduler:
            case Scheduler.RM:
                # Rate Monotonic: Insert based on priority (lower value = higher priority)
                for idx, queue_job in enumerate(component.jobs_queue):
                    if job.priority > queue_job.priority:
                        insert_idx = idx + 1
            case Scheduler.EDF:
                deadline_new = job.absolute_deadline
                
                insert_idx = 0
                for idx, queue_job in enumerate(component.jobs_queue):
                    deadline_queued = queue_job.absolute_deadline
                    if deadline_new > deadline_queued:
                        insert_idx = idx + 1
            case _:
                raise ValueError(f"Unknown scheduling policy: {component.scheduler}")

        component.jobs_queue.insert(insert_idx, job)

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

    def _get_hyperperiod(self):
        """Calculate the system hyperperiod hierarchically.
        First calculates the hyperperiod (LCM) of tasks within each component,
        then calculates the LCM of all component hyperperiods.

        Example:
            Component1 has tasks with periods [2,3]  -> LCM = 6
            Component2 has tasks with periods [2,4]  -> LCM = 4
            System hyperperiod = LCM(6,4) = 12

        Returns:
            int: The hyperperiod value for the entire system
        """
        # Calculate hyperperiod for each component
        component_hyperperiods = []
        for component in self.components:
            # Get all tasks for this component
            component_tasks = [task for task in self.tasks if task.component_id == component.id]
            if not component_tasks:
                # If component has no tasks, use its own period
                component_hyperperiods.append(component.period)
                continue

            # Calculate LCM of task periods within this component
            task_periods = [task.period for task in component_tasks]
            component_lcm = task_periods[0]
            for period in task_periods[1:]:
                component_lcm = (component_lcm * period) // np.gcd(component_lcm, period)
            component_hyperperiods.append(component_lcm)

        # Calculate system hyperperiod as LCM of component hyperperiods
        system_hyperperiod = component_hyperperiods[0]
        for period in component_hyperperiods[1:]:
            system_hyperperiod = (system_hyperperiod * period) // np.gcd(system_hyperperiod, period)

        return system_hyperperiod

def main():
    cores, components, tasks = read_csv()

    simulator = Simulator(cores, components, tasks)
    simulator.run()

    simulator.generate_output_file("simulation_solution.csv")

if __name__ == "__main__":
    main()