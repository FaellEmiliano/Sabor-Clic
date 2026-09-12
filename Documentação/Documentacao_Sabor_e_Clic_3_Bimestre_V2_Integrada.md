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


No protótipo do terceiro bimestre, a identificação do perfil é simulada com dados armazenados em localStorage. O JavaScript redireciona o usuário para a área correspondente ao perfil de demonstração. Esse mecanismo serve para validar a navegação e a separação visual das áreas; a autenticação definitiva será de responsabilidade do back-end.

# 5. REQUISITOS DO SISTEMA

## 5.1 Requisitos funcionais

| Código | Requisito |

| --- | --- |

| RF01 | Permitir identificação do usuário por perfil. |

| RF02 | Listar bancadas e suas informações. |

| RF03 | Permitir criação e consulta de reservas. |

| RF04 | Disponibilizar sessão vinculada à reserva. |

| RF05 | Exibir cardápio com produtos e disponibilidade. |

| RF06 | Permitir adicionar e remover itens do carrinho. |

| RF07 | Calcular subtotal e total do pedido em memória. |

| RF08 | Criar pedido vinculado à reserva/sessão. |

| RF09 | Exibir pedidos ao cozinheiro no KDS. |

| RF10 | Permitir evolução do status do pedido. |

| RF11 | Disponibilizar telas administrativas para gerenciamento do sistema. |



## 5.2 Requisitos não funcionais

• Interface responsiva e coerente entre as áreas.

• Separação de responsabilidades no JavaScript.

• Estrutura de back-end preparada para Flask e padrão MVC/adaptação de MVC.

• Comunicação futura por JSON e requisições HTTP.

• Validação de entradas no front-end e posteriormente também no back-end.

• Controle de acesso por papel (RBAC) na versão integrada final.

• Organização de código que facilite manutenção e evolução.

# 6. FLUXO INTEGRADO RESERVA → SESSÃO → PEDIDO → KDS

• 1. O cliente acessa a aplicação e consulta as bancadas disponíveis.

• 2. O cliente informa os dados necessários e cria uma reserva.

• 3. A reserva válida passa a representar uma sessão de uso da bancada no período definido.

• 4. Durante a sessão, o cliente acessa o cardápio digital.

• 5. Produtos disponíveis são adicionados ao carrinho.

• 6. O JavaScript calcula quantidades, subtotais e total do pedido.

• 7. Na versão integrada, o pedido será enviado ao Flask em JSON, contendo o identificador da reserva/sessão e os itens.

• 8. O back-end registrará e validará o pedido.

• 9. O pedido será disponibilizado no KDS.

• 10. O cozinheiro atualizará o status até que o pedido seja marcado como pronto/entregue.

| FIGURA SUGERIDA — Fluxograma Reserva → Sessão → Pedido → KDS |

| --- |



# 7. ARQUITETURA INTEGRADA

A arquitetura planejada separa o sistema em uma aplicação front-end multipágina e um back-end Flask. O front-end é responsável pela apresentação, interação imediata e validações de experiência do usuário. O Flask será responsável pela validação definitiva, regras de negócio, autenticação, autorização e persistência.

| Camada | Tecnologias/estrutura | Responsabilidade |

| --- | --- | --- |

| Interface | HTML5 + CSS3 | Páginas e componentes visuais. |

| Lógica do cliente | JavaScript modular | DOM, arrays, objetos, validações, carrinho e comportamento do protótipo. |

| Comunicação final | Fetch API + JSON | Integração assíncrona entre navegador e Flask no 4º bimestre. |

| Servidor | Python + Flask | Endpoints, regras de negócio, segurança e acesso aos dados. |

| Persistência | Banco relacional | Usuários, bancadas, reservas, sessões, pedidos, itens, produtos e demais entidades. |



Front-end MPA  →  Fetch/JSON  →  Flask  →  Regras de negócio  →  Banco de Dados
      ↑                         ↓
      └──────── atualização da interface / KDS ────────┘

# 8. FRONT-END E PÁGINAS DA APLICAÇÃO

O protótipo foi reestruturado de uma SPA para uma MPA real. Cada seção possui um arquivo HTML próprio e uma URL própria. A aplicação possui 21 páginas internas, além da tela de login, distribuídas entre os três perfis.

## 8.1 Páginas do Cliente

• cliente_inicio.html — visão geral da sessão atual.

• cliente_bancadas.html — consulta visual das bancadas.

• cliente_reservas.html — reservas e formulário de nova reserva.

• cliente_sessao.html — resumo da sessão vinculada à reserva.

• cliente_cardapio.html — cardápio digital e filtros.

• cliente_carrinho.html — itens selecionados e total do pedido.

• cliente_pedidos.html — acompanhamento do preparo.

• cliente_perfil.html — dados e preferências do usuário.

## 8.2 Páginas da Cozinha

