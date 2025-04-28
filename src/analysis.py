from common.csvreader import read_architectures, read_budgets, read_tasks


def main():
    # Example usage
    csv_path = 'data/testcases/1-tiny-test-case/architecture.csv'
    architectures = read_architectures(csv_path)
    for architecture in architectures:
        print(architecture)
    csv_path = 'data/testcases/1-tiny-test-case/budgets.csv'
    budgets = read_budgets(csv_path)
    for budget in budgets:
        print(budget)
    csv_path = 'data/testcases/1-tiny-test-case/tasks.csv'
    tasks = read_tasks(csv_path)
    for task in tasks:
        print(task)
        
if __name__ == "__main__":
    main()