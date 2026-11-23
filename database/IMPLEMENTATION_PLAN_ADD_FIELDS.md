# Plano de Implementação — Adicionar Campos no Banco de Dados (`database`)

Este plano segue a skill `create-implementation-plan-skill`, dividindo a entrega da tarefa **"Adicionar campos no banco de dados"** em fases pequenas, incrementais e verificáveis.

## Contexto e Decisão

- **Contexto**: A prova da OAB ocorre mais de 1 vez ao ano, portanto é necessário armazenar a versão da prova além do ano (`year`).
- **Decisão**: Adicionar o campo `version` (`varchar(20)`, anulável) no schema da tabela `exams`, com nova migration no Alembic e validação de execução e registro em `alembic_version`.

---

## [x] Fase 1: Atualização do modelo ORM `Exam` e testes de schema — **Feito**

- **Objetivo**: Adicionar o campo `version` (`String(20)`, `nullable=True`) ao modelo ORM `Exam` e atualizar os testes unitários de schema para validar a nova coluna.
- **Arquivos/Módulos**:
  - `database/exams_questions/models/exam.py`
  - `tests/database/test_models.py`
- **Passos**:
  1. [x] Adicionar a coluna `version = Column(String(20), nullable=True)` na classe `Exam` (`__tablename__ = "exams"`).
  2. [x] Atualizar os testes em `tests/database/test_models.py` para verificar a existência da coluna `version`, seu tipo (`VARCHAR(20)`) e nulabilidade no `Base.metadata`.
- **Critério de validação**:
  - [x] `make test` executa `tests/database/test_models.py` com sucesso.

---

## [x] Fase 2: Geração e validação da migration Alembic (`v2`) — **Feito**

- **Objetivo**: Criar a nova migration no Alembic adicionando a coluna `version` (`varchar(20)`) na tabela `exams` e validar `upgrade`, `downgrade` e `alembic_version` no PostgreSQL.
- **Arquivos/Módulos**:
  - `database/exams_questions/migrations/versions/0002_v2_add_exam_version.py`
- **Passos**:
  1. [x] Criar a revision `0002` com `down_revision = '0001'` contendo `op.add_column('exams', sa.Column('version', sa.String(length=20), nullable=True))` no `upgrade()` e `op.drop_column('exams', 'version')` no `downgrade()`.
  2. [x] Com o banco ativo (`make db-up`), executar `poetry run alembic upgrade head`.
  3. [x] Verificar no PostgreSQL que a coluna `version` (`character varying(20)`) foi criada na tabela `exams` e que a tabela `alembic_version` registra a revisão `0002`.
  4. [x] Testar reversão com `poetry run alembic downgrade 0001` e reaplicação com `poetry run alembic upgrade head`.
- **Critério de validação**:
  - [x] `poetry run alembic current` exibe `0002 (head)` após `upgrade head`, a coluna `version` existe em `exams` e `downgrade`/`upgrade` executam sem erros.

---

## [x] Fase 3: Atualização do repositório `Exam` e testes de repositório — **Feito**

- **Objetivo**: Atualizar o repositório `Exam` (`get_or_create`) para aceitar e filtrar pelo parâmetro opcional `version`, além de cobrir o novo comportamento com testes.
- **Arquivos/Módulos**:
  - `database/repository/exam.py`
  - `tests/database/test_repositories.py`
- **Passos**:
  1. [x] Adicionar o parâmetro keyword-only `version: str | None = None` em `Exam.get_or_create(...)`, incluindo `ExamModel.version == version` na consulta de busca e `version=version` na criação de um novo `ExamModel`.
  2. [x] Atualizar/adicionar testes em `tests/database/test_repositories.py` validando criação, consulta e distinção de exames com mesmo `year` e `version` diferentes.
- **Critério de validação**:
  - [x] `make test` executa `tests/database/test_repositories.py` com sucesso.

---

## [ ] Fase 4: Validação completa da suíte de testes e cobertura

- **Objetivo**: Garantir que toda a suíte de testes e a cobertura do módulo `database` continuem passando após todas as alterações.
- **Arquivos/Módulos**:
  - `database/`
  - `tests/database/`
- **Passos**:
  1. [ ] Executar a suíte completa de testes (`make test`).
  2. [ ] Executar o relatório de cobertura (`make coverage`) verificando os módulos `database/exams_questions/models/`, `database/repository/` e `database/exams_questions/config/`.
- **Critério de validação**:
  - [ ] `make test` e `make coverage` finalizam sem erros ou regressões.