• cozinha_dashboard.html — visão geral operacional.

• cozinha_kds.html — quadro principal de pedidos.

• cozinha_pedidos.html — consulta detalhada dos pedidos.

• cozinha_estoque.html — disponibilidade dos produtos.

• cozinha_historico.html — histórico de produção.

## 8.3 Páginas da Administração

• admin_dashboard.html — indicadores gerais.

• admin_reservas.html — gerenciamento de reservas.

• admin_bancadas.html — gerenciamento de bancadas.

• admin_produtos.html — gerenciamento do cardápio.

• admin_ingredientes.html — acompanhamento de ingredientes.

• admin_substituicoes.html — alternativas de ingredientes.

• admin_usuarios.html — usuários e perfis.

• admin_relatorios.html — indicadores e relatórios simulados.

O arquivo index.html funciona como entrada da aplicação e contém o login de demonstração. A navegação entre as páginas é realizada por links reais, preservando o comportamento de uma aplicação multipágina.

# 9. JAVASCRIPT DO 3º BIMESTRE

O JavaScript foi reorganizado para evidenciar os conteúdos exigidos no terceiro bimestre sem antecipar a arquitetura completa do quarto bimestre. A lógica utiliza dados simulados e separa responsabilidades em arquivos específicos.

| Arquivo | Responsabilidade | Conteúdos demonstrados |

| --- | --- | --- |

| data.js | Dados simulados, perfis, produtos, bancadas e estado inicial. | Arrays, objetos literais, for...in. |

| site.js | Sessão simulada, shell, menu, navegação e utilitários. | DOM, localStorage, manipulação de classes e atributos. |

| components.js | Geração de componentes reutilizáveis. | Funções, template strings, for...of. |

| cart.js | Operações do carrinho. | find, filter, reduce, forEach, cálculos em memória. |

| catalog.js | Renderização e filtragem do cardápio. | forEach, createElement, appendChild, eventos. |

| validation.js | Validação da reserva. | for...of, validação de campos, foco e feedback. |

| login.js | Validação e login demonstrativo. | Eventos, condições, validação e localStorage. |

| views.js | Templates das páginas do protótipo. | Composição das telas e renderização. |

| a11y.js | Ajustes de acessibilidade do protótipo. | Comportamentos auxiliares de interface. |



## 9.1 Cardápio dinâmico

A página de cardápio é construída a partir do array de produtos. O módulo catalog.js percorre os objetos com forEach, cria elementos do DOM dinamicamente e permite filtrar os itens por categoria. Assim, o conteúdo exibido deixa de ser apenas estático e passa a responder aos dados disponíveis.

## 9.2 Carrinho e cálculos

O módulo cart.js centraliza a inclusão e remoção de produtos, a contagem de itens e o cálculo do total. Os dados do carrinho são mantidos no navegador durante a demonstração, inclusive entre páginas, por meio de localStorage. O cálculo utiliza reduce para somar preço × quantidade de cada item.

## 9.3 Validação

O formulário de reserva possui validação no cliente. Os campos são percorridos com for...of e o sistema impede a confirmação quando existem valores obrigatórios ausentes ou e-mail inválido. O login demonstrativo utiliza validação semelhante. Na versão final, essas validações serão repetidas pelo servidor.

# 10. BACK-END FLASK SIMULADO

O back-end do terceiro bimestre possui caráter intencionalmente simulado. Seu objetivo é apresentar a organização do servidor, exemplos dos endpoints fundamentais e a forma como as informações deverão circular entre front-end, regras de negócio e modelos. As funções atuais ainda não representam toda a persistência definitiva e algumas classes de modelo são stubs preparados para a etapa seguinte.

A estrutura possui arquivo de execução, configurações da aplicação, inicialização do Flask e controllers separados por área funcional. Essa abordagem permite demonstrar o desenho geral da arquitetura antes de conectar banco de dados e front-end real.

backend/
├── run.py
├── config.py
├── app/
│   ├── __init__.py
│   └── controller/
│       ├── auth_controller.py
│       ├── reserva_controller.py
│       └── pedidos_controller.py
└── utils/

## 10.1 Autenticação simulada

auth_controller.py contém exemplos para cadastro, consulta de usuário e login. Os modelos associados ainda são simulados. Na integração final, essas funções deverão ser expostas por rotas Flask reais, validar credenciais e criar uma sessão segura no servidor.

## 10.2 Reservas e bancadas

reserva_controller.py demonstra consulta de bancadas, criação de reserva e consulta de uma reserva por identificador. O formato já estabelece a separação entre controller e model, embora a persistência ainda não esteja implementada nessa etapa.

## 10.3 Pedidos, cardápio e KDS

pedidos_controller.py apresenta o fluxo de consulta do cardápio, criação de pedido, consulta por identificador e geração dos dados utilizados pelo KDS. O pedido recebe a referência da reserva, preservando a regra central de que pedidos pertencem ao contexto de uma reserva/sessão.

