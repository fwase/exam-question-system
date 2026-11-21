from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from database.exams_questions.config import Base
from database.exams_questions.models import Exam, Question


def test_exam_table_schema():
    assert "exams" in Base.metadata.tables
    table = Base.metadata.tables["exams"]

    expected_columns = {
        "id",
        "type",
        "year",
        "examining_board",
        "subject",
        "state",
        "job_title",
    }
    assert set(table.columns.keys()) == expected_columns

    assert table.c.id.primary_key is True
    assert isinstance(table.c.id.type, Integer)
    assert isinstance(table.c.type.type, String) and table.c.type.type.length == 20
    assert isinstance(table.c.year.type, Integer)
    assert (
        isinstance(table.c.examining_board.type, String)
        and table.c.examining_board.type.length == 100
    )
    assert (
        isinstance(table.c.subject.type, String)
        and table.c.subject.type.length == 100
    )
    assert isinstance(table.c.state.type, String) and table.c.state.type.length == 20
    assert (
        isinstance(table.c.job_title.type, String)
        and table.c.job_title.type.length == 100
    )


def test_question_table_schema_and_indexes():
    assert "questions" in Base.metadata.tables
    table = Base.metadata.tables["questions"]

    expected_columns = {
        "id",
        "uuid",
        "number",
        "theme",
        "statement",
        "choices",
        "labels_choices",
        "correct_label_choice",
        "exam_id",
    }
    assert set(table.columns.keys()) == expected_columns

    assert table.c.id.primary_key is True
    assert isinstance(table.c.id.type, Integer)
    assert isinstance(table.c.uuid.type, String) and table.c.uuid.type.length == 36
    assert isinstance(table.c.number.type, Integer)
    assert isinstance(table.c.theme.type, String) and table.c.theme.type.length == 100
    assert isinstance(table.c.statement.type, Text)
    assert isinstance(table.c.choices.type, ARRAY)
    assert isinstance(table.c.choices.type.item_type, Text)
    assert isinstance(table.c.labels_choices.type, ARRAY)
    assert isinstance(table.c.labels_choices.type.item_type, String)
    assert table.c.labels_choices.type.item_type.length == 5
    assert (
        isinstance(table.c.correct_label_choice.type, String)
        and table.c.correct_label_choice.type.length == 5
    )

    fks = list(table.c.exam_id.foreign_keys)
    assert len(fks) == 1
    assert fks[0].column.table.name == "exams"
    assert fks[0].column.name == "id"

    indexes = {idx.name: idx for idx in table.indexes}
    assert "ix_questions_uuid_btree" in indexes
    assert indexes["ix_questions_uuid_btree"].unique is True
    assert (
        indexes["ix_questions_uuid_btree"].dialect_options["postgresql"]["using"]
        == "btree"
    )

    assert "ix_questions_exam_id_btree" in indexes
    assert (
        indexes["ix_questions_exam_id_btree"].dialect_options["postgresql"]["using"]
        == "btree"
    )


def test_exam_question_relationship():
    exam = Exam(type="OAB", year=2024)
    question = Question(
        uuid="550e8400-e29b-41d4-a716-446655440000",
        number=1,
        statement="Enunciado",
        choices=["A", "B"],
        labels_choices=["A", "B"],
        correct_label_choice="A",
        exam=exam,
    )

    assert question.exam is exam
    assert exam.questions == [question]
