from typing import Any
from unittest.mock import MagicMock

import pytest

from database.repository import Exam, Question
from ingestion import BaseIngestion


def test_base_ingestion_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        BaseIngestion()  # type: ignore[abstract]


def test_incomplete_subclasses_cannot_be_instantiated() -> None:
    class MissingSave(BaseIngestion):
        def extract(self) -> dict[str, Any]:
            return {}

        def normalize(self, data: dict[str, Any]) -> dict[str, Any]:
            return data

    class MissingNormalize(BaseIngestion):
        def extract(self) -> dict[str, Any]:
            return {}

        def save(self, data: dict[str, Any], exam: Exam, question: Question) -> None:
            return None

    class MissingExtract(BaseIngestion):
        def normalize(self, data: dict[str, Any]) -> dict[str, Any]:
            return data

        def save(self, data: dict[str, Any], exam: Exam, question: Question) -> None:
            return None

    for cls in (MissingSave, MissingNormalize, MissingExtract):
        with pytest.raises(TypeError):
            cls()  # type: ignore[abstract]


def test_concrete_subclass_implements_contract() -> None:
    class DummyIngestion(BaseIngestion):
        def __init__(self) -> None:
            self.saved: tuple[dict[str, Any], Exam, Question] | None = None

        def extract(self) -> dict[str, Any]:
            return {"raw": "value"}

        def normalize(self, data: dict[str, Any]) -> dict[str, Any]:
            return {"normalized": data["raw"].upper()}

        def save(self, data: dict[str, Any], exam: Exam, question: Question) -> None:
            self.saved = (data, exam, question)

    pipeline = DummyIngestion()
    exam_repo = MagicMock(spec=Exam)
    question_repo = MagicMock(spec=Question)

    extracted = pipeline.extract()
    normalized = pipeline.normalize(extracted)
    pipeline.save(normalized, exam_repo, question_repo)

    assert extracted == {"raw": "value"}
    assert normalized == {"normalized": "VALUE"}
    assert pipeline.saved == ({"normalized": "VALUE"}, exam_repo, question_repo)
