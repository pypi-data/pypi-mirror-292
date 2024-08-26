from __future__ import annotations

import curses

from . import constants
from .model import Model


class Mode:
    NORMAL = "normal"
    INPUT = "input"


FORBIDDEN_KEYSTROKES = [
    curses.KEY_UP,
    curses.KEY_DOWN,
    curses.KEY_LEFT,
    curses.KEY_RIGHT,
    curses.KEY_ENTER,
    curses.KEY_BACKSPACE,
    10,
    13,
]


class Panel:

    def __init__(self, window, storage: Model):
        self.window = window
        self.storage = storage
        self.focused = False
        self.visible = True
        self.rows, self.cols = self.window.getmaxyx()


def is_enter(c: int) -> bool:
    """Check if enter was entered"""
    return c == curses.KEY_ENTER or c == 10 or c == 13


class StudentSidebar(Panel):

    NAME = "student_sidebar"

    def __init__(self, screen, storage):
        super().__init__(screen, storage)

        self.position = 0

        self.width = len(max(self.storage.students_folders, key=len)) + 2
        self.width = max(self.width, len(max(self.storage.problems, key=len)) + 20)

    def draw(self):

        self.window.addstr(0, 1, "STUDENTS:", curses.A_UNDERLINE)

        self.window.vline(0, self.width, curses.ACS_VLINE, 1)
        self.window.vline(1, self.width, curses.ACS_SSSB, 1)
        self.window.vline(2, self.width, curses.ACS_VLINE, self.rows - SummaryPanel.HEIGHT - 2)

        for i, student in enumerate(self.storage.students_folders):
            if i == self.position and self.focused:
                mode = curses.A_REVERSE
            elif i == self.position and not self.focused:
                mode = constants.GREEN_COLOR | curses.A_ITALIC
            else:
                mode = curses.A_NORMAL
            self.window.addstr(i + 1, 1, student, mode)

    def control(self, c):
        if c == curses.KEY_UP and self.position > 0:
            self.position -= 1
        elif c == curses.KEY_DOWN and self.position < len(self.storage.students_folders) - 1:
            self.position += 1
        elif is_enter(c):
            self.storage.set_current_panel(ProblemsTabs.NAME)

        self.storage.current_student = self.storage.students_folders[self.position]


class ProblemsTabs(Panel):
    NAME = 'problem_tabs'

    def __init__(self, window, storage):
        super().__init__(window, storage)

        self.position = 0

        self.problems = [rule.filename for rule in storage.grading_schema.rules]

    def draw(self):

        padding = self.storage.panels[StudentSidebar.NAME].width

        self.window.addstr(0, padding + 2, "FILES:", curses.A_UNDERLINE)
        self.window.hline(1, padding, curses.ACS_HLINE, self.cols - 3)

        padding += 7

        for i, student in enumerate(self.problems):
            if i == self.position and self.focused:
                mode = curses.A_REVERSE
            elif i == self.position and not self.focused:
                mode = constants.GREEN_COLOR | curses.A_ITALIC
            else:
                mode = curses.A_NORMAL

            self.window.addstr(0, padding + 2, student, mode)
            padding += len(student) + 1

    def control(self, c):
        match c:
            case curses.KEY_LEFT if self.position > 0:
                self.position -= 1
            case curses.KEY_RIGHT if self.position < len(self.problems) - 1:
                self.position += 1
            case curses.KEY_ENTER | 10 | 13:
                self.storage.run_test_for_selected_problem()
                self.storage.set_current_panel(TestsResultPanel.NAME)
                self.storage.panels[TestsResultPanel.NAME].reset_cursor()

        self.storage.current_problem_file = self.problems[self.position]


class TestsResultPanel(Panel):
    NAME = 'tests_result_panel'
    TOP_MARGIN = 2

    def __init__(self, window, storage):
        super().__init__(window, storage)

        self.start_y = 0
        self.start_x = 0
        self.margin = 0
        self.mode = Mode.NORMAL

        self.visible_vertical_range = self.rows - 3
        self.visible_horizontal_range = 0

        self.x, self.y = 0, 0

        self.length_of_current_line = None
        self.max_horizontal_scroll = None
        self.maximum_x = None
        self.maximum_y = None

        self.lines = None

    @property
    def current_line(self) -> str:
        """Return current line"""
        return self.lines[self.start_y + self.y]

    @property
    def actual_y(self) -> str:
        return self.y + self.start_y

    @property
    def actual_x(self) -> str:
        return self.x + self.start_x

    def draw(self):

        self.margin = self.storage.panels[StudentSidebar.NAME].width + 2
        self.visible_horizontal_range = self.cols - self.margin

        self.lines = self.storage.get_current_test_output().split('\n')

        for i, line in enumerate(self.lines[self.start_y: self.start_y + self.visible_vertical_range]):
            self.window.addstr(2 + i, self.margin, line[self.start_x:self.start_x + self.visible_horizontal_range])

        if self.focused:
            curses.curs_set(1)
            self.window.move(self.TOP_MARGIN + self.y, self.margin + self.x)
        else:
            curses.curs_set(0)

    def control(self, c):

        self.count_navigation_variables()

        match c:
            case curses.KEY_UP:
                self.navigate_up()
            case curses.KEY_DOWN:
                self.navigate_down()
            case curses.KEY_RIGHT:
                self.navigate_right()
            case curses.KEY_LEFT:
                self.navigate_left()
            case 36 | 59 if self.mode == Mode.NORMAL:  # $
                self.navigate_end_line()
            case 94 | 58 if self.mode == Mode.NORMAL:  # ^
                self.navigate_start_line()
            case 71 | 159 if self.mode == Mode.NORMAL:  # G
                self.start_y = max(0, len(self.lines) - self.maximum_y)
                self.y = self.maximum_y - 1
            case 103 | 191 if self.mode == Mode.NORMAL:  # g
                self.start_y = 0
                self.y = 0
            case 114 | 186 if self.mode == Mode.NORMAL:  # r
                self.storage.run_test_for_selected_problem()

    def count_navigation_variables(self):
        self.length_of_current_line = len(self.lines[self.start_y + self.y])
        self.max_horizontal_scroll = max(0, self.length_of_current_line - self.visible_horizontal_range)
        self.maximum_x = min(self.visible_horizontal_range - 1, self.length_of_current_line)
        self.maximum_y = min(len(self.lines), self.visible_vertical_range)

    def navigate_left(self) -> None:
        if self.x > 0:
            self.x -= 1

        if self.x == 0:
            self.start_x = max(self.start_x - 1, 0)

    def navigate_right(self) -> None:
        if self.x < self.maximum_x:
            self.x += 1

        if self.x == self.maximum_x:
            self.start_x = min(self.start_x + 1, self.max_horizontal_scroll)

    def navigate_up(self) -> None:
        if self.y > 0:
            self.y -= 1

        if self.y == 0:
            self.start_y = max(self.start_y - 1, 0)

    def navigate_down(self) -> None:
        if self.y < self.maximum_y - 1:
            self.y += 1

        if self.y == self.maximum_y - 1:
            self.start_y = min(self.start_y + 1, len(self.lines) - self.maximum_y - 1)

    def navigate_start_line(self) -> None:
        self.x = 0
        self.start_x = 0

    def navigate_end_line(self) -> None:
        self.start_x = max(0, self.length_of_current_line - self.visible_horizontal_range)
        self.x = self.maximum_x

    def reset_cursor(self):
        self.x, self.y = 0, 0


