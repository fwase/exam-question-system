from typing import Any

import pandas as pd

from database.repository import Exam, Question
from ingestion.base_ingestion import BaseIngestion

DEFAULT_OAB_PARQUET_URL = (
    "https://huggingface.co/datasets/eduagarcia/oab_exams/"
    "resolve/main/data/train-00000-of-00001.parquet"
)


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
        raise NotImplementedError

    def save(self, data: dict[str, Any], exam: Exam, question: Question) -> None:
        """Persiste os dados normalizados utilizando os repositórios de exame e questão."""
        raise NotImplementedError
