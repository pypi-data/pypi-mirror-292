import time
from pathlib import Path

import PySimpleGUI as sg
from psgtray import SystemTray

from gradebook_tray.utils import (
    Config,
    StudentVue,
    DifferenceStorage,
    Assignment,
    AssignmentGradeCalc,
    Mark,
    Course,
    calculate_total_grade,
    calculate_grade,
)
from gradebook_tray.utils.config import logger

ICON_PATH = Path(__file__).resolve().parent / "assets"


def font(size: int = 14, bold: bool = False):
    return "Microsoft Yahei UI", size, "bold" if bold else "normal"


sg.LOOK_AND_FEEL_TABLE["MyColors"] = {
    "BACKGROUND": "#f1f5f9",
    "TEXT": "#334155",
    "INPUT": "#3b82f6",
    "TEXT_INPUT": "#1e3a8a",
    "SCROLL": "#f1f5f9",
    "BUTTON": ("#e2e8f0", "#2563eb"),
    "PROGRESS": sg.DEFAULT_PROGRESS_BAR_COLOR,
    "BORDER": 1,
    "SLIDER_DEPTH": 1,
    "PROGRESS_DEPTH": 1,
    "ACCENT1": "#818cf8",
    "ACCENT2": "#4f46e5",
    "ACCENT3": "#312e81",
}
sg.change_look_and_feel("MyColors")


def course_widget(course: Course):
    grade = calculate_grade(
        course.marks[0].assignments, course.marks[0].grade_calculations
    )
    widget = sg.Column(
        [
            [
                sg.Text(
                    course.name,
                    font=font(14, True),
                    pad=((16, 0), (12, 2)),
                    enable_events=True,
                    key=f"{course.id}_name",
                ),
                sg.Push(),
                sg.Text(f"{grade:.3f}", font=font(14), pad=((0, 16), (12, 2))),
            ],
            [
                sg.Text(course.staff, font=font(), pad=((16, 0), (2, 12))),
                sg.Push(),
                sg.Text(course.period, font=font(), pad=((0, 16), (2, 12))),
            ],
        ],
        element_justification="left",
        expand_x=True,
        pad=(12, 8),
        key=course.id,
    )
    return widget


def assignment_widget(assignment: Assignment):
    widget = sg.Column(
        [
            [
                sg.Text(
                    assignment.measure,
                    font=font(14, True),
                    pad=((16, 0), (12, 2)),
                    enable_events=True,
                    key=f"{assignment.id}_name",
                ),
                sg.Push(),
                sg.Text(
                    f"{assignment.points_earned}/{assignment.points_possible}",
                    font=font(14),
                    pad=((0, 16), (12, 2)),
                ),
            ],
            [
                sg.Text(assignment.due_date, font=font(), pad=((16, 0), (2, 12))),
                sg.Push(),
                sg.Text(assignment.type, font=font(), pad=((0, 16), (2, 12))),
            ],
        ],
        element_justification="left",
        expand_x=True,
        pad=(12, 8),
        key=assignment.id,
    )
    return widget


