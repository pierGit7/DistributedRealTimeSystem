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
    Perform precise Response-Time Analysis following the algorithm exactly.
    """
    # Sort tasks by priority (highest priority first) for analysis
    sorted_tasks = sorted(tasks, key=lambda x: x['priority'], reverse=True)

    results = []

    for i, task in enumerate(sorted_tasks):
        Ci = task['wcet']  # Worst-case execution time
        Di = task['deadline']  # Deadline

        # Initial response timess
        Ri = Ci

        while True:
            # Calculate interference from higher priority tasks
            interference = 0
            for j in range(i):
                higher_task = sorted_tasks[j]
                interference += math.ceil(Ri / higher_task['period']) * higher_task['wcet']

            # New response time calculation
            new_Ri = Ci + interference

            # Convergence check
            if new_Ri == Ri:
                break

            Ri = new_Ri

            # Schedulability check
            if Ri > Di:
                break

        # Determine schedulability
        schedulable = Ri <= Di

        # Store results
        result = {
            'Task': task['name'],
            'WCRT': Ri,
            'Deadline': Di,
            'Status': '✓' if schedulable else '✗'
        }
        results.append(result)

    # Sort results by task name to get T1, T2, ... order
    return sorted(results, key=lambda x: x['Task'])


def main():
    """
    Main function to read tasks and perform response time analysis.
    """
    # Read tasks from CSV
    tasks = read_csv(
        '/Users/aske/PycharmProjects/DistributedRealTimeSystem/Exercises/Response-Time Analysis/exercise-TC1.csv')

    # Perform response time analysis
    analysis_results = response_time_analysis(tasks)

    # Print results in a formatted table
    print("----  ----  --------  ------")
    for result in analysis_results:
        print(f"{result['Task']:4} {result['WCRT']:5.1f}     {result['Deadline']:3}      {result['Status']}")
    print("----  ----  --------  ------")


if __name__ == "__main__":
    main()