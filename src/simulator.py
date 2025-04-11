from common.csvreader import read_architectures

def main():
    # Example usage
    csv_path = 'data/testcases/1-tiny-test-case/architecture.csv'
    architectures = read_architectures(csv_path)
    for architecture in architectures:
        print(architecture)

    

if __name__ == "__main__":
    main()