# Sabor e Clic

Projeto integrador do curso Técnico em Desenvolvimento de Sistemas do IFSP. A entrega do terceiro bimestre apresenta um protótipo navegável em HTML, CSS e JavaScript e uma API Flask executável com dados demonstrativos mantidos em memória.

O fluxo central é **Reserva → Sessão → Pedido → KDS**. A Reserva define cliente, bancada e período; a Sessão representa o atendimento ativo; o Pedido pertence a uma Sessão; e o KDS mostra o Pedido com o contexto da bancada.

## Escopo do terceiro bimestre

Está implementado nesta etapa:

- protótipo multipágina para Cliente, Cozinha e Administração;
- JavaScript ES6+ com arrays, objetos literais, `for...of`, `for...in`, `forEach`, DOM, validações e cálculos do carrinho em memória;
- aplicação Flask criada por factory com Blueprints, rotas, controllers e models;
- requisições e respostas JSON nos endpoints do backend;
- dados simulados em memória para usuários, bancadas, reservas, sessões, cardápio e pedidos;
- vínculo de Pedido por `id_sessao` e consulta para o KDS;
- DER, MER, dicionário de dados e documentação do projeto.

Fetch no front-end, POO completa em JavaScript, persistência em banco físico, autenticação real, cookies de login, RBAC no servidor e triggers permanecem para o quarto bimestre.

## Protótipo no Figma

O [protótipo navegável do Sabor e Clic no Figma](https://www.figma.com/design/5XKfiCZo91lwR5qq5dX70Q/html.to.design-%E2%80%94-by-%E2%80%B9div%E2%80%BARIOTS-%E2%80%94-Import-websites-to-Figma-designs--web-html-css---Community-?node-id=0-1&t=SBqUxwiB4E0ViRW8-1) reúne os wireframes e as telas usadas como referência para esta entrega.

## Estrutura atual

```text
Sabor-Clic/
├── backend/
│   ├── app/
│   │   ├── controllers/   # validações e casos de uso
│   │   ├── models/        # dados demonstrativos em memória
│   │   ├── routes/        # Blueprints e contratos HTTP/JSON
│   │   └── __init__.py    # factory Flask
│   ├── tests/
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
├── FrontEnd/
│   ├── assets/
│   │   ├── components.js
│   │   ├── cart.js
│   │   ├── catalog.js
│   │   ├── data.js
│   │   ├── views.js
│   │   └── demais arquivos de interface
│   └── páginas HTML por perfil
└── Documentação/
    ├── documentação V3 do terceiro bimestre
    ├── PDF oficial do projeto
    ├── DER e MER
    └── dicionário de dados
```

## Como executar o backend

É necessário ter Python 3.10 ou mais recente.

```bash
cd backend
python -m venv .venv
```

Ative o ambiente virtual. No Windows:

```powershell
.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale o Flask e inicie a API:

```bash
pip install -r requirements.txt
python run.py
```

A API ficará disponível em `http://127.0.0.1:5000/api`. Como os dados são mantidos em memória, alterações são descartadas quando o processo é encerrado.

## Endpoints disponíveis

| Método | Rota | Finalidade nesta etapa |
| --- | --- | --- |
| GET | `/api` | Confirma que a API está em execução |
| POST | `/api/cadastro` | Cria cadastro demonstrativo |
| GET | `/api/cadastro/<id>` | Consulta um usuário demonstrativo |
| POST | `/api/login` | Identifica um usuário demonstrativo, sem autenticação real |
| GET | `/api/bancadas` | Lista bancadas simuladas |
| POST | `/api/reservas` | Cria uma reserva em memória |
| GET | `/api/reservas/<id>` | Consulta uma reserva |
| POST | `/api/sessoes` | Cria e ativa a Sessão de uma Reserva |
| GET | `/api/sessoes/<id>` | Consulta uma Sessão |
| POST | `/api/sessoes/<id>/encerrar` | Encerra uma Sessão |
| GET | `/api/cardapio` | Lista os pratos simulados |
| POST | `/api/pedido/cadastro` | Cria Pedido vinculado por `id_sessao` |
| GET | `/api/pedido/<id>` | Consulta um Pedido |
| GET | `/api/kds` | Lista a fila demonstrativa do KDS |
| GET | `/api/kds/<id>` | Consulta um Pedido no formato do KDS |

Exemplo de criação de Pedido:

```json
{
  "id_sessao": 501,
  "itens": [
    {"id_prato": 2, "quantidade": 1},
    {"id_prato": 5, "quantidade": 2}
  ],
  "observacao": "Sem cebola"
}
```

## Como abrir o front-end

Abra `FrontEnd/index.html` no navegador. As contas demonstrativas aparecem na tela inicial e usam a senha exibida pela própria interface. O login e o carrinho utilizam `localStorage`; o front-end ainda não chama a API Flask por Fetch nesta entrega.

## Verificação do backend

Com o ambiente virtual ativo e dentro de `backend`, execute:

```bash
python -m unittest discover -s tests -v
```

Validações demonstrativas no frontend (executar a partir da raiz do repositório com Node.js 20+):

```bash
node --test FrontEnd/tests/validation.test.cjs
```

## Documentação

- [Documentação V3 do terceiro bimestre](Documentação/Documentacao_Sabor_e_Clic_3_Bimestre.pdf)
- [PDF oficial do Projeto Integrador](Documentação/Versão2_ProjetoIntegrador31082026.pdf)
- [Dicionário de dados](Documentação/Dicionario_de_Dados_Sabor_e_Clic.pdf)
- [DER](Documentação/DER_saborclic.png)
- [MER](Documentação/MER_saborclic.png)
- [Plano de Segurança, matriz RBAC e OWASP Top 10:2021](Documentação/Seguranca_3_Bimestre.md)
- [Roteiro de evidências e casos de teste de Segurança](Documentação/Evidencias_Seguranca_3_Bimestre.md)

### Entregas de Banco de Dados e Segurança

O 3º bimestre inclui DER no brModelo, MER lógico em 3FN e dicionário de dados editável em `.docx`; os artefatos editáveis precisam corresponder à versão final dos diagramas. A modelagem física/SQL e triggers ficam para o 4º bimestre.

O controle de acesso do protótipo em `localStorage` **não é autorização real**. A API ainda não verifica senha nem perfis; veja a matriz de RBAC e o plano OWASP para o comportamento a implementar no 4º bimestre. As validações JavaScript de reserva (data, horário, capacidade, telefone e e-mail) oferecem apenas feedback demonstrativo e **não persistem a reserva**.
