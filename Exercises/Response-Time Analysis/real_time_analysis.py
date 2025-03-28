import pandas as pd


def read_csv(file):

    df = pd.read_csv(file)

    req_columns = ['Task', 'Task', 'BCET', 'WCET', 'Period', 'Deadline', 'Priority']
    if not all(col in df.columns for col in req_columns):
        print(f"Missing required column(s): {req_columns}")
        return []
    
    tasks = []
    for _, row in df.iterrows():
        task = {
            "name" : row['Task'],
            "bcet" :row['BCET'],
            "wcet" : row['Period'],
            "deadline" : row['Deadline'],
            "priority" : row['Priority']
        }
        tasks.append(task)
    
    return tasks
def real_time_analysis(jobs):

    sorted_jobs = sorted(jobs, key=lambda jobs: jobs.priority, reverse = True )
    return


def main():

    jobs = read_csv('/Users/aske/Documents/GitHub/DistributedRealTimeSystem/Exercises/Response-Time Analysis/exercise-TC1.csv')
    print(jobs)
    # real_time_analysis(jobs)
if __name__ == "__main__":
    main()  