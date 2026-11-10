# Decisões de implementação

Data de referência 02/11/2026. Contrato final desta implementação, a ser considerado junto ao SQL e ao dicionário atualizado.

1. Triggers estão fora do escopo por instrução explícita do usuário. O consumo e o estorno são feitos no Python, com bloqueios de linha e atualização condicional de saldo em transação.
2. A confirmação do pedido reserva os ingredientes. Cancelar antes de iniciar preparo estorna; cancelar depois do início não os devolve automaticamente. Ajustes físicos são registrados como movimentações.
3. As necessidades de todas as receitas do pedido são agregadas. O original é preferido; um substituto direto pode atender a necessidade completa por prioridade, fator e saldo. Não existe encadeamento de substitutos nem mistura parcial.
4. Os saldos de ingredientes originais são reservados antes de escolher substitutos, evitando gastar como substituto um ingrediente necessário em outro componente do mesmo pedido. Unidades diferentes devem ser refletidas no fator cadastrado.
5. Pedido e estoque são atômicos. A mesma chave de idempotência e conteúdo retornam o mesmo pedido; mudar o conteúdo com a mesma chave resulta em conflito. Preços enviados pelo navegador não são usados.
6. Reserva possui zero ou uma sessão; a sessão possui exatamente uma reserva. O check-in ocorre dentro do período. Prato pode possuir zero itens de pedido, permitindo cadastrar antes da primeira venda.
7. Contas criadas pela API têm um perfil especializado. Alteração do perfil de uma conta existente não é exposta; administradores criam contas novas nos perfis autorizados. O esquema preserva as tabelas de especialização; acesso direto ao banco deve continuar restrito.
8. Um cliente pode manter sessões em bancadas distintas e selecionar o atendimento na interface. Fim do período bloqueia novos pedidos; o encerramento é manual, após concluir ou cancelar os pedidos. Não há fechamento automático com pendências.
9. O código de acesso é identificador operacional gerado pelo servidor, não substitui login nem é credencial de autorização na API.
10. Todas as consultas de catálogo exigem autenticação. Essa escolha substitui o catálogo público previsto na matriz histórica.
11. Pratos são inativados logicamente. Movimentações não têm rota de edição/exclusão; correções são novas movimentações. Ingredientes referenciados pelo histórico não são removidos pela API.
12. Datas internas são UTC, JSON inclui offset e a interface exibe São Paulo. Entradas sem offset representam São Paulo. Bancos legados com datas de negócio locais exigem avaliação antes de converter registros; o banco real verificado nesta sessão ainda não tinha reservas/pedidos.
13. O SQL final mantém os tamanhos e escalas atuais do modelo físico, inclusive fator DECIMAL(10,4), em vez de aplicar cegamente os tamanhos propostos no PDF antigo. O dicionário final representa esses tipos.
14. Capacidade/pessoas, categorias/imagens, estoque mínimo, cobrança online e notificações não integram esta versão do esquema. Não são simulados na interface.
15. Sessões de autenticação são revogáveis no banco. A restauração de snapshot revoga as sessões recuperadas. A conta de runtime permanece sem DDL; instalação/migração deve ser executada por administrador do MySQL.

Os PDFs/diagramas do terceiro bimestre são preservados como histórico. Esta versão não declara fidelidade pixel a pixel ao Figma, certificação WCAG, implantação pública ou execução do workflow remoto antes de essas verificações ocorrerem.
