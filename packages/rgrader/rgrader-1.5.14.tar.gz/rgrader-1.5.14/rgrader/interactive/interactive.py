"""Interactive grading tool"""
from __future__ import annotations
import curses
import traceback
import argparse

from . import constants
from .model import Model
from .panels import StudentSidebar, ProblemsTabs, TestsResultPanel, SummaryPanel, EditorPanel
from ..classroom.commands import parse_grading_schema


def run_tests_interactive_argument_parser(argument_parser: argparse.ArgumentParser) -> None:
    """Add necessary arguments for interactive grading"""
    argument_parser.add_argument('-gs', '--grading-scheme', required=False)


def create_color_pairs() -> None:
    """Init color pairs"""
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    constants.GREEN_COLOR = curses.color_pair(1)
    constants.RED_COLOR = curses.color_pair(2)


def wrapper(screen, args: argparse.Namespace) -> None:

    create_color_pairs()
    storage = Model(parse_grading_schema(args.grading_schema))

    sidebar = StudentSidebar(screen, storage)
    problem_tabs = ProblemsTabs(screen, storage)
    summary_panel = SummaryPanel(screen, storage)
    test_result_panel = TestsResultPanel(screen, storage)
    editor_panel = EditorPanel(screen, storage)

    # Must be in such order to maintain proper drawing
    storage.add_panel(ProblemsTabs.NAME, problem_tabs)
    storage.add_panel(SummaryPanel.NAME, summary_panel)
    storage.add_panel(StudentSidebar.NAME, sidebar)
    storage.add_panel(TestsResultPanel.NAME, test_result_panel)

    storage.set_current_panel(StudentSidebar.NAME)

    sidebar.draw()
    problem_tabs.draw()
    summary_panel.draw()

    while True:
        screen.erase()

        for panel in storage.panels.values():
            if panel.visible:
                panel.draw()

        c = screen.getch()
        match c:
            case 113:
                break
            case 97 | 132:
                storage.set_current_panel(StudentSidebar.NAME)
            case 115 | 150:
                storage.set_current_panel(ProblemsTabs.NAME)
            case 100 | 178:
                editor_panel.visible = False
                storage.set_current_panel(TestsResultPanel.NAME)
            case 44 | 177:  # , make reduction
                storage.reduce_grade()
            case 46 | 142:  # . - erase reduction
                storage.cancel_reduction()
            case 121 | 189:
                storage.copy_summary_to_clipboard()

        storage.current_panel.control(c)


def run_tests_interactive(args: argparse.Namespace) -> None:
    """Run the test with terminal interface"""
    try:
        curses.wrapper(wrapper, args)
    except Exception as ex:
        traceback.print_exc()
