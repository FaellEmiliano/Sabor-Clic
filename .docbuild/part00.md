INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DE SÃO PAULO
CAMPUS SÃO PAULO

SABOR & CLIC

Sistema de Gestão para Espaços Gastronômicos e Dark Kitchens

DOCUMENTAÇÃO DO PROJETO INTEGRADOR — 3º BIMESTRE

Turma: [PREENCHER]

Integrantes: [PREENCHER]

Professores: [PREENCHER]

São Paulo — 2026

# SUMÁRIO

1. Introdução

2. Objetivos

3. Visão geral e escopo do sistema

4. Atores e controle de acesso

5. Requisitos do sistema

6. Fluxo integrado Reserva → Sessão → Pedido → KDS

7. Arquitetura integrada

8. Front-end e páginas da aplicação

9. JavaScript do 3º bimestre

10. Back-end Flask simulado

11. Contratos de rotas e integração futura

12. Banco de dados

13. Cardápio, pedidos e carrinho

14. KDS e operação da cozinha

15. Bancadas, reservas e sessões

16. Segurança

17. Estado atual da implementação

18. Atendimento aos requisitos do 3º bimestre

19. Próximos passos para o 4º bimestre

20. Considerações finais

Referências

# 1. INTRODUÇÃO

O Sabor & Clic é um sistema web voltado à gestão de espaços gastronômicos compartilhados, com foco na reserva de bancadas, organização das sessões de uso e gerenciamento dos pedidos realizados durante cada reserva. O projeto integra conteúdos de Desenvolvimento Web, Programação, Banco de Dados, Segurança da Informação e Design de Interfaces.

A versão documentada neste trabalho representa a etapa de estruturação do terceiro bimestre. O front-end já possui um protótipo navegável em formato MPA (Multi-Page Application), com páginas separadas para Cliente, Cozinha e Administração. O JavaScript utiliza dados simulados para demonstrar manipulação do DOM, arrays, objetos, validações e cálculos. Paralelamente, o back-end Flask possui uma estrutura simulada com exemplos dos endpoints fundamentais e dos contratos de dados que serão consolidados na integração definitiva.

A opção por dados e respostas simuladas nesta fase permite validar o fluxo completo da aplicação sem antecipar toda a complexidade de persistência, autenticação definitiva e integração assíncrona. Dessa forma, o projeto mantém coerência com os requisitos do terceiro bimestre e prepara uma arquitetura que poderá ser evoluída no quarto bimestre.

# 2. OBJETIVOS

## 2.1 Objetivo geral

Desenvolver uma plataforma web capaz de integrar reservas de bancadas gastronômicas, sessões de uso, cardápio digital, pedidos e acompanhamento do preparo em um único sistema, com interfaces e permissões específicas para clientes, cozinheiros e administradores.

## 2.2 Objetivos específicos

• Permitir a consulta e a reserva de bancadas.

• Criar uma sessão de uso vinculada a cada reserva ativa.

• Disponibilizar um cardápio digital para criação de pedidos.

• Vincular todos os pedidos a uma reserva/sessão válida.

• Disponibilizar um KDS para o acompanhamento da cozinha.

• Separar as áreas de Cliente, Cozinha e Administração.

• Demonstrar no terceiro bimestre as lógicas fundamentais em JavaScript e Flask com dados simulados.

• Preparar contratos de rotas e dados compatíveis com a futura integração por Fetch API e JSON.

• Documentar a modelagem de dados por meio do DER, MER e dicionário de dados.

# 3. VISÃO GERAL E ESCOPO DO SISTEMA

O núcleo do Sabor & Clic é a relação entre a reserva de uma bancada e os serviços utilizados durante aquele período. Após a criação de uma reserva válida, o cliente passa a possuir uma Sessão. Essa Sessão funciona como o contexto no qual o cliente acessa o cardápio, cria pedidos e acompanha seu preparo.

O pedido não é tratado como uma operação isolada: ele deve estar associado à reserva/sessão que originou a solicitação. Essa decisão mantém rastreabilidade entre cliente, bancada, horário e consumo, além de permitir que o KDS identifique corretamente onde cada pedido deve ser entregue.

O escopo desta versão prioriza a validação visual e lógica dos principais fluxos. Operações avançadas, persistência definitiva, integração HTTP real e mecanismos completos de segurança são planejados para a etapa seguinte.

# 4. ATORES E CONTROLE DE ACESSO

| Ator | Responsabilidades principais | Área da aplicação |

| --- | --- | --- |

| Cliente | Consultar bancadas, reservas e sessão; acessar cardápio; manter carrinho; criar e acompanhar pedidos. | Cliente |

| Cozinheiro | Visualizar pedidos, acompanhar fila de produção, alterar etapas do preparo e consultar histórico. | Cozinha / KDS |

| Administrador | Gerenciar reservas, bancadas, produtos, ingredientes, substituições, usuários e relatórios. | Administração |


