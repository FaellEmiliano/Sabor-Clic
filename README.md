# Sabor e Clic

Aplicação HTML/CSS/JavaScript com API Flask e persistência MySQL. Fluxo: **reserva → sessão → pedido → cozinha**. Estoque, substituições e estornos são processados em transações no backend. **Não há triggers, conforme a orientação do projeto nesta implementação.**

## Execução local no Windows

Use Python 3.10+ e MySQL 8. O Node.js 22+ é necessário apenas para os testes JavaScript. Na raiz do repositório, execute no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Edite o `.env` na raiz. Preencha `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST` e `DB_PORT`, ou configure `DATABASE_URL`. Variáveis do processo têm precedência. Substitua o valor de exemplo de `SECRET_KEY` por uma chave aleatória persistente. Se remover a variável, o ambiente local gera a chave em `.session-key`. Use `COOKIE_SECURE=false` para o HTTP local e `true` em HTTPS.

### Banco existente

Faça um backup do esquema e dos dados antes de atualizar. Se o banco se chama `saboreclic`, abra `backend/database/APLICAR_MIGRACAO.sql` no MySQL Workbench, conecte com uma conta administrativa e execute o arquivo inteiro. Confira o nome do esquema no `USE` antes de rodar. Para outro esquema, use o comando abaixo com uma conexão administrativa apontando para o banco correto:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m flask --app run migrate-db
```

A migração acrescenta as tabelas e colunas necessárias sem apagar registros ou criar triggers. Use a conta normal da aplicação para iniciar o servidor. O administrador já cadastrado pode continuar usando sua conta.

### Banco novo

Crie um esquema vazio no MySQL. Aponte a configuração para esse esquema e rode `init-db` com uma conta que tenha permissão de criar e alterar tabelas. A partir da raiz:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m flask --app run init-db
```

Volte a usar as credenciais normais da aplicação. Ainda em `backend`, crie o primeiro administrador. O comando solicita nome, e-mail e senha:

```powershell
..\.venv\Scripts\python.exe -m flask --app run create-admin
```

Para preencher um ambiente de demonstração, execute `..\.venv\Scripts\python.exe -m flask --app run seed-demo`. O comando solicita uma senha e cria as contas `admin@demo.local`, `cliente@demo.local` e `chef@demo.local`.

### Iniciar e acessar

Dentro de `backend`, execute:

```powershell
..\.venv\Scripts\python.exe run.py
```

