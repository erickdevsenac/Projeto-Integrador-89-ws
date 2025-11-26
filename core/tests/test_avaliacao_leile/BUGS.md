# BUGS.md

## Bug 001 - Produto com estoque 0 aparece na categoria "produto"
- **Severidade**: Alta
- **Área**: Lógica de Negócio / Funcionalidade
- **Passos para reproduzir**:
  1. Criar uma categoria "Produto".
  2. Criar um produto associado à categoria com `quantidade_estoque = 0`.
  3. Chamar a função que lista produtos por categoria (`Produto.objects.por_categoria("Produto")`).
- **Resultado Esperado**: Produto com estoque 0 **não deve aparecer** na lista.
- **Resultado Obtido**: Produto com estoque 0 aparece na lista (falha na filtragem).
- **Observações**: Ajustar o método `por_categoria` para filtrar apenas produtos disponíveis (`quantidade_estoque > 0`).

