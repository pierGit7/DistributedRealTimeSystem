import pandas as pd
import os
import sys

from common.core import Core
from common.component import Component
from common.task import Task
from common.scheduler import Scheduler
from common.utils import get_project_root

def read_cores(csv:str) -> list[Core]:
    """
    Reads the architecture information from a CSV file and returns a list of Architecture objects.
    
    Args:
        csv (str): Path to the CSV file. Can be either an absolute path or a relative path from the project root.

    Returns:
        list[Architecture]: List of Architecture objects parsed from the CSV file.
    """
    csv = _get_csv_path(csv)

    df = pd.read_csv(csv)

    architectures = []
    for _, row in df.iterrows():
        architecture = Core(
            id=row['core_id'],
            speed_factor=row['speed_factor'],
            scheduler=Scheduler[row['scheduler']]
        )
        architectures.append(architecture)

    return architectures

def read_budgets(csv:str) -> list[Component]:
    csv = _get_csv_path(csv)

    df = pd.read_csv(csv)

    budgets = []
    for _,row in df.iterrows():
        budget = Component(
            component_id=row['component_id'],
            scheduler=Scheduler[row['scheduler']],
            budget=row['budget'],
            period=row['period'],
            core_id=row['core_id'],
            priority=row['priority']
        )
        budgets.append(budget)

    return budgets

def read_tasks(csv:str) -> list[Task]:
    csv = _get_csv_path(csv)

    df = pd.read_csv(csv)

    tasks = []
    for _,row in df.iterrows():
        task = Task(
            task_name=row['task_name'],
            wcet=row['wcet'],
            period=row['period'],
            component_id=row['component_id'],
            priority=row['priority']
        )
        tasks.append(task)

    return tasks

def _get_csv_path(csv:str) -> str:
    if os.path.exists(csv):
        return csv

    csv = os.path.join(get_project_root(),csv)
    if os.path.exists(csv):
        return csv
    
    raise FileNotFoundError(
        f"File {csv} does not exist. "
        "Pass to the function an absolute path or a relative path from the project root. "
        "For example 'data/testcases/1-tiny-test-case/architecture.csv", csv
    )

def read_csv() -> tuple[list[Core], list[Component], list[Task]]:
    if len(sys.argv) != 4:
        script_name = os.path.basename(sys.argv[0])
        print(f"Usage: python {script_name} <architecture.csv> <budget.csv> <tasks.csv>")
        sys.exit(1)

    architecture_file = sys.argv[1]
    budget_file = sys.argv[2]
    tasks_file = sys.argv[3]

    try:
        architectures = read_cores(architecture_file)
        budgets = read_budgets(budget_file)
        tasks = read_tasks(tasks_file)
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing files: {e}")
        sys.exit(1)

    return architectures, budgets, tasks