# 11. CONTRATOS DE ROTAS E INTEGRAÇÃO FUTURA

A tabela abaixo reúne os endpoints representados pelo back-end simulado. Eles funcionam como contratos iniciais da API. Na versão definitiva, deverão ser registrados como rotas Flask reais, retornar JSON padronizado e utilizar códigos HTTP adequados.

| Método | Endpoint | Finalidade | Situação 3º bi |

| --- | --- | --- | --- |

| POST | /api/cadastro | Cadastrar cliente/usuário. | Simulado |

| GET | /api/cadastro/<id> | Consultar usuário por id. | Simulado |

| POST | /api/login | Validar credenciais. | Simulado |

| GET | /api/bancadas | Listar bancadas. | Simulado |

| POST | /api/reservas | Criar reserva. | Simulado |

| GET | /api/reservas/<id> | Consultar reserva. | Simulado |

| GET | /api/cardapio | Obter produtos disponíveis. | Simulado |

| POST | /api/pedido/cadastro | Criar pedido vinculado à reserva. | Simulado |

| GET | /api/pedido/<id> | Consultar pedido. | Simulado |

| GET | /api/kds/<id> | Obter informação para o KDS. | Simulado |



## 11.1 Contratos previstos para fechar o fluxo final

Para aproximar a estrutura da versão final, a integração deverá acrescentar uma representação explícita da Sessão, mesmo que ela seja derivada de uma reserva ativa. Uma opção de contrato final é disponibilizar GET /api/reservas/<id>/sessao ou GET /api/sessoes/<id>, além de uma rota PATCH para atualização do status do pedido.

| Método | Endpoint proposto | Uso futuro |

| --- | --- | --- |

| GET | /api/reservas/<id>/sessao | Obter a sessão vinculada à reserva. |

| PATCH | /api/pedidos/<id>/status | Atualizar o estado do pedido no KDS. |

| GET | /api/reservas/<id>/pedidos | Listar os pedidos de uma reserva/sessão. |



Essas rotas são apresentadas como planejamento de integração e não como funcionalidades concluídas nesta etapa.

# 12. BANCO DE DADOS

A modelagem do banco de dados já possui materiais específicos no repositório: DER_saborclic.png, MER_saborclic.png, EER_saborclic.mwb e o Dicionario_de_Dados_Sabor_e_Clic. Esses arquivos registram as entidades, atributos, relacionamentos e estruturas previstas para a persistência definitiva.

## 12.1 DER

O Diagrama Entidade-Relacionamento representa conceitualmente as entidades do sistema e suas cardinalidades. Ele deve ser utilizado como referência principal para compreender as relações entre usuários, bancadas, reservas, pedidos, itens, pratos/ingredientes e demais elementos do domínio.

| INSERIR/ATUALIZAR FIGURA — Documentação/DER_saborclic.png |

| --- |



## 12.2 MER/EER

O modelo desenvolvido no MySQL Workbench aproxima o projeto da implementação relacional. Ele complementa o DER conceitual e será a base para a construção física das tabelas no quarto bimestre.

| INSERIR/ATUALIZAR FIGURA — Documentação/MER_saborclic.png |

| --- |



## 12.3 Dicionário de dados

O dicionário de dados descreve os campos, significados, tipos e restrições planejadas. A versão completa permanece como documento separado no repositório e deve ser mantida sincronizada com futuras alterações do modelo.

# 13. CARDÁPIO, PEDIDOS E CARRINHO

No front-end, os produtos do cardápio são objetos armazenados em um array de dados de demonstração. Cada produto possui identificador, nome, categoria, preço, status, descrição e referência de imagem. Apenas produtos disponíveis podem ser adicionados ao carrinho.

O carrinho também é simulado no navegador. Quando um produto já existente é adicionado novamente, sua quantidade é incrementada. A remoção utiliza filter e o cálculo utiliza reduce. Na versão integrada, o carrinho permanecerá como estado de interface até o momento da finalização, quando os itens serão enviados ao endpoint de criação de pedido.

Carrinho (front-end) → JSON do pedido → POST /api/pedido/cadastro → validação Flask → persistência → KDS

# 14. KDS E OPERAÇÃO DA COZINHA

O Kitchen Display System representa a área operacional do cozinheiro. O protótipo organiza pedidos em colunas como Recebidos, Em preparo e Prontos, permitindo visualizar identificação do pedido, bancada, tempo e itens solicitados.

No terceiro bimestre, as alterações de estado são demonstrativas. Na integração final, as ações do KDS deverão chamar o back-end para alterar o status do pedido e, posteriormente, atualizar também a visualização do cliente.

# 15. BANCADAS, RESERVAS E SESSÕES

