import pandas as pd
import numpy as np


def output_result_csv(ouput_path: str, wcrt_dict: dict, tasks: np.array) -> None:
    """
    Writes the worst-case response time dictionary to a CSV file.
    Parameters:
    output_path (str): The file path to write the CSV file to.
    wcrt_dict (dict): The dictionary containing the worst-case response times for each task.
    """
    # Create a list to store the results
    results = []

    for job in tasks:
        task = job["Task"]
        wcrt = wcrt_dict[task]
        deadline = job["Deadline"]
        status = "true" if wcrt <= deadline else "false"
        results.append([task, wcrt, deadline, status])

    # Create a DataFrame from the results
    results_df = pd.DataFrame(results, columns=["Task", "WCRT", "Deadline", "Status"])

    # Save the DataFrame to a CSV file
    results_df.to_csv(ouput_path.removesuffix(".csv") + "_s.csv", index=False)
