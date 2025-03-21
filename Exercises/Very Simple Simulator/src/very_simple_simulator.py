import pandas as pd
import numpy as np
from dataclasses import dataclass


# struct to keep track of the jobs
@dataclass
class Jobs:
    task: np.array
    release_time: int
    remaining_time: int
    response_time: int


# function to read the file
def read_file(path: str) -> pd.DataFrame:
    """
    Reads a CSV file from the specified path and returns its contents as a pandas DataFrame.
    Parameters:
    path (str): The file path to the CSV file.
    Returns:
    pd.DataFrame: The contents of the CSV file as a pandas DataFrame.
    """
    return pd.read_csv(path)


# function to check if every job is done
def check_remaining_jobs(jobs: np.array) -> bool:
    """
    Checks if there are any jobs remaining to be executed.
    Parameters:
    jobs (np.array): The list of jobs to check.
    Returns:
    bool: True if there are jobs remaining, False otherwise.
    """
    for job in jobs:
        if job.remaining_time > 0:
            return True
    return False


# function to check if the job is ready to be executed
def get_ready_list(jobs: np.array, current_time: int) -> np.array:
    ready_job: np.array = []
    for job in jobs:
        if job.release_time <= current_time and job.remaining_time > 0:
            ready_job.append(job)
    return ready_job


def run_cycle(input_path: str) -> None:
    # Print the contents of the CSV file
    # Task  BCET(best case execution time)  WCET(worst case execution time)  Period  Deadline  Priority
    df = read_file(input_path).values

    # init number of cycles and current time
    num_cycles: int = 1000
    current_time: int = 0

    # init the jobs
    jobs: np.array = []
    for i in range(len(df)):
        jobs.append(Jobs(df[i], 0, df[i, 2], 0))

    jobs_queue = jobs.copy()

    # init the worst case dictionary
    wcrt_dict = {jobs[i].task[0]: 0 for i in range(len(jobs))}

    while current_time <= num_cycles and check_remaining_jobs(jobs_queue):
        # release job at the start of the period
        for job in jobs:
            if current_time % job.task[3] == 0 and current_time != 0:
                jobs_queue.append(Jobs(job.task, current_time, job.task[2], 0))

        ready_job = get_ready_list(jobs_queue, current_time)
        highest_priority_job = None
        if ready_job:
            highest_priority_job = max(ready_job, key=lambda job: job.task[5])

        if highest_priority_job:
            # advace by 1
            current_time += 1
            # compute the task
            highest_priority_job.remaining_time -= 1
            # check if the task is done
            if highest_priority_job.remaining_time <= 0:
                highest_priority_job.response_time = (
                    current_time - highest_priority_job.release_time
                )
                wcrt_dict[highest_priority_job.task[0]] = max(
                    wcrt_dict[highest_priority_job.task[0]],
                    highest_priority_job.response_time,
                )
        else:
            current_time += 1
    # Create a list to store the results
    results = []

    for job in jobs:
        task = job.task[0]
        wcrt = wcrt_dict[task]
        deadline = job.task[4]
        status = "true" if wcrt <= deadline else "false"
        results.append([task, wcrt, deadline, status])

    # Create a DataFrame from the results
    results_df = pd.DataFrame(results, columns=["Task", "WCRT", "Deadline", "Status"])

    # Save the DataFrame to a CSV file
    results_df.to_csv(input_path.removesuffix(".csv") + "_s.csv", index=False)


if __name__ == "__main__":
    run_cycle(
        "/Users/pierfrancesco/Desktop/second semester DTU/distributed/repo/Exercises/Very Simple Simulator/exercise-TC1.csv"
    )