Acesse [http://127.0.0.1:5000/](http://127.0.0.1:5000/) e entre com a conta cadastrada. O Flask serve o frontend e a API no mesmo endereço. Use `Ctrl+C` para parar o servidor e rode o mesmo comando para reiniciá-lo após uma migração.

O arquivo `backend/database/SCHEMA.sql` é um dump histórico com comandos `DROP TABLE`. Use os scripts de instalação ou migração acima para preparar o banco.

## Regras implementadas

- Reserva futura, sem sobreposição, em bancada ativa; tarifa por duração em horas calculada pelo servidor. Reagendamento também rejeita passado. Cancelamento permitido enquanto confirmada.
- Reserva tem zero ou uma sessão; a sessão é criada no check-in, dentro do período reservado. Um cliente pode atender reservas paralelas em bancadas diferentes e selecionar a sessão na interface.
- Pedido usa sessão própria e ativa. Valores, nomes históricos e total são gravados pelo servidor em uma única transação.
- Checkout exige `Idempotency-Key` com 16–64 caracteres. Mesmo conteúdo e chave retornam o mesmo pedido; reutilizar a chave com conteúdo diferente retorna 409. O frontend preserva a chave após falha de rede e cria outra para uma nova operação.
- Consumo agregado pela ficha técnica. O ingrediente original é preferido; na falta de saldo, o servidor escolhe um substituto direto com saldo suficiente por prioridade e ID, aplicando o fator de conversão. Não há substituição recursiva nem mistura parcial; o consumo real fica registrado.
- O estoque é reservado na confirmação. Cancelamento ainda em `recebido` estorna; depois de iniciar preparo não devolve ingredientes automaticamente. Reenvios não geram nova baixa.
- KDS: `recebido → em_preparo → pronto → entregue`. Cozinha registra estimativa; administrador pode cancelar. Transições armazenam horários reais.
- Datas são armazenadas em UTC e enviadas em ISO 8601 com offset. Entradas sem offset são interpretadas no horário de São Paulo; a interface exibe São Paulo.
- Pratos são inativados logicamente. Ingredientes com histórico de movimentação não podem ser excluídos de forma destrutiva pela API.

## Arquitetura

- `backend/app/models/`: 17 tabelas e operações de persistência.
- `controllers/http.py`: validação, identidade, propriedade e serialização.
- `controllers/seguranca_controller.py`: sessões revogáveis, rate limit e auditoria.
- `controllers/operacao_controller.py`: reservas, sessões, checkout e estados do pedido.
- `controllers/estoque_controller.py`: alocação, movimentações e estornos com atualização condicional do saldo.
- `controllers/consulta_controller.py`: filtros SQL e paginação validada.
- `controllers/api_controller.py`: handlers de aplicação; `routes/api_routes.py` registra somente o transporte HTTP.
- `FrontEnd/assets/domain.js`: `Entidade`, `Usuario`, `Prato`, `ItemPedido`, `Carrinho` e `Pedido`, com herança, campos privados e métodos estáticos. Carrinho calcula em centavos.
- `api.js`, `views.js`, `cart.js` e demais scripts: transporte, telas e interação. Listas paginadas não são usadas como fonte dos totais da sessão.

## API

Prefixo `/api`. Login e cadastro de cliente são públicos; as demais operações exigem autenticação, inclusive consultas do catálogo. Essa é a política final adotada, substituindo a matriz histórica que previa catálogo público.

| Recurso | Operações |
| --- | --- |
| `/login`, `/logout`, `/me` | POST, POST e GET |
| `/usuarios`, `/usuarios/<id>`, `/usuarios/<id>/status` | Gestão administrativa; leitura/edição própria autorizada |
| `/usuarios/cliente`, `/usuarios/cozinheiro`, `/usuarios/administrador` | POST; perfis privilegiados exclusivos do administrador |
| `/bancadas`, `/pratos`, `/ingredientes` | CRUD com permissões; cozinha altera apenas disponibilidade dos pratos |
| `/fichas-tecnicas`, `/substituicoes` | CRUD com chaves compostas |
| `/reservas`, `/sessoes`, `/pedidos` | Fluxo operacional, com acesso do cliente aos próprios recursos |
| `/sessoes/<id>` | Detalhe e resumo agregado de pedidos/consumo |
| `/sessoes/<id>/encerrar` | POST; exige concluir os pedidos |
| `/kds`, `/resumo-cozinha` | Fila operacional e contagens totais |
| `/disponibilidade?inicio=...&fim=...` | Bancadas disponíveis no intervalo |
| `/movimentacoes`, `/auditoria` | Histórico de estoque e eventos administrativos |
| `/relatorios?de=...&ate=...` | Receitas, ticket médio, tempo de preparo e resultados por bancada |

Listas usam `pagina`, `limite` (máximo 100), filtros por colunas permitidas e `q` onde existe texto pesquisável. `metadados` informa total e página. As opções de formulários percorrem as páginas separadamente; a seleção de um formulário não substitui os registros da tabela visível. Pedidos aceitam `situacao=ativos` ou `finalizados`.

Sessões autenticadas são persistidas e revogadas no servidor. O cookie é HttpOnly/SameSite; expiração absoluta de oito horas e inatividade de 30 minutos. Escritas exigem `X-CSRF-Token`. Login tem limite por conta e IP; senhas são verificadas sem remover caracteres. Auditoria não guarda senha, cookie, token ou payload pessoal. CORS aceita somente origens configuradas; o uso recomendado é mesma origem pelo Flask. CSP permite handlers inline da interface existente; saída dinâmica é escapada. Essa política pode ser endurecida após retirar os handlers inline.

## SQL e backup

- `01_modelo_fisico.sql`: esquema final e restrições, não destrutivo.
- `02_insercoes_basicas.sql`: dados mínimos sem senha real fixa.
- `03_migracao_integracao.sql`: alterações aditivas da versão anterior, aplicadas com inspeção pelo comando de migração.
- `11_queries_relatorios.sql`: vendas, estoque, ocupação e auditoria.
- `APLICAR_MIGRACAO.sql`: instalação administrativa idempotente para o banco local.

Não há `20_triggers.sql`. O saldo é atualizado pelo backend, dentro da mesma transação das movimentações.

```powershell
python -m flask --app run backup-db caminho-privado/snapshot.json
python -m flask --app run restore-db caminho-privado/snapshot.json
```

A restauração exige um esquema inicializado e vazio. Não substitui registros existentes e revoga sessões autenticadas recuperadas. Snapshots contêm dados privados e hashes; mantenha-os fora do Git e sob acesso restrito. O comando é snapshot de dados; o esquema continua nos scripts SQL.

## Testes

```powershell
cd backend
..\.venv\Scripts\python.exe -m unittest discover -s tests
```

```powershell
node --test FrontEnd/tests/domain.test.cjs FrontEnd/tests/validation.test.cjs
```

Integração HTTP, em uma fixture recém-iniciada:

```powershell
cd backend
..\.venv\Scripts\python.exe -m tests.serve_fixture
```

Em outro terminal, na raiz:

```powershell
node --test FrontEnd/tests/integration.test.cjs
```

`QA_PORT` altera a porta da fixture e `SABOR_QA_URL` altera o destino do teste Node. O teste inclui cenários com mais de 50 registros. Use uma fixture nova para cada execução, pois ele cria dados e depende da sessão inicial da fixture.

Para MySQL isolado, configure `QA_DATABASE_URL` para uma instância de testes com autorização para criar/remover schemas temporários e execute `python -m tests.mysql_verification` a partir de `backend`. O teste usa apenas schemas aleatórios `sabor_clic_qa_*` e nunca altera as tabelas de `DB_NAME`. Verifica migração, seeds, concorrência, estoque, idempotência e backup/restauração. Não usa triggers.

O workflow `.github/workflows/tests.yml` executa as verificações em ambiente descartável quando enviado ao GitHub. A configuração local do workflow não comprova sua execução remota.

Documentação final, decisões e roteiro em `Documentação/final/`. Evidências e limites em `VERIFICACAO.md`.
