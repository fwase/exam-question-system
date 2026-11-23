# Plano de Implementação — Ingestão de Questões da OAB (`ingestion.oab_ingestion`)

Este plano segue a skill `create-implementation-plan-skill`, dividindo a entrega da tarefa **"[Ingestão] Adicionar ingestão de questões da OAB no banco de dados"** em fases pequenas, incrementais e verificáveis.

## Contexto e Decisões

- **Contexto**: Após a criação da camada base de ingestão (`BaseIngestion`), é necessário implementar o processo de ingestão das questões da OAB.
- **Decisões**:
  - Criar o submódulo `oab_ingestion` dentro de `ingestion/` (`ingestion/oab_ingestion`), tendo como base a classe abstrata `BaseIngestion` (`ingestion/base_ingestion.py`).
  - Neste primeiro momento, será implementado apenas o carregamento da base de dados Parquet disponível em `https://huggingface.co/datasets/eduagarcia/oab_exams/blob/main/data/train-00000-of-00001.parquet` (utilizando a URL de download direto `/resolve/main/...` para leitura binária com `pandas`/`pyarrow`).
  - A carga deve ser feita dentro do método `extract(self) -> dict[str, Any]`.
  - Os demais métodos abstratos (`normalize` e `save`) ainda não terão implementação funcional nesta etapa (levantando `NotImplementedError`).

---

## [x] Fase 1: Estrutura do submódulo `oab_ingestion` e classe `OABIngestion` — **Feito**

- **Objetivo**: Criar o pacote `ingestion/oab_ingestion` e definir a classe `OABIngestion` herdando de `BaseIngestion`, com as assinaturas de `extract`, `normalize` e `save` e a definição da fonte de dados da OAB.
- **Arquivos/Módulos**:
  - `ingestion/oab_ingestion/__init__.py`
  - `ingestion/oab_ingestion/oab_ingestion.py`
- **Passos**:
  1. [x] Criar `ingestion/oab_ingestion/oab_ingestion.py` definindo `OABIngestion(BaseIngestion)`.
  2. [x] Definir a URL padrão da fonte Parquet da OAB (usando `https://huggingface.co/datasets/eduagarcia/oab_exams/resolve/main/data/train-00000-of-00001.parquet` para download direto do arquivo Parquet, permitindo sobrescrita via parâmetro no `__init__` para facilitar testes).
  3. [x] Declarar os métodos `extract(self) -> dict[str, Any]`, `normalize(self, data: dict[str, Any]) -> dict[str, Any]` e `save(self, data: dict[str, Any], exam: Exam, question: Question) -> None`, deixando `normalize` e `save` com `raise NotImplementedError`.
  4. [x] Criar `ingestion/oab_ingestion/__init__.py` exportando `OABIngestion`.
- **Critério de validação**:
  - [x] Executar `poetry run python -c "from ingestion.oab_ingestion import OABIngestion; from ingestion import BaseIngestion; assert issubclass(OABIngestion, BaseIngestion); OABIngestion()"` sem erros.

---

## [x] Fase 2: Implementação do método `extract` para carga do Parquet da OAB — **Feito**

- **Objetivo**: Implementar o carregamento do dataset Parquet da OAB dentro de `OABIngestion.extract()`, retornando os dados no contrato `dict[str, Any]` definido em `BaseIngestion`.
- **Arquivos/Módulos**:
  - `ingestion/oab_ingestion/oab_ingestion.py`
- **Passos**:
  1. [x] Implementar `extract(self) -> dict[str, Any]` utilizando `pandas.read_parquet(self.source_url, engine="pyarrow")` (dependências `pandas` e `pyarrow` já configuradas no `pyproject.toml`).
  2. [x] Converter o `DataFrame` carregado para uma estrutura serializável em `dict[str, Any]` (ex.: `{"records": df.to_dict(orient="records"), "total": len(df)}`).
  3. [x] Garantir tratamento claro caso ocorra falha de leitura/rede ao carregar o arquivo Parquet.
- **Critério de validação**:
  - [x] Executar `poetry run python -c "from ingestion.oab_ingestion import OABIngestion; data = OABIngestion().extract(); assert isinstance(data, dict) and data['total'] > 0"` confirmando a carga da base da OAB.

---

## [x] Fase 3: Testes unitários do submódulo `oab_ingestion` — **Feito**

- **Objetivo**: Garantir via testes unitários o contrato de `OABIngestion`, o comportamento de `extract()` (de forma determinística e offline via mock) e o comportamento esperado dos métodos ainda não implementados (`normalize` e `save`).
- **Arquivos/Módulos**:
  - `tests/ingestion/test_oab_ingestion.py`
- **Passos**:
  1. [x] Adicionar teste verificando que `OABIngestion` herda de `BaseIngestion` e pode ser instanciada.
  2. [x] Adicionar teste para `OABIngestion.extract()` mockando `pandas.read_parquet`, validando que a URL configurada é passada corretamente e que o retorno segue o formato `dict[str, Any]` esperado.
  3. [x] Adicionar testes verificando que `normalize(...)` e `save(...)` levantam `NotImplementedError`.
- **Critério de validação**:
  - [x] `make test` executa `tests/ingestion/test_oab_ingestion.py` com sucesso, sem regressões na suíte existente.

---

## [x] Fase 4: Documentação e validação final de testes e cobertura — **Feito**

- **Objetivo**: Atualizar a documentação do módulo `ingestion` para refletir o novo submódulo `oab_ingestion` e validar toda a suíte de testes e cobertura do projeto.
- **Arquivos/Módulos**:
  - `ingestion/README.md`
  - `ingestion/oab_ingestion/`
  - `tests/ingestion/`
- **Passos**:
  1. [x] Atualizar `ingestion/README.md` documentando o submódulo `oab_ingestion` (`OABIngestion`), especificando que nesta etapa apenas `extract` está implementado e que `normalize` e `save` serão implementados em tarefas futuras.
  2. [x] Executar `make test` para validar toda a suíte de testes.
  3. [x] Executar `make coverage` para verificar a cobertura do submódulo `ingestion/oab_ingestion/`.
- **Critério de validação**:
  - [x] `make test` e `make coverage` finalizam sem erros ou regressões.
