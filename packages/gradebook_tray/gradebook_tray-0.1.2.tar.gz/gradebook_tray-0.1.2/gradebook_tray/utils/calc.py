from .studentvue import Assignment, AssignmentGradeCalc, Course
from math import isnan


def calculate_breakdown_grade(
    assignments: list[Assignment],
    grade_calculations: list[AssignmentGradeCalc],
) -> dict[str, float]:
    """
    Calculate the current grade based on the assignments and
    grade calculations.

    Args:
        assignments list[Assignment]: List of assignments
        grade_calculations list[AssignmentGradeCalc]: List of grade calculations

    Returns: dict[str, float], the current grade for each category
    """

    category = {}
    for assignment in assignments:
        if isnan(assignment.points_earned) or isnan(assignment.points_possible):
            continue
        category.setdefault(assignment.type, []).append(
            assignment.points_earned / assignment.points_possible
        )
    return {
        gc.type: sum(grades) / len(grades) if grades else float("nan")
        for gc, grades in zip(
            grade_calculations,
            [category.get(gc.type, []) for gc in grade_calculations],
        )
        if gc.type.lower() != "total"
    }


def calculate_grade(
    assignments: list[Assignment],
    grade_calculations: list[AssignmentGradeCalc],
) -> float:
    """
    Calculate the current grade based on the assignments and
    grade calculations.

    Args:
        assignments list[Assignment]: List of assignments
        grade_calculations list[AssignmentGradeCalc]: List of grade calculations

    Returns: float, the current grade
    """

    gc_weight = {
        gc.type: gc.weight for gc in grade_calculations if gc.weight is not None
    }
    breakdown = calculate_breakdown_grade(assignments, grade_calculations)
    total, weights = 0.0, 0.0
    for key, value in breakdown.items():
        if isnan(value) or key not in gc_weight:
            continue
        total += value * gc_weight[key]
        weights += gc_weight[key]
    return total / weights * 100 if weights else float("nan")


def calculate_total_grade(courses: list[Course]) -> float:
    """
    Calculate the current grade based on the courses.

    Args:
        courses list[Course]: List of courses

    Returns: float, the current grade
    """

    total = 0.0
    n = 0
    for course in courses:
        score = calculate_grade(
            course.marks[0].assignments, course.marks[0].grade_calculations
        )
        if isnan(score):
            continue
        total += score
        n += 1
    return total / n if n else float("nan")
