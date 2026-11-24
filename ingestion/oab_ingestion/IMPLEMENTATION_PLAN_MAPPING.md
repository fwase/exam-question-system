# Plano de Implementação — Mapeamento e Persistência de Questões da OAB (`ingestion.oab_ingestion`)

Este plano segue a skill `create-implementation-plan-skill`, dividindo a entrega da tarefa **"[Ingestão] Mapeamento de questões da OAB para o banco de dados"** em fases pequenas, incrementais e verificáveis.

## Contexto e Decisões

- **Contexto**: O dataset da OAB extraído em `OABIngestion.extract()` está em formato Parquet e precisa ser mapeado e normalizado para o schema do banco de dados PostgreSQL (`exams` e `questions`), permitindo a inserção completa de cada exame (`exam_id`) com suas respectivas questões.
- **Decisões**:
  - Criar um módulo de enums na raiz do projeto contendo o enum de tipo de exame (`ExamType`) com o valor `OAB`, utilizando esse enum para preencher `exams.type`.
  - Extrair `exams.version` a partir de `exam_id` fazendo split por `"-"` e obtendo a última posição (ex.: `"2010-01"` -> `"01"`).
  - Criar um registro distinto na tabela `exams` para cada `exam_id` único e associar todas as suas questões correspondentes na tabela `questions` via `exam_id`, garantindo que seja possível recuperar no banco o exame e suas questões equivalentes.
  - Concentrar a lógica de transformação e mapeamento na camada `normalize`, estruturando os dados prontos para persistência no PostgreSQL na camada `save` (utilizando os repositórios `Exam` e `Question` de `database.repository`).

---

## [x] Fase 1: Módulo de Enum na raiz do projeto (`ExamType`) — **Feito**

- **Objetivo**: Criar o pacote/módulo de enums na raiz do projeto definindo `ExamType` com o membro `OAB`.
- **Arquivos/Módulos**:
  - `enums/__init__.py`
  - `enums/exam_type.py` (ou definição centralizada exportada em `enums/__init__.py`)
- **Passos**:
  1. [x] Criar a pasta `enums/` na raiz do projeto.
  2. [x] Definir `ExamType(str, Enum)` (ou `StrEnum`) com `OAB = "OAB"`.
  3. [x] Exportar `ExamType` em `enums/__init__.py`.
- **Critério de validação**:
  - [x] Executar `poetry run python -c "from enums import ExamType; assert ExamType.OAB == 'OAB' and ExamType.OAB.value == 'OAB'"` sem erros.

---

## [x] Fase 2: Mapeamento e normalização em `OABIngestion.normalize` — **Feito**

- **Objetivo**: Implementar `OABIngestion.normalize(self, data: dict[str, Any]) -> dict[str, Any]` realizando o mapeamento completo das colunas do Parquet para o schema de `exams` e `questions`, agrupando as questões por exame (`exam_id`).
- **Arquivos/Módulos**:
  - `ingestion/oab_ingestion/oab_ingestion.py`
- **Passos**:
  1. [x] Validar a estrutura de entrada (`records`) recebida de `extract()`.
  2. [x] Para cada registro, extrair `exams.year` a partir de `exam_year` (como `int`), `exams.version` a partir de `exam_id.split("-")[-1]` e `exams.type` como `ExamType.OAB.value`.
  3. [x] Mapear os campos de questão para o schema de `questions`:
     - `question_number` -> `number` (`int`)
     - `question_type` -> `theme` (`str | None`)
     - `question` -> `statement` (`str`)
     - `choices.text` (tratando estruturas `dict`/`list`/`ndarray` do Parquet) -> `choices` (`list[str]`)
     - `choices.label` -> `labels_choices` (`list[str]`)
     - `answerKey` -> `correct_label_choice` (`str`)
     - Gerar `uuid` único (ex.: determinístico via `uuid5` a partir de `exam_id` e `question_number` ou `uuid4`) para atender à coluna obrigatória `questions.uuid`.
  4. [x] Agrupar os registros normalizados por `exam_id`, retornando um dicionário estruturado com os exames distintos e suas respectivas listas de questões prontas para a camada `save`.
