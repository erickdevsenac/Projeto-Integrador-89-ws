# BUGS.md

## Bug 001 - Produto com estoque 0 aparece na categoria "Aproveite+"
- Severidade: Alta
- Área: Lógica de Negócio / Funcionalidade
- Passos para reproduzir:
  1. Criar uma categoria "Aproveite+".
  2. Criar um produto associado à categoria com `quantidade_estoque = 0`.
  3. Chamar a função que lista produtos por categoria (`Produto.objects.por_categoria("aproveite")`).
- Resultado Esperado: Produto com estoque 0 **não deve aparecer** na lista.
- Resultado Obtido: Produto com estoque 0 aparece na lista (falha na filtragem).
- Observações: Ajustar o método `por_categoria` para filtrar apenas produtos disponíveis (`quantidade_estoque > 0`).

## Bug 002 - Usuário não autenticado consegue acessar DELETE de produto
- Severidade: Alta
- Área: Segurança / Permissões
- Passos para reproduzir:
  1. Criar categoria "Aproveite+".
  2. Criar produto com estoque positivo.
  3. Fazer requisição DELETE em `/api/produto/<id>/` sem autenticação.
- Resultado Esperado: Status 401 Unauthorized ou 403 Forbidden.
- Resultado Obtido: Status 404 Not Found ou possibilidade de acesso indevido (dependendo da URL).
- Observações: Proteger endpoint de DELETE com permissão adequada (decorator `IsAuthenticated` ou `IsAdminUser`) e corrigir URL/API se necessário.
