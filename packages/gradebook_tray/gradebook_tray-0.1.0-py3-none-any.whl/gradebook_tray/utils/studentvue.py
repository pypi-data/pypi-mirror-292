from datetime import datetime
from typing import NamedTuple, Union
from urllib.parse import urlparse

from lxml import etree
from zeep import Client, Plugin
from .util import tolerant_float, tolerant_datetime


class UnescapingPlugin(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        xml_string = etree.tostring(envelope).decode()
        xml_string = xml_string.replace("&amp;", "&")
        new_envelope = etree.fromstring(xml_string)
        return new_envelope, http_headers


Xml = Union[str, etree._Element]


def to_etree(xml: Xml) -> etree.Element:
    match xml:
        case etree._Element():
            return xml
        case str():
            return etree.fromstring(xml)
        case _:
            raise TypeError("xml must be a string or an etree.Element")


class AssignmentGradeCalc(NamedTuple):
    id: str
    type: str
    weight: float
    points: float
    points_possible: float
    weighted_pct: str
    calculated_mark: float

    @classmethod
    def from_xml(cls, id: str, xml: Xml) -> "AssignmentGradeCalc":
        """Create an AssignmentGradeCalc object from a xml element

        Args:
            xml (str): The xml element to create the object from. e.g., <AssignmentGradeCalc Type="TOTAL" Weight="100%" Points="0.00" PointsPossible="0.00" WeightedPct="100.00%" CalculatedMark="N/A" />

        Returns:
            AssignmentGradeCalc: The created AssignmentGradeCalc object
        """

        root = to_etree(xml)
        assert "None" not in id
        return cls(
            id=id,
            type=root.get("Type"),
            weight=float(root.get("Weight").replace("%", "")) / 100,
            points=float(root.get("Points")),
            points_possible=float(root.get("PointsPossible")),
            weighted_pct=root.get("WeightedPct"),
            calculated_mark=tolerant_float(root.get("CalculatedMark")),
        )

    def __str__(self) -> str:
        return f"{self.type}: {self.calculated_mark}/{self.points_possible} ({self.weighted_pct})"


class Assignment(NamedTuple):
    id: int
    measure: str
    type: str
    date: datetime
    due_date: datetime
    display_score: float
    # NOTE: Not included, otherwise the difference storage will always be different
    # total_seconds_since_post: float
    score_type: str
    points_possible: float
    points_earned: float
    notes: str
    teacher_id: int
    student_id: int
    measure_description: str
    has_drop_box: bool
    drop_start_date: datetime
    drop_end_date: datetime

    @classmethod
    def from_xml(cls, xml: Xml) -> "Assignment":
        """Create an Assignment object from a xml element

        Args:
            xml (str): The xml element to create the object from. e.g., <Assignment GradebookID="12345678" Measure="????" Type="AKS Progress*" Date="8/12/2024" DueDate="8/30/2024" DisplayScore="Not Due" TimeSincePost="10d" TotalSecondsSincePost="938969.0869863" ScoreType="Raw Score" Points="100 Points Possible" Notes="" TeacherID="123456" StudentID="123456" MeasureDescription="" HasDropBox="false" DropStartDate="8/12/2024" DropEndDate="8/30/2024">

        Returns:
            Assignment: The created Assignment object
        """

        root = to_etree(xml)

        points = root.get("Points")
        match points.split():
            case None | ["/"]:
                points_possible = float("nan")
                points_earned = float("nan")
            case [possible, "Points", "Possible"]:
                points_possible = tolerant_float(possible)
                points_earned = float("nan")
            case [earned, "/", possible]:
                points_possible = tolerant_float(possible)
                points_earned = tolerant_float(earned)
            case _:
                raise ValueError(f"Invalid points string: {points}")

        return cls(
            id=int(root.get("GradebookID")),
            measure=root.get("Measure"),
            type=root.get("Type"),
            date=tolerant_datetime(root.get("Date")),
            due_date=tolerant_datetime(root.get("DueDate")),
            display_score=tolerant_float(root.get("DisplayScore")),
            points_possible=points_possible,
            points_earned=points_earned,
            score_type=root.get("ScoreType"),
            notes=root.get("Notes"),
            teacher_id=int(root.get("TeacherID")),
            student_id=int(root.get("StudentID")),
            measure_description=root.get("MeasureDescription"),
            has_drop_box=root.get("HasDropBox") == "true",
            drop_start_date=tolerant_datetime(root.get("DropStartDate")),
            drop_end_date=tolerant_datetime(root.get("DropEndDate")),
        )


class Mark(NamedTuple):
    id: str
    name: str
    short_name: str
    calculated_score_string: str
    calculated_score_raw: str
    grade_calculations: list[AssignmentGradeCalc]
    assignments: list[Assignment]

    @classmethod
    def from_xml(cls, id: str, xml: Xml) -> "Mark":
        """Create a Mark object from a xml element

        Args:
            xml (str): The xml element to create the object from. e.g., <Mark MarkName="Sem1Avg" ShortMarkName="" CalculatedScoreString="N/A" CalculatedScoreRaw="">

        Returns:
            Mark: The created Mark object
        """

        root = to_etree(xml)
        assert "None" not in id
        return cls(
            id=id,
            name=root.get("MarkName"),
            short_name=root.get("ShortMarkName"),
            calculated_score_string=root.get("CalculatedScoreString"),
            calculated_score_raw=root.get("CalculatedScoreRaw"),
            grade_calculations=[
                AssignmentGradeCalc.from_xml(
                    f'{id}_{grade_calc.get("Type")}', grade_calc
                )
                for grade_calc in root.xpath(
                    "GradeCalculationSummary/AssignmentGradeCalc"
                )
            ],
            assignments=[
                Assignment.from_xml(assignment)
                for assignment in root.xpath("Assignments/Assignment")
            ],
        )


class Course(NamedTuple):
    period: int
    title: str
    name: str
    id: str
    room: str
    staff: str
    staff_email: str
    staff_gu: str
    image_type: str
    marks: list[Mark]

    @classmethod
    def from_xml(cls, xml: Xml) -> "Course":
        """Create a Course object from a xml element

        Args:
            xml (str): The xml element to create the object from. e.g., <Course Period="0" Title="????" CourseName="????" CourseID="????" Room="????" Staff="????" StaffEMail="????" StaffGU="????????-????-????-????-????????????" ImageType="????" HighlightPercentageCutOffForProgressBar="50" UsesRichContent="true">
        """

        root = to_etree(xml)
        id = str(root.get("CourseID"))
        return cls(
            period=int(root.get("Period")),
            title=root.get("Title"),
            name=root.get("CourseName"),
            id=str(root.get("CourseID")),
            room=root.get("Room"),
            staff=root.get("Staff"),
            staff_email=root.get("StaffEMail"),
            staff_gu=root.get("StaffGU"),
            image_type=root.get("ImageType"),
            marks=[
                Mark.from_xml(f'{id}_{mark.get("MarkName")}', mark)
                for mark in root.xpath("Marks/Mark")
            ],
        )


class StudentVue:
    def __init__(
        self,
        username: str,
        password: str,
        endpoint: str,
    ):
        """Create a studentvue object

        Args:
            username (str): The username of the studentvue account
            password (str): The password of the studentvue account
            endpoint (str): The endpoint of the studentvue account, usually formatted as https://<district>.edupoint.com
        """

        self._username = username
        self._password = password
        endpoint = urlparse(endpoint)
        self._base_url = f"{endpoint.scheme}://{endpoint.netloc}"
        self._client = Client(
            f"{endpoint.scheme}://{endpoint.netloc}/Service/PXPCommunication.asmx?WSDL",
            plugins=[UnescapingPlugin()],
        )

    def get_grade_book(self, report_period: int = None) -> list[Course]:
        """Get the gradebook for the student

        Args:
            report_period (int, optional): The report period to get the gradebook for. Defaults to None.

        Returns:
            str: The gradebook for the student
        """

        xml = self._make_service_request("Gradebook", ReportPeriod=report_period)
        courses = etree.fromstring(xml).xpath("//Course")
        return [Course.from_xml(course) for course in courses]

    def _make_service_request(self, method_name, **kwargs) -> str:
        def _xml(tag, children=None):
            if children is None:
                children = []
            return f"&lt;{tag}&gt;{''.join(children)}&lt;/{tag}&gt;"

        param_str = _xml(
            "Parms", [_xml(key, [str(value)]) for key, value in kwargs.items()]
        )

        return self._client.service.ProcessWebServiceRequest(
            userID=self._username,
            password=self._password,
            skipLoginLog=1,
            parent=0,
            webServiceHandleName="PXPWebServices",
            methodName=method_name,
            paramStr=param_str,
        )
