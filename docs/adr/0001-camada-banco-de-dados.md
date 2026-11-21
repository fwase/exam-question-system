# ADR 0001: Definição da Camada de Banco de Dados (`database`)

- **Status**: Aceito
- **Data**: 2026-11-21
- **Contexto**: Task "Definição e implementação da camada de banco de dados" (`Tasks Tracker` — Notion)

## Contexto

O sistema **Exam Question System** está na fase inicial de desenvolvimento (MVP), com foco no fluxo de extração, normalização e cadastro de questões (iniciando pelas questões da OAB). Até o momento, o módulo `database` possui apenas a documentação inicial e o diagrama de entidades (`database/desenho_esquema.excalidraw`) com as entidades `Exam` e `Question`.

É necessário definir a tecnologia de banco de dados, as ferramentas de mapeamento objeto-relacional (ORM) e versionamento de schema, a estratégia de indexação e a organização modular do código de acesso a dados, prevendo também a possível coexistência de outros bancos de dados no futuro.

## Decisões

1. **Banco de Dados Relacional: PostgreSQL**
   - Adotar o **PostgreSQL** como banco de dados principal para exames e questões.
   - Justificativa: baixa volumetria inicial de escrita e acesso, adequação ao MVP, suporte nativo a tipos estruturados como arrays (`ARRAY(Text)`, `ARRAY(String)`) presentes no schema de `Question` e confiabilidade transacional.
   - Em ambiente de desenvolvimento local, será provisionado via Docker em `localhost:5434` (`question_system_db`, usuário `admin`), com comandos de subida e descida centralizados no `Makefile`.

2. **ORM e Gerenciamento de Migrations: SQLAlchemy + Alembic**
   - Adotar **SQLAlchemy** como ORM e **Alembic** para controle de migrations.
   - Justificativa: maturidade, estabilidade e completude do ecossistema para a stack Python.

3. **Estratégia de Indexação: B-tree**
   - Criar índices utilizando a estrutura **B-tree** nos campos indicados no schema (como chaves únicas e chaves estrangeiras de relacionamento).

4. **Organização Modular e Entrypoint Singleton**
   - Isolar o banco de exames e questões em um submódulo dedicado dentro de `database/` (contendo `config/`, `migrations/` e `models/`), permitindo que novos módulos de banco de dados sejam adicionados no futuro sem acoplamento.
   - Separar as operações de acesso a dados em um submódulo próprio `database/repository/`.
   - Expor um entrypoint único de acesso ao banco de dados implementado como **Singleton**.

## Consequências

### Positivas
- Separação clara de responsabilidades entre configuração/infraestrutura, modelos ORM, migrations e repositórios.
- Facilidade para evoluir o schema de forma versionada e reversível via Alembic.
- Ambiente local reproduzível via Docker e `Makefile`, evitando conflitos com instâncias PostgreSQL na porta padrão `5432` (uso da porta `5434`).
- Base preparada para múltiplos bancos de dados no futuro dentro do módulo `database`.

### Negativas / Trade-offs
- O uso de Singleton para o objeto de banco de dados requer cuidado nos testes automatizados para garantir isolamento de sessões/transações entre casos de teste.
- O uso de tipos específicos do PostgreSQL (`ARRAY`) acopla as migrations e modelos ao PostgreSQL, exigindo que testes de integração rodem preferencialmente contra PostgreSQL (ex.: container Docker) em vez de SQLite em memória.
