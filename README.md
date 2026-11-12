# Sabor e Clic

Aplicação HTML/CSS/JavaScript com API Flask e persistência MySQL. Fluxo: **reserva → sessão → pedido → cozinha**. Estoque, substituições e estornos são processados em transações no backend. **Não há triggers, conforme a orientação do projeto nesta implementação.**

## Execução local

### Windows 10

1. Baixe o instalador de 64 bits do Python 3.10 ou superior. Se usar o instalador tradicional, marque **Add Python to PATH** e mantenha o `pip` selecionado. Abra um novo PowerShell e confira com `python --version` ou `py -3 --version`. [Downloads do Python para Windows](https://www.python.org/downloads/windows/)
2. Instale o **MySQL Server 8**. Selecione uma versão compatível com a sua edição do Windows. No configurador, habilite TCP/IP, use a porta `3306` (ou anote a porta escolhida), defina a senha de `root` e configure o servidor como serviço do Windows. Confira em `services.msc` se o serviço está em execução. O MySQL Workbench é opcional. [MySQL Installer para Windows](https://dev.mysql.com/downloads/installer/) · [Manual de instalação do MySQL](https://dev.mysql.com/doc/refman/8.4/en/windows-installation.html)

### Linux (Ubuntu)

Instale o Python, o suporte a ambientes virtuais e o MySQL pelo APT. Estes comandos são para o Ubuntu. Em outras distribuições, use o gerenciador de pacotes correspondente e confirme que o servidor instalado é MySQL 8. [Guia do MySQL no Linux](https://dev.mysql.com/doc/refman/8.4/en/linux-installation-native.html)

```bash
sudo apt update
sudo apt install python3 python3-venv mysql-server
sudo systemctl enable --now mysql
python3 --version
mysql --version
```

### Criar o banco e configurar o projeto

Abra o console do MySQL com uma conta administrativa. No Windows, use o **MySQL Command Line Client** do menu Iniciar ou conecte-se como `root` pelo Workbench. No Ubuntu, tente `sudo mysql`. Se o servidor estiver configurado para autenticação por senha, use `mysql -u root -p`.

Para uma instalação nova, execute o SQL abaixo. Substitua `SUA_SENHA_MYSQL` por uma senha própria antes de executar. A conta `saboreclic_app` recebe permissões apenas no banco do projeto.

```sql
CREATE DATABASE IF NOT EXISTS saboreclic CHARACTER SET utf8mb4;
CREATE USER 'saboreclic_app'@'localhost' IDENTIFIED BY 'SUA_SENHA_MYSQL';
GRANT ALL PRIVILEGES ON saboreclic.* TO 'saboreclic_app'@'localhost';
```

Na raiz do projeto, copie `.env.example` para `.env` se o arquivo ainda não existir. Preencha os valores com os dados do banco que você criou.

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_NAME=saboreclic
DB_USER=saboreclic_app
DB_PASSWORD=SUA_SENHA_MYSQL
COOKIE_SECURE=false
```

Defina também `SECRET_KEY` com o resultado de `python -c "import secrets; print(secrets.token_hex(32))"` (use `py -3` ou `python3` conforme a instalação). Guarde o `.env` na sua máquina. A senha MySQL é usada pelo Flask para conectar ao banco. As contas demo são usadas na tela de login do Sabor e Clic.

### Executar o instalador

Na raiz do projeto, use o comando da sua plataforma. Os scripts criam o ambiente virtual, instalam as dependências e preparam as tabelas. Remova a opção de demonstração se quiser iniciar sem as contas e os dados de teste.

**Windows (PowerShell)**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1 -Demo
```

**Linux (Bash)**

```bash
bash instalar.sh --demo
```

Se você começar pelo instalador, ele cria o `.env` com uma chave de sessão e pausa para você preencher os dados do banco. No Windows, o script abre o Bloco de Notas. No Linux, edite o arquivo em outro terminal antes de confirmar.

### Instalação manual no Windows

Use Python 3.10+ e MySQL 8. O Node.js 22+ é necessário apenas para os testes JavaScript. Na raiz do repositório, execute no PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Edite o `.env` na raiz. Preencha `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST` e `DB_PORT`, ou configure `DATABASE_URL`. Variáveis do processo têm precedência. Substitua o valor de exemplo de `SECRET_KEY` por uma chave aleatória persistente. Se remover a variável, o ambiente local gera a chave em `.session-key`. Use `COOKIE_SECURE=false` para o HTTP local e `true` em HTTPS.

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

### Instalação com contas temporárias

Em um banco novo, execute `..\.venv\Scripts\python.exe -m flask --app run init-db --demo` dentro de `backend` para inicializar o esquema e criar as três contas. Se o esquema já estiver atualizado, execute `..\.venv\Scripts\python.exe -m flask --app run seed-demo`. Os dois comandos usam a senha de demonstração `SaborDemo123!` para as três contas novas, sem pedir entrada. Contas existentes mantêm a senha e o estado atuais.

| Perfil | E-mail |
| --- | --- |
| Administrador | `admin@demo.local` |
| Cliente | `cliente@demo.local` |
| Cozinheiro | `chef@demo.local` |

Para usar as contas como acesso inicial de uma instalação real, mantenha o sistema em acesso local durante a configuração e use `seed-demo --pedir-senha` em um esquema inicializado para escolher uma senha temporária própria. Entre com o administrador demo, abra **Usuários** e cadastre seu administrador definitivo com uma senha própria. Saia e entre com a nova conta para confirmar o acesso. Em **Usuários**, exclua as três contas demo. Se houver registros vinculados que impeçam a exclusão, desative a conta. Conclua essa etapa antes de disponibilizar o sistema. O servidor não recria as contas ao reiniciar.

O comando também inclui dados fictícios de catálogo. Para começar com um banco sem esses dados, use `init-db` e `create-admin` conforme os passos anteriores.

### Iniciar e acessar

Dentro de `backend`, execute:

```powershell
..\.venv\Scripts\python.exe run.py
```

No Linux, execute `../.venv/bin/python run.py` dentro de `backend`.

Acesse [http://127.0.0.1:5000/](http://127.0.0.1:5000/) e entre com a conta cadastrada. O Flask serve o frontend e a API no mesmo endereço. Use `Ctrl+C` para parar o servidor e rode o mesmo comando para reiniciá-lo após uma migração.

O comando `init-db` prepara o banco a partir do esquema e das migrações versionadas em `backend/database/`.

## Regras implementadas

- Reserva futura, sem sobreposição, em bancada ativa; tarifa por duração em horas calculada pelo servidor. Reagendamento também rejeita passado. Cancelamento permitido enquanto confirmada.
- Reserva tem zero ou uma sessão; a sessão é criada no check-in, dentro do período reservado. Um cliente pode atender reservas paralelas em bancadas diferentes e selecionar a sessão na interface.
- O fim do período bloqueia novos pedidos. O encerramento é manual e exige que todos os pedidos estejam entregues ou cancelados. O código de acesso da sessão é um identificador operacional.
- Pedido usa sessão própria e ativa. Valores, nomes históricos e total são gravados pelo servidor em uma única transação.
- Checkout exige `Idempotency-Key` com 16–64 caracteres. Mesmo conteúdo e chave retornam o mesmo pedido; reutilizar a chave com conteúdo diferente retorna 409. O frontend preserva a chave após falha de rede e cria outra para uma nova operação.
- Consumo agregado pela ficha técnica. O ingrediente original é preferido; na falta de saldo, o servidor escolhe um substituto direto com saldo suficiente por prioridade e ID, aplicando o fator de conversão. Não há substituição recursiva nem mistura parcial; o consumo real fica registrado.
- A alocação reserva os saldos necessários às receitas originais antes de avaliar substitutos. O fator de conversão deve refletir as unidades cadastradas.
- O estoque é reservado na confirmação. Cancelamento ainda em `recebido` estorna; depois de iniciar preparo não devolve ingredientes automaticamente. Reenvios não geram nova baixa.
- KDS: `recebido → em_preparo → pronto → entregue`. Cozinha registra estimativa; administrador pode cancelar. Transições armazenam horários reais.
- Datas são armazenadas em UTC e enviadas em ISO 8601 com offset. Entradas sem offset são interpretadas no horário de São Paulo; a interface exibe São Paulo.
- Pratos são inativados logicamente. Ingredientes com histórico de movimentação têm exclusão protegida. Correções de saldo geram novas movimentações.

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
- `03_migracao_integracao.sql`: alterações aditivas da versão anterior, aplicadas com inspeção pelo comando `init-db`.
- `11_queries_relatorios.sql`: vendas, estoque, ocupação e auditoria.
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

A [documentação técnica](Documenta%C3%A7%C3%A3o/Documentacao_final.pdf) reúne o funcionamento do sistema, as evidências e os limites da verificação. A [pasta de documentação](Documenta%C3%A7%C3%A3o/) também contém o dicionário de dados, o modelo relacional, a apresentação e o roteiro. Os documentos do terceiro bimestre ficam em [3º bimestre](Documenta%C3%A7%C3%A3o/3-bimestre/).
