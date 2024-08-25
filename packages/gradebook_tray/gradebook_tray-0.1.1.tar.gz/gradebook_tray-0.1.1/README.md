This package provide an easy interface to track StudentVUE grade, a fully-typed interface, a differential database that
wouldn't continuously take up the space, and a POC application made with PySimpleGUI that can be used to track the grade
easily.

## Installation

```bash
pip install gradebook_tray
```

## Usage

The package provide a fully-typed interface to interact with the StudentVUE grade book. The following code snippet shows
how to use the package to get the grade book, marks, assignments, and grade calculations.

```python
from gradebook_tray import StudentVue, Course, Mark, Assignment, AssignmentGradeCalc

client = StudentVue("username", "password", "endpoint")
grade_book: list[Course] = client.get_grade_book()
marks: list[Mark] = grade_book[0].marks
assignments: list[Assignment] = grade_book[0].marks[0].assignments
grade_calc: list[AssignmentGradeCalc] = grade_book[0].marks[0].grade_calculations
```

Furthermore, the package also provide a database implementation to track the grade easily (and, to a certain extent,
capable of a general timeseries database).

```python
from gradebook_tray import DifferenceStorage, Assignment, Mark

# Create a table assignment & assignment_history in the database
assignment_db = DifferenceStorage(
    named_tuple=Assignment,
    db_path="data.db",  # the location of the database
    primary_key="id",  # a primary key is required, as of 0.1.0
    not_null_cols=["id", "measure"],  # these columns are required to be not null
    unique_cols=["id"],  # these columns are required to be unique
)

# Create a table mark & mark_history in the database, automatically handle one-to-many relationship between assignment and mark by altering the assignment table. However, this feature require assignment database to be declared first and the foreign object must be a named tuple.
mark_db = DifferenceStorage(
    named_tuple=Mark,
    db_path="data.db",
    primary_key="id",
)
```

Lastly, the package also provide a POC application made with PySimpleGUI that can be used to track the grade easily.
This application have only been tested on Windows, but it should work on other platforms as well.

```bash
python -m gradebook_tray
```