# Relatório de Bugs — Aproveite+
 
## Bug 01 — PacoteSurpresa permanece ativo mesmo com preço negativo
 
### Severidade:
Alta — Afeta regra de negócio essencial.
 
### Passos para Reproduzir:
1. Autenticar como vendedor.
2. Criar um PacoteSurpresa com preço negativo.
3. Salvar.
 
### Resultado Obtido:
O pacote é criado com `ativo=True`.
 
### Resultado Esperado:
Itens com preço negativo devem ser automaticamente desativados (`ativo=False`).
 
### Status:
Corrigido após criação da validação e teste automatizado.