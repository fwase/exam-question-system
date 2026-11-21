import pytest
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from database.exams_questions.config import ExamsQuestionsDatabase, get_database
from database.exams_questions.models import Exam, Question
from database.repository import ExamRepository, QuestionRepository


@pytest.fixture()
def clean_db():
    ExamsQuestionsDatabase.reset_instance()
    db = get_database()
    with db.session_scope() as session:
        session.execute(delete(Question))
        session.execute(delete(Exam))
    yield db
    with db.session_scope() as session:
        session.execute(delete(Question))
        session.execute(delete(Exam))
    ExamsQuestionsDatabase.reset_instance()


def test_exam_repository_crud_and_get_or_create(clean_db):
    repo = ExamRepository()

    created = repo.create(
        Exam(
            type="OAB",
            year=2024,
            examining_board="FGV",
            subject="Direito Constitucional",
            state="BR",
            job_title="Advogado",
        )
    )
    assert created.id is not None

    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.type == "OAB"
    assert fetched.year == 2024

    same = repo.get_or_create(
        type="OAB",
        year=2024,
        examining_board="FGV",
        subject="Direito Constitucional",
        state="BR",
        job_title="Advogado",
    )
    assert same.id == created.id

    other = repo.get_or_create(type="OAB", year=2023, examining_board="FGV")
    assert other.id != created.id
    assert len(repo.list_all()) == 2


def test_question_repository_crud_and_referential_integrity(clean_db):
    exam_repo = ExamRepository()
    question_repo = QuestionRepository()

    exam = exam_repo.create(Exam(type="OAB", year=2024, examining_board="FGV"))

    q1 = question_repo.create(
        Question(
            uuid="550e8400-e29b-41d4-a716-446655440001",
            number=1,
            theme="Ética",
            statement="Enunciado da questão 1",
            choices=["Alt A", "Alt B", "Alt C", "Alt D"],
            labels_choices=["A", "B", "C", "D"],
            correct_label_choice="B",
            exam_id=exam.id,
        )
    )
    assert q1.id is not None

    q2_list = question_repo.create_many(
        [
            Question(
                uuid="550e8400-e29b-41d4-a716-446655440002",
                number=2,
                theme="Civil",
                statement="Enunciado da questão 2",
                choices=["Alt A", "Alt B"],
                labels_choices=["A", "B"],
                correct_label_choice="A",
                exam_id=exam.id,
            )
        ]
    )
    assert len(q2_list) == 1
    assert question_repo.create_many([]) == []

    by_id = question_repo.get_by_id(q1.id)
    assert by_id is not None
    assert by_id.uuid == q1.uuid

    by_uuid = question_repo.get_by_uuid("550e8400-e29b-41d4-a716-446655440002")
    assert by_uuid is not None
    assert by_uuid.number == 2

    by_exam = question_repo.list_by_exam_id(exam.id)
    assert [q.number for q in by_exam] == [1, 2]

    with pytest.raises(IntegrityError):
        question_repo.create(
            Question(
                uuid="550e8400-e29b-41d4-a716-446655440001",
                number=3,
                statement="UUID duplicado",
                choices=["A", "B"],
                labels_choices=["A", "B"],
                correct_label_choice="A",
                exam_id=exam.id,
            )
        )

    with pytest.raises(IntegrityError):
        question_repo.create(
            Question(
                uuid="550e8400-e29b-41d4-a716-446655440099",
                number=4,
                statement="Exam inexistente",
                choices=["A", "B"],
                labels_choices=["A", "B"],
                correct_label_choice="A",
                exam_id=999999,
            )
        )
