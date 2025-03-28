import pandas as pd
import math


def read_csv(file):
    """
    Read tasks from a CSV file and convert to a list of task dictionaries.
    """
    df = pd.read_csv(file)
    req_columns = ['Task', 'BCET', 'WCET', 'Period', 'Deadline', 'Priority']

    if not all(col in df.columns for col in req_columns):
        raise ValueError(f"Missing required column(s): {req_columns}")

    tasks = []
    for _, row in df.iterrows():
        task = {
            "name": row['Task'],
            "bcet": row['BCET'],
            "wcet": row['WCET'],
            "period": row['Period'],
            "deadline": row['Deadline'],
            "priority": row['Priority']
        }
        tasks.append(task)

    return tasks


def response_time_analysis(tasks):
    """
    Perform Response-Time Analysis.
    """
    # Sort tasks by priority (lower number means higher priority)
    sorted_tasks = sorted(tasks, key=lambda x: x['priority'])

    results = []

    for i, task in enumerate(sorted_tasks):
        R = task['wcet']  # Initial response time
        last_R = -1
        schedulable = True

        while R != last_R:
            last_R = R
            interference = 0

            # Calculate interference from higher-priority tasks
            for j in range(i):
                higher_task = sorted_tasks[j]
                interference += math.ceil(R / higher_task['period']) * higher_task['wcet']

            R = task['wcet'] + interference

            # Check if the task is schedulable
            if R > task['deadline']:
                schedulable = False
                break

        # Store results
        result = {
            'Task': task['name'],
            'WCRT': R,
            'Deadline': task['deadline'],
            'Status': 'Schedulable' if schedulable else 'Not Schedulable'
        }
        results.append(result)

    return results


def run_rta(path_file):
    """
    Main function to read tasks and perform response time analysis.
    """
    # Read tasks from CSV
    tasks = read_csv(path_file)
    print(tasks)
    # Perform response time analysis
    analysis_results = response_time_analysis(tasks)

    # Print results
    for result in analysis_results:
        if result['Status'] == 'Schedulable':
            print(f"Task {result['Task']} is schedulable with WCRT = {result['WCRT']:.1f}")
        else:
            print(f"Task {result['Task']} is not schedulable with WCRT.")
    return analysis_results
