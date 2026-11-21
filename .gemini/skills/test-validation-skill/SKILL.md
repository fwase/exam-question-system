---
name: test-validation-skill
description: Test validation skill — sempre cria testes unitários ao executar uma task e verifica se a cobertura de testes é maior que 90%.
---

# Test validation skill

Ao executar qualquer task de desenvolvimento ou alteração de código neste projeto, siga obrigatoriamente os passos abaixo antes de concluir:

1. **Criar testes unitários**:
   - Crie ou atualize testes unitários cobrindo todo o código novo ou modificado (casos de sucesso, erros e bordas).
   - Utilize `pytest` seguindo os padrões do projeto.

2. **Verificar cobertura de testes (> 90%)**:
   - Execute os testes com cobertura usando o entrypoint do `Makefile`:
     ```bash
     make coverage
     ```
     (equivalente a `python3 -m pytest --cov=. --cov-report=term-missing`)
   - Verifique se todos os testes passaram e se a cobertura total é **maior que 90%**.

3. **Corrigir cobertura insuficiente**:
   - Caso a cobertura seja menor ou igual a 90%, identifique as linhas/ramificações não cobertas no relatório e adicione testes unitários até ultrapassar 90%.
