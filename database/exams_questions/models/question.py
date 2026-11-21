from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from database.exams_questions.config import Base


class Question(Base):
    """Entidade ORM que representa uma questão vinculada a um exame."""

    __tablename__ = "questions"
    __table_args__ = (
        Index("ix_questions_uuid_btree", "uuid", unique=True, postgresql_using="btree"),
        Index("ix_questions_exam_id_btree", "exam_id", postgresql_using="btree"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), nullable=False)
    number = Column(Integer, nullable=False)
    theme = Column(String(100), nullable=True)
    statement = Column(Text, nullable=False)
    choices = Column(ARRAY(Text), nullable=False)
    labels_choices = Column(ARRAY(String(5)), nullable=False)
    correct_label_choice = Column(String(5), nullable=False)
    exam_id = Column(
        Integer,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
    )

    exam = relationship("Exam", back_populates="questions")
