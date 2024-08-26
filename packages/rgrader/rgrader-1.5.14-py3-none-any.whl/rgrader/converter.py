import re
import unittest
from typing import Type
from unittest import TestCase

from .decorators import add_points, run_solution

EXACT_REDUCTION = 0.3


class WrongStructure(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


def equals_assert_func_generator(name: str, inputs: list[str], exp_output: str, points: str, test_msg: str):
    """
    Generates function that compares whole string output with tested output
    """
    try:

        exp_output = exp_output.replace('[', '')
        exp_output = exp_output.replace(']', '')

        @add_points(float(points))
        @run_solution(inputs)
        def testing_func(self, output: list[str]):
            self.assertEqual(output, exp_output, test_msg)

        testing_func.__name__ = name

        return testing_func
    except ValueError as e:
        print(e, "'points' must be a number with floating point")


def contains_assert_func_generator(name: str, inputs: list[str], exp_output: str, points: str, test_msg: str):
    """
    Generates function that tests if required data are contained in every line
    """
    try:
        @add_points(float(points))
        @run_solution(inputs)
        def testing_func(self, output: str):

            output_lines = output.split("\n")
            expected_lines = exp_output.split("\n")

            for i, expected_line in enumerate(expected_lines):
                if len(output_lines) < i:
                    self.fail(f"Lines count doesn't match expected: {len(expected_lines)}, got {len(output_lines)}")

                expected_contains = re.findall("\\[(.*?)\\]", expected_line)

                for expected_contain in expected_contains:
                    self.assertIn(expected_contain, output_lines[i])

        testing_func.__name__ = name

        return testing_func
    except ValueError as e:
        print(e, "'points' must be a number with floating point")


def txt_to_func(test_file: str) -> dict:
    with open(test_file, "r", encoding="utf-8") as file:

        func_dict = {}
        file = file.read()

        # handle wrong test file structure
        input_lines = file.count("INPUT")
        output_lines = file.count("OUTPUT")
        cases_num = file.count("# test_")

        if input_lines != output_lines or output_lines != cases_num or input_lines != cases_num:
            raise WrongStructure(
                "Each test case should look like:\n# test_<name> <points>\n\
<optional test comment>\nINPUT\n<input per line>\nOUTPUT\n<output per line>")

        test_cases = filter(lambda x: bool(x), file.split("# "))

        for test in test_cases:
            test = test.strip().split("\n")

            if len(test) < 3:
                raise WrongStructure("Not enough elements in test case")

            if " " in test[0]:
                name, points = test[0].split(" ")
            else:
                name, points = test[0], 0

            if test[1] != "INPUT" and test[2] != "INPUT":
                raise WrongStructure(
                    f"INPUT goes right after test's name. It should look like:\n# {name} {points}\nINPUT")

            test_msg = ""
            if test[2] == "INPUT":
                test_msg = test[1]

            inputs_start = test.index("INPUT")

            if "OUTPUT" not in test:
                raise WrongStructure(f"No OUTPUT for {name}.")

            output_start = test.index("OUTPUT")

            if output_start - inputs_start == 1:
                raise WrongStructure(f"No inputs are given for {name}.")

            inputs = test[inputs_start + 1:output_start]
            outputs = "\n".join(test[output_start + 1:])

            points = float(points)

            if re.search("\\[(.*?)\\]", outputs):
                func_dict[f"{name}_contains"] = contains_assert_func_generator(f"{name}_contains", inputs, outputs, points - EXACT_REDUCTION, test_msg)
                func_dict[name] = equals_assert_func_generator(name, inputs, outputs, EXACT_REDUCTION, test_msg)
            else:
                func_dict[name] = equals_assert_func_generator(name, inputs, outputs, points, test_msg)

        return func_dict


def create_unittest(test_file: str) -> Type[TestCase]:
    return type("tests", (unittest.TestCase,), txt_to_func(test_file))
