from collections.abc import Sequence

from sqlalchemy import select

from database.exams_questions.config import ExamsQuestionsDatabase, get_database
from database.exams_questions.models import Question as QuestionModel


class Question:
    """Repositório para operações de persistência e consulta da entidade Question."""

    def __init__(self, db: ExamsQuestionsDatabase | None = None) -> None:
        self._db = db or get_database()

    def create(self, question: QuestionModel) -> QuestionModel:
        """Persiste uma nova questão e retorna a instância atualizada."""
        with self._db.session_scope() as session:
            session.add(question)
            session.flush()
            session.refresh(question)
            return question

    def create_many(self, questions: Sequence[QuestionModel]) -> list[QuestionModel]:
        """Persiste múltiplas questões em uma única transação."""
        items = list(questions)
        if not items:
            return []
        with self._db.session_scope() as session:
            session.add_all(items)
            session.flush()
            for item in items:
                session.refresh(item)
            return items

    def get_by_id(self, question_id: int) -> QuestionModel | None:
        """Busca uma questão pelo seu ID."""
        with self._db.session_scope() as session:
            return session.get(QuestionModel, question_id)

    def get_by_uuid(self, uuid: str) -> QuestionModel | None:
        """Busca uma questão pelo seu UUID único."""
        with self._db.session_scope() as session:
            stmt = select(QuestionModel).where(QuestionModel.uuid == uuid)
            return session.scalars(stmt).first()

    def list_by_exam_id(self, exam_id: int) -> list[QuestionModel]:
        """Lista as questões associadas a um exame ordenadas por número."""
        with self._db.session_scope() as session:
            stmt = (
                select(QuestionModel)
                .where(QuestionModel.exam_id == exam_id)
                .order_by(QuestionModel.number)
            )
            return list(session.scalars(stmt).all())
