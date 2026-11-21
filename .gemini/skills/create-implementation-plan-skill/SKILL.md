---
name: create-implementation-plan-skill
description: Create implementation plan skill — cria um plano de implementação em fases pequenas e bem definidas, escolhendo a quantidade adequada de fases.
---

# Create implementation plan skill

Ao planejar a implementação de uma funcionalidade, correção ou refatoração neste projeto, siga as diretrizes abaixo:

1. **Dividir em fases pequenas**:
   - Quebre a implementação em quantas fases forem necessárias para que cada fase seja **pequena, focada e fácil de revisar/validar** (evite fases grandes ou com muitas responsabilidades).
   - Cada fase deve ter um objetivo claro, escopo bem delimitado e entregáveis verificáveis.

2. **Estrutura de cada fase**:
   - **Objetivo**: o que será entregue na fase.
   - **Arquivos/Módulos**: quais arquivos serão criados ou alterados.
   - **Passos**: lista objetiva das alterações necessárias.
   - **Critério de validação**: como verificar que a fase foi concluída com sucesso (ex.: execução de testes, cobertura, build).

3. **Ordem e dependências**:
   - Ordene as fases de forma incremental e lógica, garantindo que cada fase deixe o projeto em um estado funcional sempre que possível.
