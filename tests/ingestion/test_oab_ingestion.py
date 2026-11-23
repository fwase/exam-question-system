from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from database.repository import Exam, Question
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


def test_oab_ingestion_normalize_and_save_raise_not_implemented() -> None:
    pipeline = OABIngestion()
    exam_repo = MagicMock(spec=Exam)
    question_repo = MagicMock(spec=Question)

    with pytest.raises(NotImplementedError):
        pipeline.normalize({"records": [], "total": 0})

    with pytest.raises(NotImplementedError):
        pipeline.save({"records": [], "total": 0}, exam_repo, question_repo)
