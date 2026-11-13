# Frontend Sabor e Clic

Interface HTML/CSS/JavaScript conectada à API Flask. Siga a [instalação no README principal](../README.md) e abra http://127.0.0.1:5000/.

`domain.js` implementa as entidades ES6 com campos privados, herança e métodos estáticos. `Carrinho` controla quantidades e centavos; `Pedido` serializa IDs/quantidades e identifica uma operação de checkout. O valor cobrado é sempre calculado novamente pelo backend.

`api.js` centraliza Fetch com cookie e CSRF. `views.js` carrega somente recursos necessários à tela, oferece paginação/filtros, usa totais agregados da sessão e carrega opções de relacionamento separadas das tabelas paginadas. `cart.js` manipula o carrinho por meio de seus métodos. `login.js` implementa login/cadastro reais. `a11y.js` trata preferências locais inválidas sem quebrar a página.

As telas incluem observações e endereço por pedido, controle explícito de quantidade, estimativa e estados do KDS, histórico, disponibilidade por intervalo, auditoria e movimentações de estoque. A cozinha é atualizada por polling de dez segundos; não há promessa de entrega instantânea por WebSocket.

A API exige autenticação nas consultas de catálogo. Papéis no armazenamento local são somente informação de interface; o servidor faz a autorização. Checkout usa chave de idempotência, preservada após falha de rede.

Testes e limites estão no README da raiz. O [modelo relacional](../Documenta%C3%A7%C3%A3o/MODELO_FINAL.md) descreve os campos e vínculos do esquema atual. O backend atualiza o estoque em transação.
