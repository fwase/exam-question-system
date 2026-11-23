from sqlalchemy import select

from database.exams_questions.config import ExamsQuestionsDatabase, get_database
from database.exams_questions.models import Exam as ExamModel


class Exam:
    """Repositório para operações de persistência e consulta da entidade Exam."""

    def __init__(self, db: ExamsQuestionsDatabase | None = None) -> None:
        self._db = db or get_database()

    def create(self, exam: ExamModel) -> ExamModel:
        """Persiste um novo exame e retorna a instância atualizada."""
        with self._db.session_scope() as session:
            session.add(exam)
            session.flush()
            session.refresh(exam)
            return exam

    def get_by_id(self, exam_id: int) -> ExamModel | None:
        """Busca um exame pelo seu ID."""
        with self._db.session_scope() as session:
            return session.get(ExamModel, exam_id)

    def list_all(self) -> list[ExamModel]:
        """Lista todos os exames cadastrados ordenados por ID."""
        with self._db.session_scope() as session:
            stmt = select(ExamModel).order_by(ExamModel.id)
            return list(session.scalars(stmt).all())

    def get_or_create(
        self,
        *,
        type: str,
        year: int,
        version: str | None = None,
        examining_board: str | None = None,
        subject: str | None = None,
        state: str | None = None,
        job_title: str | None = None,
    ) -> ExamModel:
        """Recupera um exame existente com os mesmos atributos ou cria um novo."""
        with self._db.session_scope() as session:
            stmt = select(ExamModel).where(
                ExamModel.type == type,
                ExamModel.year == year,
                ExamModel.version == version,
                ExamModel.examining_board == examining_board,
                ExamModel.subject == subject,
                ExamModel.state == state,
                ExamModel.job_title == job_title,
            )
            existing = session.scalars(stmt).first()
            if existing is not None:
                return existing

            exam = ExamModel(
                type=type,
                year=year,
                version=version,
                examining_board=examining_board,
                subject=subject,
                state=state,
                job_title=job_title,
            )
            session.add(exam)
            session.flush()
            session.refresh(exam)
            return exam
