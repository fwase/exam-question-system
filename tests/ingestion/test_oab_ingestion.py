from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from database.repository import Exam, Question
from enums import ExamType
from ingestion import BaseIngestion
from ingestion.oab_ingestion import OABIngestion
from ingestion.oab_ingestion.oab_ingestion import DEFAULT_OAB_PARQUET_URL


def test_oab_ingestion_inherits_from_base_ingestion() -> None:
    pipeline = OABIngestion()

    assert isinstance(pipeline, BaseIngestion)
    assert pipeline.source_url == DEFAULT_OAB_PARQUET_URL


def test_oab_ingestion_extract_reads_parquet_and_returns_dict() -> None:
    sample_df = pd.DataFrame(
        [
            {"id": 1, "question": "Questão 1"},
            {"id": 2, "question": "Questão 2"},
        ]
    )
    custom_url = "https://example.com/oab.parquet"
    pipeline = OABIngestion(source_url=custom_url)

    with patch("ingestion.oab_ingestion.oab_ingestion.pd.read_parquet", return_value=sample_df) as mock_read:
        result = pipeline.extract()

    mock_read.assert_called_once_with(custom_url, engine="pyarrow")
    assert result == {
        "records": [
            {"id": 1, "question": "Questão 1"},
            {"id": 2, "question": "Questão 2"},
        ],
        "total": 2,
    }


def test_oab_ingestion_extract_raises_runtime_error_on_failure() -> None:
    pipeline = OABIngestion(source_url="https://example.com/invalid.parquet")

    with patch(
        "ingestion.oab_ingestion.oab_ingestion.pd.read_parquet",
        side_effect=OSError("network error"),
    ):
        with pytest.raises(RuntimeError, match="Falha ao carregar o dataset Parquet da OAB"):
            pipeline.extract()


def test_oab_ingestion_normalize_maps_fields_and_groups_by_exam_id() -> None:
    pipeline = OABIngestion()
    raw_data = {
        "records": [
            {
                "exam_year": 2010,
                "exam_id": "2010-01",
                "question_number": 1,
                "question_type": "Ética Profissional",
                "question": "Enunciado da questão 1",
                "choices": {
                    "text": np.array(["Alt A", "Alt B", "Alt C", "Alt D"]),
                    "label": np.array(["A", "B", "C", "D"]),
                },
                "answerKey": "A",
            },
            {
                "exam_year": 2010,
                "exam_id": "2010-01",
                "question_number": 2,
                "question_type": float("nan"),
                "question": "Enunciado da questão 2",
                "choices": {
                    "text": ["Alt A2", "Alt B2"],
                    "label": ["A", "B"],
                },
                "answerKey": "B",
            },
            {
                "exam_year": 2010,
                "exam_id": "2010-02",
                "question_number": 1,
                "question_type": "Direito Civil",
                "question": "Enunciado da questão 3",
                "choices.text": ["Alt A3", "Alt B3"],
                "choices.label": ["A", "B"],
                "answerKey": "A",
            },
        ],
        "total": 3,
    }

    normalized = pipeline.normalize(raw_data)

    assert normalized["total_exams"] == 2
    assert normalized["total_questions"] == 3

    first_group = normalized["exams"][0]
    assert first_group["exam"] == {
        "type": ExamType.OAB.value,
        "year": 2010,
        "version": "01",
    }
    assert len(first_group["questions"]) == 2
    q1, q2 = first_group["questions"]
    assert q1["number"] == 1
    assert q1["theme"] == "Ética Profissional"
    assert q1["statement"] == "Enunciado da questão 1"
    assert q1["choices"] == ["Alt A", "Alt B", "Alt C", "Alt D"]
    assert q1["labels_choices"] == ["A", "B", "C", "D"]
    assert q1["correct_label_choice"] == "A"
    assert len(q1["uuid"]) == 36
    assert q2["theme"] is None

    second_group = normalized["exams"][1]
    assert second_group["exam"] == {
        "type": ExamType.OAB.value,
        "year": 2010,
        "version": "02",
    }
    assert len(second_group["questions"]) == 1
    assert second_group["questions"][0]["uuid"] != q1["uuid"]


