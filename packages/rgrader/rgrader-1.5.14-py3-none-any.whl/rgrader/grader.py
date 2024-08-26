"""Main grader module"""
import argparse
import traceback


from .classroom.commands import run_no_args_argparse, get_course, choose_course_work, choose_course_work_argparse
from .classroom.commands import setup_grade_submissions, grade_submissions
from .interactive.interactive import run_tests_interactive
from .test_runner import run_tests_setup_argparse, run_tests

ACTIONS = {
    'rt': (run_tests_setup_argparse, run_tests),
    'rti': (run_no_args_argparse, run_tests_interactive),
    'gc': (run_no_args_argparse, get_course),
    'submissions': (setup_grade_submissions, grade_submissions),
    'ga': (choose_course_work_argparse, choose_course_work)
}


def grade():
    """
    Run tests for solution script with specified test file and show grade
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("action", help="Action to perform", choices=ACTIONS)

    for setup_function, _ in ACTIONS.values():
        setup_function(argument_parser)

    args = argument_parser.parse_args()
    action = args.action

    if action not in ACTIONS:
        print(f"There is no such action `{action}`. Available actions are: {', '.join(ACTIONS.keys())}")

    try:
        ACTIONS[action][1](args)
    except Exception as ex:
        traceback.print_exc()
