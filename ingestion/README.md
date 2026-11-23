# Módulo `ingestion`

Responsável pela camada de ingestão do sistema, padronizando o fluxo de **extração**, **normalização** e **persistência** de provas e questões no banco de dados.

## Responsabilidade

Fornecer o contrato comum que todas as implementações concretas de ingestão (ex.: OAB, ENEM e outros exames) devem seguir, garantindo separação clara entre:

1. **Extração (`extract`)**: obtenção dos dados brutos da fonte de origem (sem parâmetros de entrada).
2. **Normalização (`normalize`)**: transformação e limpeza dos dados extraídos (`dict[str, Any]` -> `dict[str, Any]`).
3. **Persistência (`save`)**: gravação dos dados normalizados (`dict[str, Any]`) utilizando os repositórios `Exam` e `Question` do módulo `database`.

## Componentes

- **`BaseIngestion`** (`ingestion/base_ingestion.py`): classe abstrata (`ABC`) que define os métodos abstratos obrigatórios:
  - `extract(self) -> dict[str, Any]`
  - `normalize(self, data: dict[str, Any]) -> dict[str, Any]`
  - `save(self, data: dict[str, Any], exam: Exam, question: Question) -> None`
- **`oab_ingestion`** (`ingestion/oab_ingestion/oab_ingestion.py`): submódulo com a implementação `OABIngestion(BaseIngestion)` para ingestão de questões da OAB a partir do dataset Parquet `eduagarcia/oab_exams`.
  - Nesta etapa, apenas o método `extract()` está implementado (carregando o arquivo Parquet via `pandas`/`pyarrow`).
  - Os métodos `normalize()` e `save()` levantam `NotImplementedError` e serão implementados em tarefas futuras.
