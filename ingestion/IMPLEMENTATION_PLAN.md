# Plano de Implementação — Camada de Ingestão (`ingestion`)

Este plano segue a skill `create-implementation-plan-skill`, dividindo a entrega da tarefa **"[Ingestão] Adicionar camada de ingestão"** em fases pequenas, incrementais e verificáveis.

## Contexto e Decisões

- **Contexto**: Antes de adicionar processos concretos de ingestão (como a ingestão de dados da OAB no banco de dados), é necessário criar a camada base de ingestão.
- **Decisões**:
  - Criar um novo módulo chamado `ingestion`.
  - Definir a classe abstrata `BaseIngestion` (`base_ingestion.py`) com os métodos abstratos `extract`, `normalize` e `save`.
  - Criar `ingestion/README.md` descrevendo a responsabilidade do módulo e seus componentes (neste primeiro instante, apenas o componente base, sem implementações reais).

---

## [x] Fase 1: Estrutura inicial do módulo `ingestion` e classe abstrata `BaseIngestion` — **Feito**

- **Objetivo**: Criar o pacote `ingestion` e definir a classe abstrata base (`BaseIngestion`) com os métodos abstratos `extract`, `normalize` e `save` e suas respectivas assinaturas.
- **Arquivos/Módulos**:
  - `ingestion/__init__.py`
  - `ingestion/base_ingestion.py`
- **Passos**:
  1. [x] Criar `ingestion/base_ingestion.py` definindo a classe abstrata `BaseIngestion(ABC)` com os métodos abstratos (`@abstractmethod`):
     - `extract(self) -> dict[str, Any]` (sem parâmetros de entrada além de `self`).
     - `normalize(self, data: dict[str, Any]) -> dict[str, Any]` (entrada e saída `dict[str, Any]`).
     - `save(self, data: dict[str, Any], exam: Exam, question: Question) -> None` (recebendo `exam`, `question` — repositórios de `database.repository` — além de `dict[str, Any]`).
  2. [x] Criar `ingestion/__init__.py` exportando `BaseIngestion`.
- **Critério de validação**:
  - [x] Executar `poetry run python -c "from ingestion import BaseIngestion; from ingestion.base_ingestion import BaseIngestion"` sem erros e confirmar que `BaseIngestion` é abstrata (`ABC` com os três métodos em `__abstractmethods__`).

---

## [x] Fase 2: Testes unitários do contrato da classe abstrata `BaseIngestion` — **Feito**

- **Objetivo**: Garantir via testes unitários que `BaseIngestion` impõe o contrato abstrato (`extract`, `normalize` e `save`) às subclasses e suporta o fluxo esperado de parâmetros e retornos.
- **Arquivos/Módulos**:
  - `tests/ingestion/test_base_ingestion.py`
- **Passos**:
  1. [x] Adicionar teste verificando que instanciar `BaseIngestion` diretamente levanta `TypeError`.
  2. [x] Adicionar teste verificando que subclasses incompletas (omitindo qualquer um dos métodos `extract`, `normalize` ou `save`) também levantam `TypeError` ao serem instanciadas.
  3. [x] Adicionar teste com uma subclasse concreta mínima (dublê de teste) implementando os três métodos para validar a chamada de `extract()`, `normalize(dict[str, Any])` e `save(dict[str, Any], exam, question)`.
- **Critério de validação**:
  - [x] `make test` executa `tests/ingestion/test_base_ingestion.py` com sucesso, sem regressões na suíte existente.

---

## [x] Fase 3: Documentação do módulo (`ingestion/README.md`) — **Feito**

- **Objetivo**: Documentar a responsabilidade do módulo `ingestion` e os seus componentes atuais.
- **Arquivos/Módulos**:
  - `ingestion/README.md`
- **Passos**:
  1. [x] Criar `ingestion/README.md` explicando a responsabilidade do módulo `ingestion` (definir a camada de ingestão responsável por extrair, normalizar e persistir dados de provas/questões no banco de dados).
  2. [x] Listar os componentes do módulo, deixando explícito que neste primeiro momento existe apenas o componente base (`BaseIngestion` em `base_ingestion.py`), sem implementações reais.
- **Critério de validação**:
  - [x] Revisar `ingestion/README.md` garantindo clareza sobre responsabilidade, contrato dos métodos e ausência de implementações concretas nesta etapa.

---

## [x] Fase 4: Validação final de testes e cobertura — **Feito**

- **Objetivo**: Confirmar que toda a suíte de testes e o relatório de cobertura do projeto executam sem erros após a adição do módulo `ingestion`.
- **Arquivos/Módulos**:
  - `ingestion/`
  - `tests/ingestion/`
- **Passos**:
  1. [x] Executar a suíte completa de testes (`make test`).
  2. [x] Executar o relatório de cobertura (`make coverage`) verificando a cobertura do módulo `ingestion/`.
- **Critério de validação**:
  - [x] `make test` e `make coverage` finalizam sem erros ou regressões.
