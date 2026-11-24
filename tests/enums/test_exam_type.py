from enum import StrEnum

from enums import ExamType


def test_exam_type_oab_value() -> None:
    assert issubclass(ExamType, StrEnum)
    assert ExamType.OAB == "OAB"
    assert ExamType.OAB.value == "OAB"