- **Critério de validação**:
  - [x] Executar um script rápido com `poetry run python -c ...` passando registros simulados do Parquet para `OABIngestion().normalize(...)` e verificar que cada `exam_id` gera um exame único com `type == "OAB"`, `version` extraída corretamente e todas as questões mapeadas.

---

## [x] Fase 3: Persistência no PostgreSQL em `OABIngestion.save` — **Feito**

- **Objetivo**: Implementar `OABIngestion.save(self, data: dict[str, Any], exam: Exam, question: Question) -> None` para gravar no PostgreSQL todos os exames e suas questões associadas a partir do resultado de `normalize()`.
- **Arquivos/Módulos**:
  - `ingestion/oab_ingestion/oab_ingestion.py`
- **Passos**:
  1. [x] Percorrer os exames normalizados retornados por `normalize()`.
  2. [x] Para cada exame, criar ou recuperar o registro correspondente na tabela `exams` via `exam.get_or_create(type=..., year=..., version=...)`, obtendo o `exam_id` persistido.
  3. [x] Instanciar os modelos `QuestionModel` com `exam_id` vinculado ao exame recém-criado/recuperado e persistir em lote via `question.create_many(...)` (evitando duplicidades por `uuid` caso necessário).
  4. [x] Garantir que, ao final da execução, cada `exam_id` (ex.: `2010-01`, `2010-02`) tenha seu registro em `exams` e todas as suas questões recuperáveis via `question.list_by_exam_id(exam_id)`.
- **Critério de validação**:
  - [x] Com o banco PostgreSQL ativo (`make db-up`), executar o fluxo `extract -> normalize -> save` (ou com amostra controlada) e confirmar via `Exam().list_all()` e `Question().list_by_exam_id(...)` que os exames e suas questões equivalentes são recuperados corretamente.

---

## [x] Fase 4: Testes unitários e de contrato (`tests/`) — **Feito**

- **Objetivo**: Cobrir com testes automatizados o novo módulo `enums`, o mapeamento/agrupamento em `OABIngestion.normalize()` e a persistência em `OABIngestion.save()`.
- **Arquivos/Módulos**:
  - `tests/enums/test_exam_type.py` (ou em `tests/ingestion/test_oab_ingestion.py`)
  - `tests/ingestion/test_oab_ingestion.py`
- **Passos**:
  1. [x] Adicionar testes validando `ExamType.OAB`.
  2. [x] Adicionar testes para `OABIngestion.normalize()` cobrindo:
     - Split de `exam_id` (`"2010-01"` -> `version="01"`).
     - Mapeamento de todos os 8 campos do Parquet para o schema de `exams` e `questions`.
     - Agrupamento correto de múltiplos `exam_id` distintos e suas respectivas questões.
     - Tratamento de `choices` em formato de lista/array.
  3. [x] Adicionar testes para `OABIngestion.save()` (com mocks de `Exam` e `Question` e/ou banco de teste) garantindo que `get_or_create` e `create_many` são chamados com o `exam_id` correto para cada grupo de questões.
  4. [x] Remover/atualizar os testes antigos que esperavam `NotImplementedError` em `normalize` e `save`.
- **Critério de validação**:
  - [x] `make test` executa toda a suíte sem falhas ou regressões.

---

## [ ] Fase 5: Documentação e validação final de cobertura

- **Objetivo**: Atualizar a documentação do módulo `ingestion` e validar testes e cobertura do projeto após todas as alterações.
- **Arquivos/Módulos**:
  - `ingestion/README.md`
- **Passos**:
  1. [ ] Atualizar `ingestion/README.md` documentando o enum `ExamType`, o mapeamento completo Parquet -> PostgreSQL em `OABIngestion.normalize()` e o fluxo de persistência em `OABIngestion.save()`.
  2. [ ] Executar `make test` e `make coverage`.
- **Critério de validação**:
  - [ ] `make test` e `make coverage` finalizam com sucesso, sem falhas ou queda de cobertura inesperada.
