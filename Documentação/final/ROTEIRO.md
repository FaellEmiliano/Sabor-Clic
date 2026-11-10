# Roteiro de apresentação

## Sequência sugerida

1. Problema: conflitos de reserva, filas de preparo e controle manual de ingredientes.
2. Arquitetura: HTML/CSS/JavaScript orientado a objetos → Fetch/JSON → Flask → MySQL.
3. Cadastro administrativo de bancada, ingrediente, prato, ficha e substituição.
4. Cliente reserva um período; demonstrar rejeição de conflito e de data passada.
5. Dentro do período, iniciar sessão e escolher o atendimento correto.
6. Montar carrinho, editar quantidade, informar observações e enviar pedido.
7. Demonstrar preço oficial, registro de consumo e a mesma operação reenviada sem duplicação.
8. Cozinha salva estimativa e avança recebido → em preparo → pronto → entregue.
9. Cliente acompanha, encerra sessão e administrador consulta relatórios e auditoria.
10. Mostrar testes de segurança, concorrência MySQL e backup/restauração.
11. Explicar: não foram utilizadas triggers por decisão explícita; a regra de estoque é transacional no backend.

## Preparação

Preparar o esquema com `init-db` usando uma conta administrativa. Criar dados com `seed-demo` e ensaiar os três perfis. Criar reserva com início próximo ao horário da apresentação, sem alterar relógio do sistema ou desativar validações. Não exibir `.env`, `.session-key`, cookies, tokens ou snapshot privado.

Para demonstração reproduzível sem tocar no banco real, iniciar a fixture. Ela já tem uma sessão ativa e dados de teste; informar claramente que é um ambiente descartável, e não simular que foram criados no MySQL real.
