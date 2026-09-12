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

