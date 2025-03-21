import pandas as pd
import numpy as np
from jobs import Jobs, check_remaining_jobs, get_ready_list
from task_handler import output_result_csv


def run_cycle(input_path: str) -> None:
    # Print the contents of the CSV file
    # Task  BCET(best case execution time)  WCET(worst case execution time)  Period  Deadline  Priority
    tasks = pd.read_csv(input_path)
    tasks_dict = tasks.to_dict(orient="records")

    # init number of cycles and current time
    num_cycles: int = 1000
    current_time: int = 0

    # init the tasks
    jobs_queue: np.array = []
    for task in tasks_dict:
        jobs_queue.append(Jobs(task, 0, task["WCET"], 0))

    # init the worst case dictionary example[T0, 0; T1,0; ...]
    # wcrt_dict = {tasks.values[i][0]: 0 for i in range(len(tasks))}
    wcrt_dict = {task: 0 for task in tasks["Task"]}

    while current_time <= num_cycles and check_remaining_jobs(jobs_queue):
        # release job at the start of the period
        for task in tasks_dict:
            if current_time % task["Period"] == 0 and current_time != 0:
                jobs_queue.append(Jobs(task, current_time, task["WCET"], 0))

        ready_job = get_ready_list(jobs_queue, current_time)
        highest_priority_job = None
        if ready_job:
            highest_priority_job = min(ready_job, key=lambda job: job.task["Priority"])

        if highest_priority_job:
            # advance by 1
            current_time += 1
            # compute the task
            highest_priority_job.remaining_time -= 1
            # check if the task is done
            if highest_priority_job.remaining_time <= 0:
                highest_priority_job.response_time = (
                    current_time - highest_priority_job.release_time
                )
                wcrt_dict[highest_priority_job.task["Task"]] = max(
                    wcrt_dict[highest_priority_job.task["Task"]],
                    highest_priority_job.response_time,
                )
                for i, job in enumerate(jobs_queue):
                    if job.task["Priority"] == highest_priority_job.task["Priority"]:
                        jobs_queue.pop(i)
                        break
        else:
            current_time += 1

    output_result_csv(input_path, wcrt_dict, tasks_dict)


if __name__ == "__main__":
    run_cycle(
        "/Users/pierfrancesco/Desktop/second semester DTU/distributed/repo/Exercises/Very Simple Simulator/exercise-TC1.csv"
    )
