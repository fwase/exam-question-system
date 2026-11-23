from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.exams_questions.config import Base


class Exam(Base):
    """Entidade ORM que representa uma prova/exame."""

    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    version = Column(String(20), nullable=True)
    examining_board = Column(String(100), nullable=True)
    subject = Column(String(100), nullable=True)
    state = Column(String(20), nullable=True)
    job_title = Column(String(100), nullable=True)

    questions = relationship(
        "Question",
        back_populates="exam",
        cascade="all, delete-orphan",
    )
