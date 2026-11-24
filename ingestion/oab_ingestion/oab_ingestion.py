from typing import Any
from uuid import NAMESPACE_URL, uuid5

import pandas as pd

from database.exams_questions.models import Question as QuestionModel
from database.repository import Exam, Question
from enums import ExamType
from ingestion.base_ingestion import BaseIngestion

DEFAULT_OAB_PARQUET_URL = (
    "https://huggingface.co/datasets/eduagarcia/oab_exams/"
    "resolve/main/data/train-00000-of-00001.parquet"
)


def _to_str_list(values: Any, field_name: str) -> list[str]:
    """Converte sequências ou arrays (ex.: numpy.ndarray) em lista de strings."""
    if values is None or (isinstance(values, float) and pd.isna(values)):
        raise ValueError(f"Campo obrigatório ausente ou nulo: '{field_name}'.")
    if hasattr(values, "tolist"):
        values = values.tolist()
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"Campo '{field_name}' deve ser uma lista ou array.")
    return [str(item) for item in values]


def _extract_choices(record: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Extrai textos e rótulos das alternativas a partir do registro bruto."""
    choices = record.get("choices")
    if isinstance(choices, dict):
        raw_texts = choices.get("text")
        raw_labels = choices.get("label")
    else:
        raw_texts = record.get("choices.text")
        raw_labels = record.get("choices.label")

    return (
        _to_str_list(raw_texts, "choices.text"),
        _to_str_list(raw_labels, "choices.label"),
    )


def _extract_exam_version(exam_id: str) -> str:
    """Extrai a versão do exame a partir da última parte de `exam_id`."""
    version = exam_id.split("-")[-1].strip()
    if not version:
        raise ValueError(f"Valor inválido para 'exam_id': '{exam_id}'.")
    return version


def _normalize_optional_text(value: Any) -> str | None:
    """Normaliza valores textuais opcionais tratando NaN e strings vazias como None."""
    if value is None or pd.isna(value):
        return None
    normalized = str(value).strip()
    return normalized or None


class OABIngestion(BaseIngestion):
    """Processo de ingestão das questões da OAB."""

    def __init__(self, source_url: str = DEFAULT_OAB_PARQUET_URL) -> None:
        self.source_url = source_url

    def extract(self) -> dict[str, Any]:
        """Extrai os dados brutos da base Parquet da OAB."""
        try:
            df = pd.read_parquet(self.source_url, engine="pyarrow")
        except Exception as exc:
            raise RuntimeError(
                f"Falha ao carregar o dataset Parquet da OAB em '{self.source_url}'."
            ) from exc

        return {
            "records": df.to_dict(orient="records"),
            "total": len(df),
        }

    def normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normaliza os dados extraídos para o formato esperado pela persistência."""
        records = data.get("records")
        if not isinstance(records, list):
            raise ValueError("Dados inválidos para normalização: 'records' deve ser uma lista.")

        exams_by_id: dict[str, dict[str, Any]] = {}

        for record in records:
            exam_id = str(record["exam_id"]).strip()
            if exam_id not in exams_by_id:
                exams_by_id[exam_id] = {
                    "exam": {
                        "type": ExamType.OAB.value,
                        "year": int(record["exam_year"]),
                        "version": _extract_exam_version(exam_id),
                    },
                    "questions": [],
                }

            choices, labels_choices = _extract_choices(record)
            question_number = int(record["question_number"])
            question_uuid = str(
                uuid5(NAMESPACE_URL, f"{ExamType.OAB.value}:{exam_id}:{question_number}")
            )

            exams_by_id[exam_id]["questions"].append(
                {
                    "uuid": question_uuid,
                    "number": question_number,
                    "theme": _normalize_optional_text(record.get("question_type")),
                    "statement": str(record["question"]),
                    "choices": choices,
                    "labels_choices": labels_choices,
                    "correct_label_choice": str(record["answerKey"]).strip(),
                }
            )

        exams = list(exams_by_id.values())
        return {
            "exams": exams,
            "total_exams": len(exams),
            "total_questions": sum(len(item["questions"]) for item in exams),
        }

    def save(self, data: dict[str, Any], exam: Exam, question: Question) -> None:
        """Persiste os dados normalizados utilizando os repositórios de exame e questão."""
        exams_data = data.get("exams")
        if not isinstance(exams_data, list):
            raise ValueError("Dados inválidos para persistência: 'exams' deve ser uma lista.")

        for item in exams_data:
            exam_payload = item["exam"]
            persisted_exam = exam.get_or_create(
                type=exam_payload["type"],
                year=exam_payload["year"],
                version=exam_payload["version"],
            )

            existing_uuids = {
                existing.uuid for existing in question.list_by_exam_id(persisted_exam.id)
            }
            new_questions = [
                QuestionModel(
                    uuid=q_data["uuid"],
                    number=q_data["number"],
                    theme=q_data.get("theme"),
                    statement=q_data["statement"],
                    choices=q_data["choices"],
                    labels_choices=q_data["labels_choices"],
                    correct_label_choice=q_data["correct_label_choice"],
                    exam_id=persisted_exam.id,
                )
                for q_data in item.get("questions", [])
                if q_data["uuid"] not in existing_uuids
            ]

            if new_questions:
                question.create_many(new_questions)