def test_oab_ingestion_normalize_validates_input() -> None:
    pipeline = OABIngestion()

    with pytest.raises(ValueError, match="records"):
        pipeline.normalize({"records": None})

    with pytest.raises(ValueError, match="exam_id"):
        pipeline.normalize(
            {
                "records": [
                    {
                        "exam_year": 2010,
                        "exam_id": "2010-",
                        "question_number": 1,
                        "question": "Q",
                        "choices": {"text": ["A"], "label": ["A"]},
                        "answerKey": "A",
                    }
                ]
            }
        )

    with pytest.raises(ValueError, match="ausente ou nulo"):
        pipeline.normalize(
            {
                "records": [
                    {
                        "exam_year": 2010,
                        "exam_id": "2010-01",
                        "question_number": 1,
                        "question": "Q",
                        "choices": {"text": None, "label": ["A"]},
                        "answerKey": "A",
                    }
                ]
            }
        )

    with pytest.raises(ValueError, match="lista ou array"):
        pipeline.normalize(
            {
                "records": [
                    {
                        "exam_year": 2010,
                        "exam_id": "2010-01",
                        "question_number": 1,
                        "question": "Q",
                        "choices": {"text": "not-a-list", "label": ["A"]},
                        "answerKey": "A",
                    }
                ]
            }
        )


def test_oab_ingestion_save_persists_exams_and_questions_without_duplicates() -> None:
    pipeline = OABIngestion()
    exam_repo = MagicMock(spec=Exam)
    question_repo = MagicMock(spec=Question)

    exam_repo.get_or_create.side_effect = [
        SimpleNamespace(id=10),
        SimpleNamespace(id=20),
    ]
    question_repo.list_by_exam_id.side_effect = [
        [SimpleNamespace(uuid="uuid-existing")],
        [],
    ]

    normalized_data = {
        "exams": [
            {
                "exam": {"type": "OAB", "year": 2010, "version": "01"},
                "questions": [
                    {
                        "uuid": "uuid-existing",
                        "number": 1,
                        "theme": "Ética",
                        "statement": "Q1",
                        "choices": ["A", "B"],
                        "labels_choices": ["A", "B"],
                        "correct_label_choice": "A",
                    },
                    {
                        "uuid": "uuid-new-1",
                        "number": 2,
                        "theme": None,
                        "statement": "Q2",
                        "choices": ["A", "B"],
                        "labels_choices": ["A", "B"],
                        "correct_label_choice": "B",
                    },
                ],
            },
            {
                "exam": {"type": "OAB", "year": 2010, "version": "02"},
                "questions": [
                    {
                        "uuid": "uuid-new-2",
                        "number": 1,
                        "theme": "Civil",
                        "statement": "Q3",
                        "choices": ["A", "B"],
                        "labels_choices": ["A", "B"],
                        "correct_label_choice": "A",
                    }
                ],
            },
        ]
    }

    pipeline.save(normalized_data, exam_repo, question_repo)

    assert exam_repo.get_or_create.call_count == 2
    exam_repo.get_or_create.assert_any_call(type="OAB", year=2010, version="01")
    exam_repo.get_or_create.assert_any_call(type="OAB", year=2010, version="02")

    assert question_repo.create_many.call_count == 2
    first_batch = question_repo.create_many.call_args_list[0].args[0]
    assert len(first_batch) == 1
    assert first_batch[0].uuid == "uuid-new-1"
    assert first_batch[0].exam_id == 10

    second_batch = question_repo.create_many.call_args_list[1].args[0]
    assert len(second_batch) == 1
    assert second_batch[0].uuid == "uuid-new-2"
    assert second_batch[0].exam_id == 20


def test_oab_ingestion_save_validates_input() -> None:
    pipeline = OABIngestion()
    exam_repo = MagicMock(spec=Exam)
    question_repo = MagicMock(spec=Question)

    with pytest.raises(ValueError, match="exams"):
        pipeline.save({"exams": None}, exam_repo, question_repo)
