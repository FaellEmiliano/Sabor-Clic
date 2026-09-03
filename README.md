# Sabor-Clic

#Estrutura de arquivos: (rascunho)
sabor-e-clic/
│
├── README.md
├── .gitignore
├── requirements.txt
├── .env.example
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   │
│   ├── cliente/
│   │   ├── reservas.html
│   │   ├── sessao.html
│   │   ├── cardapio.html
│   │   ├── carrinho.html
│   │   └── pedidos.html
│   │
│   ├── cozinheiro/
│   │   └── kds.html
│   │
│   ├── administrador/
│   │   ├── dashboard.html
│   │   ├── pratos.html
│   │   ├── ingredientes.html
│   │   └── bancadas.html
│   │
│   └── assets/
│       ├── css/
│       │   ├── global.css
│       │   ├── components.css
│       │   └── pages/
│       │       ├── cardapio.css
│       │       ├── sessao.css
│       │       ├── kds.css
│       │       └── admin.css
│       │
│       └── js/
│           ├── api/
│           │   ├── authApi.js
│           │   ├── reservaApi.js
│           │   ├── sessaoApi.js
│           │   ├── pedidoApi.js
│           │   └── cardapioApi.js
│           │
│           ├── models/
│           │   ├── Carrinho.js
│           │   ├── ItemPedido.js
│           │   ├── Pedido.js
│           │   └── Prato.js
│           │
│           ├── pages/
│           │   ├── login.js
│           │   ├── reservas.js
│           │   ├── sessao.js
│           │   ├── cardapio.js
│           │   ├── carrinho.js
│           │   ├── pedidos.js
│           │   ├── kds.js
│           │   └── admin.js
│           │
│           └── utils/
│               ├── validation.js
│               ├── format.js
│               └── dom.js
│
├── backend/
│   ├── run.py
│   ├── config.py
│   │
│   └── app/
│       ├── __init__.py
│       │
│       ├── routes/
│       │   ├── auth_routes.py
│       │   ├── reserva_routes.py
│       │   ├── sessao_routes.py
│       │   ├── pedido_routes.py
│       │   ├── prato_routes.py
│       │   ├── ingrediente_routes.py
│       │   ├── bancada_routes.py
│       │   └── kds_routes.py
│       │
│       ├── controllers/
│       │   ├── auth_controller.py
│       │   ├── reserva_controller.py
│       │   ├── sessao_controller.py
│       │   ├── pedido_controller.py
│       │   ├── prato_controller.py
│       │   └── ingrediente_controller.py
│       │
│       ├── models/
│       │   ├── usuario_model.py
│       │   ├── reserva_model.py
│       │   ├── sessao_model.py
│       │   ├── pedido_model.py
│       │   ├── prato_model.py
│       │   ├── ingrediente_model.py
│       │   └── bancada_model.py
│       │
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── reserva_service.py
│       │   ├── sessao_service.py
│       │   ├── pedido_service.py
│       │   └── estoque_service.py
│       │
│       ├── middleware/
│       │   ├── auth.py
│       │   └── permissions.py
│       │
│       ├── database/
│       │   └── connection.py
│       │
│       └── utils/
│           ├── responses.py
│           └── validation.py
│
├── database/
│   ├── 01_modelo_fisico.sql
│   ├── 02_insercoes_basicas.sql
│   ├── 11_queries_relatorios.sql
│   └── 20_triggers.sql
│
├── tests/
│   ├── backend/
│   └── frontend/
│
└── docs/
    ├── der/
    │   ├── der_saboreclic.brM3
    │   └── der_saboreclic.png
    │
    ├── dicionario_dados/
    ├── figma/
    ├── apresentacao/
    └── documentacao/