def main():
    cfg = Config()
    client = StudentVue(cfg["username"], cfg["password"], cfg["endpoint"])

    db_a = DifferenceStorage(
        named_tuple=Assignment,
        db_path=cfg["db_path"],
        primary_key="id",
    )
    db_cal = DifferenceStorage(
        named_tuple=AssignmentGradeCalc,
        db_path=cfg["db_path"],
        primary_key="id",
    )
    db_m = DifferenceStorage(
        named_tuple=Mark,
        db_path=cfg["db_path"],
        primary_key="id",
    )
    db_c = DifferenceStorage[Course](
        named_tuple=Course,
        db_path=cfg["db_path"],
        primary_key="id",
    )

    def update():
        try:
            window.write_event_value("Updater Status", "Updating...")
            grade_book = client.get_grade_book()
            window.write_event_value("Updater Status", "Syncing...")
            db_c.sync(grade_book)
            window.write_event_value(
                "Updater Status", calculate_total_grade(grade_book)
            )
        except Exception as e:
            logger.error(e)
            window.write_event_value("Updater Status", f"Error")

    menu = ["", ["Status", "Refresh", "Exit"]]
    course_columns = [
        [course_widget(course)]
        for course in sorted(db_c.current_snapshot(), key=lambda x: x.period)
    ]
    window = sg.Window(
        "StudentVue Tray",
        [
            [
                sg.Column(
                    course_columns,
                    scrollable=True,
                    vertical_scroll_only=True,
                    expand_x=True,
                    expand_y=True,
                    key="course_column",
                    background_color="#f8fafc",
                    pad=8,
                )
            ]
        ],
        enable_close_attempted_event=True,
        finalize=True,
        resizable=True,
        background_color="#f8fafc",
    )
    frame_id = window["course_column"].Widget.frame_id
    canvas = window["course_column"].Widget.canvas

    # HACK: Fix the resizing issue
    # ref: https://github.com/PySimpleGUI/PySimpleGUI/issues/4752
    def _canva_config(event, canvas=canvas, frame_id=frame_id):
        canvas.itemconfig(frame_id, width=canvas.winfo_width())

    canvas.bind("<Configure>", _canva_config)
    window.hide()

    tray = SystemTray(
        menu=menu,
        single_click_events=False,
        window=window,
        icon=str(ICON_PATH / "icon.png"),
    )

    last_update = time.time()

    current_grade = calculate_total_grade(db_c.current_snapshot())

    while True:
        if time.time() - last_update > cfg["update_interval"]:
            window.start_thread(update)
            last_update = time.time()
        event, values = window.read()
        if event == tray.key:
            event = values[tray.key]

        match event:
            case "Updater Status":
                val = values['Updater Status']
                tray.set_tooltip(str(val))
                match val:
                    case "Error":
                        tray.show_message("Error", "An error occurred")
                        tray.change_icon(str(ICON_PATH / "error.png"))
                    case "Updating...":
                        tray.change_icon(str(ICON_PATH / "fetch.png"))
                    case "Syncing...":
                        tray.change_icon(str(ICON_PATH / "update.png"))
                    case _:
                        tray.change_icon(str(ICON_PATH / "icon.png"))
                        tray.set_tooltip(f"Current Grade: {val:.3f}")
                        new_grade = float(val)
                        if new_grade < current_grade:
                            tray.show_message(
                                "Grade Update",
                                f"Grade decreased to {new_grade:.3f}. Aww :(",
                            )
                        elif new_grade > current_grade:
                            tray.show_message(
                                "Grade Update",
                                f"Grade increased to {new_grade:.3f}. Yay!",
                            )
                        current_grade = new_grade
            case "Status":
                window.un_hide()
            case sg.WINDOW_CLOSED | sg.WIN_CLOSED | sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                window.hide()  # minimize to tray
            case "Exit":
                break
            case "Refresh":
                window.start_thread(update)
            case _:
                if event.endswith("_name"):
                    course_id = event.split("_")[0]
                    course = db_c[course_id]
                    assignments = course.marks[0].assignments
                    assignment_columns = [
                        [assignment_widget(assignment)] for assignment in assignments
                    ]
                    assignment_window = sg.Window(
                        course.name,
                        [
                            [
                                sg.Column(
                                    assignment_columns,
                                    scrollable=True,
                                    vertical_scroll_only=True,
                                    expand_x=True,
                                    expand_y=True,
                                    background_color="#f8fafc",
                                    pad=8,
                                )
                            ]
                        ],
                        finalize=True,
                        background_color="#f8fafc",
                    )
                    assignment_window.read()
                    assignment_window.close()

    window.close()
    tray.close()
    db_a.close()
    db_cal.close()
    db_m.close()
    db_c.close()


if __name__ == "__main__":
    main()
