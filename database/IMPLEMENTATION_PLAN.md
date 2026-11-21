# Plano de Implementação — Camada de Banco de Dados (`database`)

Este plano segue a skill `create-implementation-plan-skill`, dividindo a entrega da tarefa **"Definição e implementação da camada de banco de dados"** em fases pequenas, incrementais e verificáveis.

---

## [x] Fase 1: Infraestrutura Docker do PostgreSQL e comandos no `Makefile` — **Feito**

- **Objetivo**: Disponibilizar o banco de dados PostgreSQL local via Docker com as credenciais e porta especificadas, além de comandos no `Makefile` para gerenciar o ciclo de vida do container.
- **Arquivos/Módulos**:
  - `compose.yaml` na raiz do projeto.
  - `Makefile`.
- **Passos**:
  1. [x] Criar o serviço `postgres` no arquivo Compose usando imagem oficial do PostgreSQL (`postgres:17-alpine`), mapeando a porta `5434:5432` para acesso em `localhost:5434`.
  2. [x] Configurar as variáveis de ambiente do container para `POSTGRES_DB=question_system_db`, `POSTGRES_USER=admin` e `POSTGRES_PASSWORD=admin_123`, com volume persistente (`postgres_data`) e `healthcheck` (`pg_isready`).
  3. [x] Adicionar no `Makefile` os targets `db-up` e `db-down` para subir e derrubar o banco de dados.
- **Critério de validação**:
  - [x] Executar `make db-up` e confirmar que o container inicia com status saudável (`healthy`) e aceita conexão em `localhost:5434` com `question_system_db` / `admin`.
  - [x] Executar `make db-down` e confirmar que o container é encerrado corretamente.

---

## [x] Fase 2: Dependências Python e estrutura de diretórios do módulo `database` — **Feito**

- **Objetivo**: Instalar as dependências de ORM/migrations e estruturar os submódulos dentro de `database/`, isolando o banco de exames e questões (permitindo outros bancos no futuro) e a camada de repositório.
- **Arquivos/Módulos**:
  - `pyproject.toml` e `poetry.lock`.
  - `database/__init__.py`
  - `database/exams_questions/__init__.py`
  - `database/exams_questions/config/__init__.py`
  - `database/exams_questions/migrations/` (`.gitkeep`)
  - `database/exams_questions/models/__init__.py`
  - `database/repository/__init__.py`
- **Passos**:
  1. [x] Adicionar `sqlalchemy`, `alembic` e o driver PostgreSQL (`psycopg[binary]`) via Poetry.
  2. [x] Criar o submódulo `database/exams_questions/` contendo as três pastas obrigatórias: `config/`, `migrations/` e `models/`.
  3. [x] Criar o submódulo `database/repository/` para concentrar o acesso aos dados.
- **Critério de validação**:
  - [x] `make install` (ou `poetry install --no-root`) conclui sem erros.
  - [x] Imports básicos dos novos pacotes (`database.exams_questions.config`, `database.exams_questions.models`, `database.repository`) funcionam via `poetry run python`.

---

## [x] Fase 3: Configuração do ORM e Entrypoint Singleton (`config/`) — **Feito**

- **Objetivo**: Configurar a conexão com o PostgreSQL via SQLAlchemy e implementar o entrypoint Singleton para recuperação da instância do banco de dados.
- **Arquivos/Módulos**:
  - `database/exams_questions/config/database.py`
  - `database/exams_questions/config/__init__.py`
  - `tests/database/test_database_singleton.py`
- **Passos**:
  1. [x] Definir a URL de conexão padrão apontando para `postgresql+psycopg://admin:admin_123@localhost:5434/question_system_db` (permitindo sobrescrita por variável de ambiente `DATABASE_URL`).
  2. [x] Criar a base declarativa (`Base`) do SQLAlchemy e a configuração de `Engine` e `session_factory` (`Session`).
  3. [x] Implementar a classe Singleton (`ExamsQuestionsDatabase`) responsável por gerenciar o acesso ao banco de dados e expor o entrypoint `get_database()` para recuperar a instância do banco de dados / sessão.
  4. [x] Criar testes unitários validando o comportamento Singleton (mesma instância em múltiplas chamadas).
- **Critério de validação**:
  - [x] `make test` executa `tests/database/test_database_singleton.py` com sucesso.
  - [x] Com `make db-up` ativo, um smoke test executando `SELECT 1` através do entrypoint Singleton responde sem erros.

