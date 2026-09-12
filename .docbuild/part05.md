• Implementar autenticação por sessão/cookies e RBAC no servidor.

• Conectar o fluxo completo Reserva → Sessão → Pedido → KDS.

• Atualizar o KDS e a área do cliente a partir dos estados reais dos pedidos.

• Criar testes de integração e revisar validações de segurança.

# 20. CONSIDERAÇÕES FINAIS

A versão atual do Sabor & Clic consolida a base necessária para a integração definitiva. O front-end apresenta os fluxos completos e possui lógicas reais de interface para o conteúdo previsto no terceiro bimestre. O back-end, por sua vez, define de forma simulada os principais contratos de endpoints e a separação inicial das responsabilidades do servidor.

A estratégia adotada evita implementar prematuramente toda a infraestrutura do quarto bimestre, mas mantém compatibilidade entre as partes. O cardápio, carrinho, reservas, pedidos e KDS foram estruturados para que os dados simulados possam ser substituídos progressivamente por respostas do Flask sem necessidade de redesenhar o sistema inteiro.

Com a modelagem do banco de dados, o protótipo multipágina, os módulos de JavaScript e a estrutura Flask documentados em conjunto, o projeto encerra o terceiro bimestre com uma visão integrada do produto e um caminho claro para a implementação final.

# REFERÊNCIAS

INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DE SÃO PAULO — CAMPUS SÃO PAULO. Projeto Integrador: Sabor & Clic — Sistema de Gestão para Dark Kitchens e Espaços Gastronômicos. Versão atualizada em 31 ago. 2026.

SABOR & CLIC. Repositório do projeto. GitHub: FaellEmiliano/Sabor-Clic. Acesso em setembro de 2026.
