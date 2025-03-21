from dataclasses import dataclass
import numpy as np


# struct to keep track of the jobs
@dataclass
class Jobs:
    task: np.array
    release_time: int
    remaining_time: int
    response_time: int


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
    """
    Get the list of jobs that are ready to be executed.
    Args:
        jobs (np.array): An array of job objects. Each job object is expected to have 'release_time' and 'remaining_time' attributes.
        current_time (int): The current time against which the jobs' readiness is evaluated.
    Returns:
        np.array: An array of job objects that are ready to be executed. A job is considered ready if its release_time is less than or equal to the current_time and its remaining_time is greater than 0.
    """
    ready_job: np.array = []
    for job in jobs:
        if job.release_time <= current_time and job.remaining_time > 0:
            ready_job.append(job)
    return ready_job
