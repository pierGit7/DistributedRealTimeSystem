import sys
from pathlib import Path

from src.simulator import Simulator
from src.common.csvreader import read_cores, read_budgets, read_tasks

def test_simulator_tiny_case():
    cores = read_cores("data/testcases/1-tiny-test-case/architecture.csv")
    budgets = read_budgets("data/testcases/1-tiny-test-case/budgets.csv")
    tasks = read_tasks("data/testcases/1-tiny-test-case/tasks.csv")
    
    # Initialize simulator
    simulator = Simulator(cores, budgets, tasks)
    
    # Run simulation
    simulator.run()
    
    # Get results
    results = simulator.get_task_results()
    
    # Assert expected values
    # These values should match your tiny test case expected outcomes
    assert len(results) > 0
    # Example assertions (adjust according to your actual test data):
    

 