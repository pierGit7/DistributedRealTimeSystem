import os
import pandas as pd
from Exercises.VerySimpleSimulator.src.very_simple_simulator import run_cycle


def test_exercise_1():
    run_test("ex1")


def test_exercise_2():
    run_test("ex2")


def test_exercise_3():
    run_test("ex3")


def run_test(filename: str):
    solution_file = os.path.join(get_res_path(), "solutions", f"{filename}_s.csv")

    input_file = os.path.join(get_res_path(), "files", f"{filename}.csv")
    output_file = os.path.join(get_res_path(), "files", f"{filename}_s.csv")

    run_cycle(input_file)

    output_df = pd.read_csv(output_file)
    solution_df = pd.read_csv(solution_file)

    print(f"Output dataframe shape: {output_df.shape}")
    print(f"Solution dataframe shape: {solution_df.shape}")
    if not output_df.shape == solution_df.shape:
        print("Error: dataframe shape are different")
        assert False

    print("Output dataframe:")
    print(output_df)
    print("==============================")

    print("Solution dataframe:")
    print(solution_df)
    print("==============================")
    assert output_df.equals(solution_df)


def get_root():
    """
    Get the project root
    """
    return os.path.dirname(os.path.dirname(__file__))


def get_res_path():
    """
    Get the absoulte path of the tests/res folder
    """
    return os.path.join(get_root(), "tests", "res")


def get_tmp_path():
    """
    Get the absoulte path of the tests/.tmp folder.
    If it doesn't exist it creates it
    """
    tmp_path = os.path.join(get_root(), "tests", ".tmp")
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    return tmp_path
