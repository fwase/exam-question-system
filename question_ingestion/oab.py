from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

from question_ingestion.base import BaseQuestionPipeline

OAB_PARQUET_URL = (
    "https://huggingface.co/datasets/eduagarcia/oab_exams/resolve/main/data/"
    "train-00000-of-00001.parquet"
)


class OABQuestionPipeline(BaseQuestionPipeline):
    """Pipeline de extração, normalização e cadastro de questões da OAB."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        if output_dir is None:
            self.output_dir = Path(__file__).resolve().parent / "data" / "oab"
        else:
            self.output_dir = Path(output_dir)

    def extract(self) -> Path:
        """Faz o download do arquivo Parquet da OAB e retorna o caminho local."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / "train-00000-of-00001.parquet"
        urlretrieve(OAB_PARQUET_URL, output_path)
        return output_path

    def normalize(self, raw_data: Any) -> Any:
        """Normaliza e limpa ruídos dos dados extraídos da OAB."""
        return None

    def save(self, normalized_data: Any) -> None:
        """Cadastra as questões normalizadas da OAB no banco de dados."""
        return None