As bancadas representam os espaços físicos que podem ser reservados. Os dados simulados incluem nome, capacidade, preço, status, recursos disponíveis e imagem. O cliente consulta essas informações antes de iniciar o fluxo de reserva.

A reserva associa o cliente a uma bancada e a um período. No desenho funcional do Sabor & Clic, uma reserva ativa disponibiliza uma Sessão. A Sessão é o ambiente de uso durante o período reservado e concentra os pedidos, consumo e acompanhamento da experiência.

Embora o back-end simulado atual trabalhe diretamente com id_reserva na criação do pedido, essa escolha já é compatível com a regra de negócio: a reserva é a origem do contexto da Sessão. A versão final poderá manter a sessão como entidade explícita ou derivá-la da reserva ativa, conforme a modelagem consolidada.

# 16. SEGURANÇA

A versão atual possui mecanismos de segurança apenas em nível de protótipo. O front-end identifica perfis usando localStorage e impede navegação casual para páginas de outro perfil por redirecionamento. Esse comportamento não é considerado autenticação real e não deverá ser usado como proteção definitiva.

O back-end possui estrutura de configuração para SECRET_KEY e exemplos de login/cadastro, mas o fluxo final de autenticação, sessão, cookies e autorização ainda será implementado. Na versão definitiva, o servidor deverá ser a fonte de verdade para as permissões.

• Sessões Flask/cookies seguros.

• Hash de senha e armazenamento seguro.

• RBAC para Cliente, Cozinheiro e Administrador.

• Validação de todas as entradas no servidor.

• Consultas SQL parametrizadas.

• Proteção das rotas administrativas e do KDS.

• Sanitização e prevenção de vulnerabilidades comuns.

# 17. ESTADO ATUAL DA IMPLEMENTAÇÃO

| Área | Estado | Observação |

| --- | --- | --- |

| Protótipo MPA | Implementado | 21 páginas internas + login, com navegação real. |

| Design e componentes | Implementado no protótipo | Interface completa para os três perfis. |

| Dados de demonstração | Implementado | Produtos, bancadas, perfis, pedidos e indicadores simulados. |

| Cardápio dinâmico | Implementado no front-end | DOM + filtros por categoria. |

| Carrinho | Implementado no front-end | Adicionar, remover, quantidade e total; persistência local. |

| Validação de reserva | Implementado no front-end | Validação demonstrativa. |

| Login por perfil | Implementado como simulação | LocalStorage; não é autenticação real. |

| Estrutura Flask | Parcial / simulada | Controllers e contratos de endpoints. |

| Banco de dados em execução | Planejado | Modelagem pronta; persistência final fica para próxima etapa. |

| Fetch API entre front e Flask | Planejado | Integração do 4º bimestre. |

| Autenticação segura/RBAC no servidor | Planejado | Será implementado no back-end definitivo. |



# 18. ATENDIMENTO AOS REQUISITOS DO 3º BIMESTRE

| Requisito | Situação | Evidência/abordagem |

| --- | --- | --- |

| DER | Concluído | DER_saborclic.png. |

| Dicionário de dados | Concluído | Dicionario_de_Dados_Sabor_e_Clic. |

| Protótipo / telas | Concluído | MPA com áreas Cliente, Cozinha e Admin. |

| Cardápio Digital | Concluído no protótipo | cliente_cardapio.html + catalog.js. |

| KDS | Concluído no protótipo | cozinha_kds.html. |

| Arrays e objetos JS | Concluído | data.js e módulos de lógica. |

| forEach | Concluído | catalog.js e cart.js. |

| for...of | Concluído | validation.js e components.js. |

| for...in | Concluído | Busca de perfil em objeto de usuários. |

| Manipulação do DOM | Concluído | catalog.js, site.js e renderização das páginas. |

| Validação de formulários | Concluído | validation.js e login.js. |

| Cálculos em memória | Concluído | cart.js. |

| Estrutura Flask | Parcial / adequada ao escopo | run.py, config.py, app e controllers. |

| Rotas fundamentais | Representadas como contratos simulados | Controllers de autenticação, reserva, pedido e KDS. |

| JSON / integração inicial | Planejada no contrato | Dados estruturados preparados; Fetch real fica para o 4º bi. |

| Segurança / RBAC | Planejado e documentado | Separação de perfis no protótipo + estratégia de servidor definida. |



# 19. PRÓXIMOS PASSOS PARA O 4º BIMESTRE

• Registrar as rotas Flask reais e padronizar respostas JSON.

• Implementar os models de acesso ao banco de dados.

• Criar o banco físico e sincronizá-lo com DER/MER/dicionário.

• Substituir dados simulados do front-end por requisições Fetch API.

• Implementar classes ES6+ onde forem úteis para o domínio do front-end.

• Adicionar async/await e tratamento de erros nas operações HTTP.

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