class SummaryPanel(Panel):

    NAME = 'summary_panel'
    HEIGHT = 15

    def __init__(self, window, storage):
        super().__init__(window, storage)

    def draw(self):

        width = self.storage.panels[StudentSidebar.NAME].width
        start_y = self.rows - self.HEIGHT

        self.window.hline(start_y, 0, curses.ACS_HLINE, width)
        self.window.addch(start_y, width, curses.ACS_SBSS)
        self.window.vline(start_y + 1, width, curses.ACS_VLINE, self.HEIGHT)

        self.window.addstr(start_y + 1, 1, "SUMMARY:", curses.A_UNDERLINE)

        total_grade = 0

        for i, rule in enumerate(self.storage.grading_schema.rules):
            test_result = self.storage.test_runner_result[self.storage.current_student].get(rule.filename)

            if test_result is not None:
                gained_grade = test_result.current_grade
                max_grade = test_result.max_grade
                reduction = test_result.reduction
            else:
                max_grade, gained_grade, reduction = 0, 0, 0

            total_grade += gained_grade

            result_string = "No Data" if test_result is None else f"{gained_grade}/{max_grade}"
            result_string = f" - {rule.filename}: {result_string}"

            reduction_string = f" (-{reduction:.1f})" if reduction else ""

            self.window.addstr(start_y + i + 2, 1, result_string)
            self.window.addstr(start_y + i + 2, 1 + len(result_string), reduction_string, constants.RED_COLOR)

        self.window.addstr(start_y + len(self.storage.grading_schema.rules) + 2, 2,
                           f"> Total Grade: {total_grade}/{self.storage.grading_schema.total_grade}")


class EditorPanel(TestsResultPanel):

    NAME = 'editor_panel'

    def __init__(self, window, storage):
        super().__init__(window, storage)


    def draw(self):

        self.margin = self.storage.panels[StudentSidebar.NAME].width + 2
        self.visible_horizontal_range = self.cols - self.margin

        self.lines = self.storage.current_test_result.summary.split('\n') if self.storage.current_test_result is not None else [""]

        self.window.addstr(2, self.margin, f"SUMMARY EDITOR: {self.mode} mode", curses.A_UNDERLINE)
        for i, line in enumerate(self.lines[self.start_y: self.start_y + self.visible_vertical_range]):
            self.window.addstr(3 + i, self.margin, line[self.start_x:self.start_x + self.visible_horizontal_range])

        if self.focused:
            curses.curs_set(1)
            self.window.move(self.TOP_MARGIN + self.y + 1, self.margin + self.x)
        else:
            curses.curs_set(0)

    def control(self, c):
        """Control behaviour of the editor panel."""
        super().control(c)

        match c:
            case 105 if self.mode == Mode.NORMAL:  # i
                self.mode = Mode.INPUT
            case curses.KEY_F1 if self.mode == Mode.INPUT:
                self.mode = Mode.NORMAL
            case ch if self.mode == Mode.INPUT and ch not in FORBIDDEN_KEYSTROKES:
                self.lines[self.actual_y] = self.current_line[:self.actual_x] + chr(ch) + self.current_line[self.actual_x:]
                self.count_navigation_variables()
                self.navigate_right()
            case curses.KEY_BACKSPACE if self.mode == Mode.INPUT and self.actual_x != 0:
                self.lines[self.actual_y] = self.current_line[:self.actual_x - 1] + self.current_line[self.actual_x:]
                self.count_navigation_variables()
                self.navigate_left()
            case curses.KEY_BACKSPACE if self.mode == Mode.INPUT and self.actual_x == 0:
                current_line = self.lines.pop(self.actual_y)
                
            case curses.KEY_ENTER | 10 | 13:
                current_line = self.current_line
                self.lines[self.actual_y] = current_line[:self.actual_x]
                self.lines.insert(self.actual_y + 1, current_line[self.actual_x:])
                self.count_navigation_variables()
                self.navigate_start_line()
                self.navigate_down()

        self.storage.current_test_result.summary = '\n'.join(self.lines)
