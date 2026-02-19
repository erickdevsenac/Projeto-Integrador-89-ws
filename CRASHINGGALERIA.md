# 1️⃣ Verificar tratamento de erro de conexão

Confirmar se existe verificação de conectividade antes do carregamento das imagens.

Implementar tratamento para:

Timeout de requisição

Falha de fetch

Status HTTP diferente de 200

Exibir mensagem amigável ao usuário em vez de permitir quebra da renderização.

Implementar try/catch adequado.

Criar estado de erro (errorState) para renderização condicional.

Exibir componente de fallback (ex: "Verifique sua conexão e tente novamente").

# 2️⃣ Validar URLs das imagens

Confirmar se os caminhos das imagens estão corretos.

Verificar se há retorno null, undefined ou string vazia.

Validar se a API está retornando corretamente os dados da galeria.

# 3️⃣ Verificar possível quebra na renderização

Conferir se há:

Uso incorreto de map() sem validação do array.

Acesso a propriedades de objetos indefinidos.

Problemas de chave (key) nos componentes listados.

# 4️⃣ Implementar fallback visual

Adicionar:

Loading state (isLoading)

Componente de erro

Botão de "Tentar novamente"