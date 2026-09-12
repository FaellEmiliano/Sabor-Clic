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

