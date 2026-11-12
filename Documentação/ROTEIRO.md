# Roteiro de apresentação do Sabor e Clic

## Preparação

Use um ambiente descartável com os três perfis. Em um banco de demonstração inicializado, use `seed-demo`. A fixture de `backend/tests/serve_fixture.py` oferece uma sessão ativa para mostrar o checkout sem esperar o horário de uma reserva. Identifique o ambiente usado durante a apresentação e mantenha credenciais e tokens fora da tela.

## Sequência de fala

1. **Arquitetura e perfis.** Siga o clique do navegador até a API Flask e o MySQL. Explique o que cada perfil pode fazer e onde a API verifica a propriedade de uma reserva ou de um pedido.
2. **Reserva e check-in.** Mostre por que 14h30–15h30 conflita com 14h–15h na mesma bancada e por que 15h é um limite válido para a próxima reserva. No código, aponte o bloqueio da bancada e as duas comparações de horário. Separe a confirmação da reserva da abertura da sessão.
3. **Carrinho e reenvio.** Envie duas unidades e localize o preço oficial no pedido. Use o trecho do frontend para mostrar onde a chave é guardada antes do envio. No backend, mostre a consulta da chave dentro da sessão e o retorno do pedido já gravado quando o conteúdo coincide.
4. **Estoque.** Use o exemplo de 0,400 kg com fator 1,25 para explicar o consumo de 0,500 kg de substituto. No código, aponte o teste de saldo e a chamada a `consume` antes do `commit`. Explique por que uma falha antes da confirmação desfaz as alterações pendentes.
5. **Cozinha.** Localize o ticket no KDS, registre a estimativa e avance pelos estados recebido, em preparo, pronto e entregue. Explique por que um cancelamento em recebido estorna o consumo e o que acontece depois do início do preparo.
6. **Fechamento.** Volte ao perfil do cliente, confirme a entrega e encerre a sessão. Mostre onde consultar a movimentação e o relatório. Encerre com as evidências registradas no ambiente descartável.
