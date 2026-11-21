# Exam Question System

Sistema de consulta de questões de provas em linguagem natural, reunindo questões de concursos, OAB, ENEM e outros exames.

## Escopo Inicial

No primeiro momento, o sistema trabalhará apenas com questões da **OAB**.

## Arquitetura

O sistema inicial será um **monólito dividido em módulos**:

- **Cadastro de usuário**: gerenciamento de usuários da plataforma.
- **Consulta de questões**: busca de questões em linguagem natural.
- **Extração e cadastro de questões**: extração e persistência das questões na base.
- **Geração de embeddings das questões**: criação de representações vetoriais das questões para suportar a busca semântica.
- **Banco de dados (`database`)**: responsável pela comunicação com o banco de dados.

## Fase Atual

O foco inicial do desenvolvimento está no fluxo de **extração e cadastro de questões**. Os demais módulos serão implementados em seguida, em ordem ainda a definir.

### Fluxo de Extração e Cadastro de Questões

1. **Extração de base de dados**
2. **Normalização e limpeza de ruídos** (se necessário)
3. **Cadastro no banco de dados**

## Tecnologias

- **Python**: `3.14.4`