---

## [x] Fase 4: Mapeamento das Entidades ORM e Índices B-tree (`models/`) — **Feito**

- **Objetivo**: Mapear as entidades `Exam` e `Question` no SQLAlchemy conforme o diagrama `database/desenho_esquema.excalidraw`, incluindo chaves, relacionamentos e índices B-tree.
- **Arquivos/Módulos**:
  - `database/exams_questions/models/exam.py`
  - `database/exams_questions/models/question.py`
  - `database/exams_questions/models/__init__.py`
  - `tests/database/test_models.py`
- **Passos**:
  1. [x] Mapear a entidade `Exam` como classe ORM com campos via `Column(...)`:
     - `id` (`Integer`, `primary_key=True`)
     - `type` (`String(20)`)
     - `year` (`Integer`)
     - `examining_board` (`String(100)`)
     - `subject` (`String(100)`)
     - `state` (`String(20)`)
     - `job_title` (`String(100)`)
  2. [x] Mapear a entidade `Question` como classe ORM com campos via `Column(...)`:
     - `id` (`Integer`, `primary_key=True`)
     - `uuid` (`String(36)`, com índice B-tree único)
     - `number` (`Integer`)
     - `theme` (`String(100)`)
     - `statement` (`Text`)
     - `choices` (`ARRAY(Text)`)
     - `labels_choices` (`ARRAY(String(5))`)
     - `correct_label_choice` (`String(5)`)
     - `exam_id` (`Integer`, `ForeignKey("exams.id")`, com índice B-tree, representando a relação indicada no esquema).
  3. [x] Garantir criação explícita de índices B-tree (`postgresql_using="btree"`) nos campos indexados conforme definido nas decisões.
  4. [x] Adicionar testes unitários verificando colunas, tipos, constraints e índices declarados no `Base.metadata`.
- **Critério de validação**:
  - [x] `make test` passa validando o schema ORM em `tests/database/test_models.py`.

---

## [x] Fase 5: Configuração do Alembic e Migration `v1` (`migrations/`) — **Feito**

- **Objetivo**: Configurar o Alembic para gerenciar o versionamento do banco e gerar a migration `v1` criando as tabelas e índices no PostgreSQL.
- **Arquivos/Módulos**:
  - `alembic.ini`
  - `database/exams_questions/migrations/env.py`
  - `database/exams_questions/migrations/script.py.mako`
  - `database/exams_questions/migrations/versions/0001_v1_initial_schema.py`
- **Passos**:
  1. [x] Inicializar/configurar o Alembic apontando `script_location` para `database/exams_questions/migrations` e `target_metadata` para o `Base.metadata` dos modelos ORM.
  2. [x] Gerar a migration `v1` contemplando a criação das tabelas de `Exam` e `Question`, chaves estrangeiras, constraints de unicidade e índices B-tree.
  3. [x] Testar aplicação (`upgrade`) e reversão (`downgrade`) da migration contra o banco Docker.
- **Critério de validação**:
  - [x] Executar `poetry run alembic upgrade head` com `make db-up` ativo e confirmar no PostgreSQL que as tabelas, colunas, constraints e índices B-tree foram criados.
  - [x] Executar `poetry run alembic downgrade base` e novamente `upgrade head` sem erros.

---

## [x] Fase 6: Camada de Repositório (`repository/`) e Testes de Integração — **Feito**

- **Objetivo**: Implementar o submódulo `repository/` para encapsular operações de leitura e escrita de `Exam` e `Question` usando o entrypoint Singleton.
- **Arquivos/Módulos**:
  - `database/repository/exam_repository.py`
  - `database/repository/question_repository.py`
  - `database/repository/__init__.py`
  - `tests/database/test_repositories.py`
- **Passos**:
  1. [x] Implementar os repositórios de `Exam` e `Question` consumindo o Singleton de banco de dados de `database/exams_questions/config`.
  2. [x] Implementar operações básicas de criação/inserção e consulta necessárias para o fluxo inicial de ingestão.
  3. [x] Escrever testes unitários/integração validando inserção, consulta e integridade referencial entre `Exam` e `Question`.
- **Critério de validação**:
  - [x] `make test` e `make coverage` executam com sucesso cobrindo config, models e repositories.
