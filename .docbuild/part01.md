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

