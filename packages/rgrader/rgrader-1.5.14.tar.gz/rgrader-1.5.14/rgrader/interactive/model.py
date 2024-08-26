from __future__ import annotations

import os
import shutil
from copy import deepcopy
from dataclasses import dataclass

import pyperclip

from ..classroom.commands import collect_test_scripts, TMP_TESTS_DIR
from ..classroom.model import GradingSchema
from ..test_runner import load_tests, GraderTestResult, run_tests_for

REDUCTION_STEP = 0.3


@dataclass
class TestResult:
    """Class to hold the test result"""
    gained_grade: float
    max_grade: float
    reduction: float = 0
    tester_output: str = ""
    summary: str = ""

    @property
    def current_grade(self) -> float:
        """Return grade with reduction"""
        return round(self.gained_grade - self.reduction, 2)


class Model:
    """Class for storing global data of app"""

    def __init__(self, grading_schema: GradingSchema):
        self.current_panel = None
        self.panels = {}

        self.grading_schema = grading_schema

        self.students_folders = get_students_folders()
        self.problems = [rule.filename for rule in self.grading_schema.rules]

        self.current_student = self.students_folders[0]
        self.current_problem_file = grading_schema.rules[0].filename

        self.test_runner_result = {student: {} for student in self.students_folders}
        self.test_cases = {}

        self.load_test_cases()

    @property
    def current_test_result(self) -> TestResult:
        """Return the current test result"""
        if self.current_problem_file not in self.test_runner_result[self.current_student]:
            return None

        return self.test_runner_result[self.current_student][self.current_problem_file]

    def load_test_cases(self) -> None:
        """Load test cases from specified locations in grading schema and write them to self.test_cases"""
        collected_test_scripts = collect_test_scripts(self.grading_schema)

        for rule, copied_path in collected_test_scripts.items():
            self.test_cases[rule] = load_tests(copied_path)

        shutil.rmtree(TMP_TESTS_DIR)

    def add_panel(self, name: str, panel) -> None:
        """Add panel to panel registry"""
        self.panels[name] = panel

    def set_current_panel(self, name: str) -> None:
        """Set current panel"""
        if self.current_panel is not None:
            self.current_panel.focused = False

        self.current_panel = self.panels.get(name)
        self.current_panel.visible = True
        self.current_panel.focused = True

    def get_current_test_output(self) -> str:
        if self.current_problem_file not in self.test_runner_result[self.current_student]:
            return ""

        return self.test_runner_result[self.current_student][self.current_problem_file].tester_output

    def get_current_test_result(self) -> GraderTestResult | None:
        if self.current_problem_file not in self.test_runner_result[self.current_student]:
            return None

        return self.test_runner_result[self.current_student][self.current_problem_file]

    def run_test_for_selected_problem(self) -> None:
        script_path = os.path.join(self.current_student, self.current_problem_file)

        grading_rule = next(filter(lambda r: r.filename == self.current_problem_file, self.grading_schema.rules))

        result = run_tests_for(script_path=script_path, suite=deepcopy(self.test_cases[grading_rule]),
                               pylint_args=self.grading_schema.pylint_args)

        rule = next(filter(lambda r: r.filename == self.current_problem_file, self.grading_schema.rules))
        max_grade = self.grading_schema.total_grade * rule.weight / 100
        gained_grade = round(result.gained_points / result.total_points * max_grade, 2)

        test_result = TestResult(gained_grade=gained_grade, max_grade=max_grade, tester_output=result.output)

        self.test_runner_result[self.current_student][self.current_problem_file] = test_result

    def reduce_grade(self) -> None:
        """
        Reduce gained grade of current problem by REDUCTION_STEP
        """
        if self.current_test_result is None:
            return

        if self.current_test_result.current_grade - REDUCTION_STEP >= 0:
            self.current_test_result.reduction += REDUCTION_STEP

        self.current_test_result.reduction = round(self.current_test_result.reduction, 2)

    def cancel_reduction(self) -> None:
        """
        Cancel the reduction on current problem by one REDUCTION_STEP
        :return: None
        """
        if self.current_test_result is None:
            return

        if self.current_test_result.current_grade + REDUCTION_STEP <= self.current_test_result.gained_grade:
            self.current_test_result.reduction -= REDUCTION_STEP

        self.current_test_result.reduction = round(self.current_test_result.reduction, 2)

    def copy_summary_to_clipboard(self) -> None:
        """
        Copy generated summary to clipboard
        :return:
        """
        summary_str_parts = ["SUMMARY:"]

        total_grade = 0

        for i, rule in enumerate(self.grading_schema.rules):
            test_result = self.test_runner_result[self.current_student].get(rule.filename)

            if test_result is not None:
                gained_grade = test_result.current_grade
                max_grade = test_result.max_grade
            else:
                max_grade, gained_grade, reduction = 0, 0, 0

            total_grade += gained_grade

            result_string = "No Data" if test_result is None else f"{gained_grade}/{max_grade}"
            result_string = f" - {rule.filename}: {result_string}"
            summary_str_parts.append(result_string)

        summary_str_parts.append(f"> Total Grade: {total_grade}/{self.grading_schema.total_grade}")

        pyperclip.copy('\n'.join(summary_str_parts))


def get_students_folders() -> list[str]:
    """Return a list of student folders from current directory"""
    return [path for path in os.listdir() if os.path.isdir(path) and
            os.path.exists(os.path.join(path, '.submission.yaml'))]
