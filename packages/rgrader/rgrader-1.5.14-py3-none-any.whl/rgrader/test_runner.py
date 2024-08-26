import argparse
import doctest
import importlib.util
import inspect
import os
import unittest
from typing import Type
from unittest import TestLoader, TestSuite, TextTestRunner

from pylint.lint import Run
from pylint.reporters.text import TextReporter
from six import StringIO

from .converter import create_unittest
from .globals import get_testing_script_path, set_testing_script_path
from .utils import map_pylint_arguments

PYLINT_WEIGHT = .25


class GraderTestResult(unittest.TextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_points = None
        self.gained_points = None

        self.output = None


class GraderTestRunner(TextTestRunner):
    """Test runner that counts points for each successful test case."""

    def __init__(self, *args, pylint_args=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.pylint_args = pylint_args

    def run_pylint(self) -> tuple[str, float]:
        """
        Run's pylint and returns how many points gained on scale from 0 to 1.
        """
        pylint_output = StringIO()
        reporter = TextReporter(pylint_output)
        Run(args=self.pylint_args + [get_testing_script_path()], reporter=reporter, exit=False)

        lint_message = pylint_output.getvalue()

        pep8_grade = 0
        for line in lint_message.splitlines():
            if "rated at" in line:
                try:
                    pep8_grade = float(line.split(" ")[6].split("/10")[0]) / 10
                    pep8_grade = pep8_grade if pep8_grade >= 0 else 0

                except:
                    pep8_grade = 0

        return lint_message, pep8_grade

    def check_doctests(self, module_path: str) -> tuple[str, bool]:
        """
        Checks whether each function has at least one doctest. Runs all doctests.
        """

        module_name = os.path.splitext(os.path.basename(module_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        functions = inspect.getmembers(module, inspect.isfunction)

        missed_doctests = []
        for name, func in functions:

            finder = doctest.DocTestFinder()
            tests = finder.find(func)

            if len(tests) == 0 or len(tests[0].examples) == 0:
                missed_doctests.append(name)

        result = doctest.testmod(module)

        doctest_message = []
        verdict = True

        if len(missed_doctests) > 0:
            doctest_message.append(f"Following functions miss doctests: {', '.join(missed_doctests)}")
            verdict = False

        if result.failed != 0:
            doctest_message.append(f"TestResults({result.failed=}, {result.attempted=})")
            verdict = False

        return "\n".join(doctest_message), verdict

    def run(self, test_suite: TestSuite) -> GraderTestResult:
        """Run tests and count total grade"""

        test_cases = self._discover_test_cases(test_suite)

        pylint_check = False
        doctests_check = False
        for case in test_cases:
            if hasattr(case, "pylint_check") and case.pylint_check:
                pylint_check = True
            if hasattr(case, "doctests_check") and case.doctests_check:
                doctests_check = True

        self.stream.writeln(f"=== Running tests for: {get_testing_script_path()} ===")

        if os.path.exists(get_testing_script_path()):
            result = super().run(test_suite)
            self.show_points(test_cases, result)
            doctest_dependent_points = result.gained_points * (1 - PYLINT_WEIGHT)
            pylint_dependent_points = result.gained_points - doctest_dependent_points

            if pylint_check:
                lint_message, pep8_grade = self.run_pylint()

                pylint_dependent_points *= pep8_grade

                self.stream.writeln(lint_message)

            if doctests_check:
                doctest_message, verdict = self.check_doctests(get_testing_script_path())
                if not verdict:
                    self.stream.writeln(doctest_message)
                    doctest_dependent_points /= 2

            result.gained_points = pylint_dependent_points + doctest_dependent_points
            self.stream.writeln(f"Grade: {result.gained_points}/{result.total_points}")
        else:
            result = GraderTestResult(stream=self.stream, descriptions="", verbosity=0)
            self.show_points(test_cases, result)
            result.gained_points = 0
            self.stream.writeln(f"File '{get_testing_script_path()}' was not found")

        self.stream.seek(0)
        result.output = self.stream.read()

        return result

    def show_points(self, test_cases: list[Type], result: GraderTestResult) -> None:
        """
        Count and print gained points
        Args:
            test_case: class of testcase, we must pass it because, after running tests
            it is very hard to find TestCase class
            result: Test result of the TestCase
        """

        all_methods = [method
                       for test_case in test_cases
                       for name, method in inspect.getmembers(test_case)
                       if name.startswith("test_")]

        failed_methods_names = [method._testMethodName for method, _ in result.failures] + \
                               [method._testMethodName for method, _ in result.errors]
        succeeded_methods = [method for method in all_methods if method.__name__ not in failed_methods_names]

        total_points = sum(getattr(method, "points_increment") for method in all_methods)
        gained_points = sum(getattr(method, "points_increment") for method in succeeded_methods)

        result.total_points = total_points
        result.gained_points = gained_points

    @staticmethod
    def _discover_test_cases(test_suite: TestSuite) -> set:
        """Get all TestCase classes from a TestSuite
        Args:

            test_suite: suite where to search for TestCase classes
        """
        discovered_test_cases = set()

        nodes_to_discover = [test_suite]
        while nodes_to_discover:
            node = nodes_to_discover.pop()

            for test in node._tests:
                if isinstance(test, TestSuite):
                    nodes_to_discover.append(test)
                else:
                    discovered_test_cases.add(test.__class__)

        return discovered_test_cases


def load_python_tests(test_file_path: str) -> TestSuite:
    """Load test suite from file by path

    Args:
        test_file_path: path to the test script

    """
    directory_path = os.path.dirname(test_file_path)
    test_file_name = os.path.basename(test_file_path)

    loader = TestLoader().discover(start_dir=directory_path, top_level_dir=directory_path,
                                   pattern=test_file_name)
    return loader


def load_tests(test_script_path: str) -> TestSuite:
    """Load test suite from python or .tests file"""

    if test_script_path.endswith(".py"):
        suite = load_python_tests(test_script_path)
    elif test_script_path.endswith(".tests"):
        suite = TestLoader().loadTestsFromTestCase(create_unittest(test_script_path))
    else:
        raise TypeError("Invalid test file extension")

    return suite


def run_tests_setup_argparse(argument_parser: argparse.ArgumentParser) -> None:
    """Add necessary arguments to argparse"""
    argument_parser.add_argument("-t", "--tests", help="Path to the test script")
    argument_parser.add_argument("-s", "--solution", help="Path to the solution")
    argument_parser.add_argument("-p", "--pylint-args", help="Arguments for pylint", required=False, default="")


def run_tests_for(script_path: str, test_script_path: str = None, suite: TestSuite = None,
                  pylint_args=None) -> GraderTestResult:
    """
    Run tests for given script with test_script_path
    :param script_path:
    :param test_script_path:
    :param suite:
    :param pylint_args:
    :return:
    """

    pylint_args = [] if pylint_args is None else pylint_args

    if test_script_path is None and suite is None:
        raise ValueError("You must provide either test_script_path or suite")

    set_testing_script_path(script_path)

    if suite is None:
        suite = load_tests(test_script_path)

    stream = StringIO()

    runner = GraderTestRunner(stream, pylint_args=pylint_args)
    result = runner.run(suite)

    return result


def run_tests(args: argparse.Namespace) -> None:
    """Perform run tests action"""

    test_file_path = args.tests
    solution_file_path = args.solution
    pylint_args = map_pylint_arguments(args.pylint_args)

    result = run_tests_for(script_path=solution_file_path, test_script_path=test_file_path, pylint_args=pylint_args)

    result.stream.seek(0)
    print(result.stream.read())
