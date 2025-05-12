import csv
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class TaskResult:
    task_name: str
    component_id: str
    task_schedulable: bool
    avg_response_time: float
    max_response_time: float
    component_schedulable: bool

class CSVOutput:
    def __init__(self, filename: str):
        self.filename = filename
        self.headers = [
            'task_name',
            'component_id',
            'task_schedulable',
            'avg_response_time',
            'max_response_time',
            'component_schedulable'
        ]
        self.results: List[TaskResult] = []

    def add_task_result(self, result: TaskResult) -> None:
        """Add a single task result to the collection."""
        self.results.append(result)

    def add_multiple_results(self, results: List[TaskResult]) -> None:
        """Add multiple task results at once."""
        self.results.extend(results)

    def write_results(self) -> None:
        """Write all results to the CSV file."""
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    'task_name': result.task_name,
                    'component_id': result.component_id,
                    'task_schedulable': 1 if result.task_schedulable else 0,
                    'avg_response_time': result.avg_response_time,
                    'max_response_time': result.max_response_time,
                    'component_schedulable': 1 if result.component_schedulable else 0
                })

    def clear_results(self) -> None:
        """Clear all stored results."""
        self.results.clear()