# Sabor e Clic

Sistema de restaurante com reservas de bancadas, pedidos, fila da cozinha e controle de estoque. Desenvolvido em HTML, CSS e JavaScript, com API Flask e banco MySQL.

## Requisitos

- [Python 3.10 ou superior](https://www.python.org/downloads/) com `pip` e suporte a `venv`. No Windows, marque **Add Python to PATH** durante a instalação.
- [MySQL Server 8](https://dev.mysql.com/downloads/mysql/) instalado e em execução.

## Instalação

Use uma instalação nova com um banco vazio. O instalador cria as tabelas a partir do esquema completo em `backend/database/01_modelo_fisico.sql`. Para adotar uma nova versão do sistema, reinstale usando um banco novo.

### 1. Criar o banco

Abra o MySQL como administrador pelo Workbench ou pelo terminal (`mysql -u root -p`; no Ubuntu, também é possível usar `sudo mysql`). Execute, substituindo a senha de exemplo:

```sql
CREATE DATABASE saboreclic CHARACTER SET utf8mb4;
CREATE USER 'saboreclic_app'@'localhost' IDENTIFIED BY 'SUA_SENHA_MYSQL';
GRANT ALL PRIVILEGES ON saboreclic.* TO 'saboreclic_app'@'localhost';
```

### 2. Executar o instalador

Baixe o projeto, abra o terminal na pasta principal e execute o comando da sua plataforma.

**Windows — PowerShell**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1
```

**Linux — Bash**

```bash
bash instalar.sh
```

O instalador prepara o ambiente Python, instala as dependências e cria o arquivo `.env` com uma chave de sessão. Na primeira execução, ele pausa para você preencher os dados do banco; no Windows, abre o Bloco de Notas.

Confira estes campos no `.env`, salve e volte ao terminal para continuar:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_NAME=saboreclic
DB_USER=saboreclic_app
DB_PASSWORD=SUA_SENHA_MYSQL
COOKIE_SECURE=false
```

Mantenha a `SECRET_KEY` gerada pelo instalador. O `.env` fica apenas na sua máquina.

### 3. Criar o administrador e iniciar

**Windows — PowerShell**

```powershell
cd backend
..\.venv\Scripts\python.exe -m flask --app run create-admin
..\.venv\Scripts\python.exe run.py
```

**Linux — Bash**

```bash
cd backend
../.venv/bin/python -m flask --app run create-admin
../.venv/bin/python run.py
```

O primeiro comando solicita nome, e-mail e senha do administrador. Depois, acesse **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** e entre com essa conta. O Flask serve a interface e a API no mesmo endereço.

Para parar, pressione `Ctrl+C`. Nas próximas vezes, basta executar `run.py` com o Python do ambiente virtual; o administrador é criado somente uma vez.

### Demonstração (opcional)

Para instalar com dados de exemplo, acrescente `-Demo` ao instalador Windows ou `--demo` ao instalador Linux. Nesse caso, pule a criação do administrador e use uma destas contas, todas com a senha `SaborDemo123!`:

| Perfil | E-mail |
| --- | --- |
| Administrador | `admin@demo.local` |
| Cliente | `cliente@demo.local` |
| Cozinheiro | `chef@demo.local` |

Essas contas são destinadas à demonstração local.

## Fotos de produtos e ingredientes

Ao criar ou editar um cadastro, o administrador pode enviar uma foto, escolher da biblioteca compartilhada ou deixar sem foto. A biblioteca começa com as oito fotos do projeto e permite reutilizar os novos uploads.

São aceitos JPEG, PNG e WebP de até **5 MB e 20 megapixels**. As fotos são ajustadas e comprimidas automaticamente para WebP, com até 1200 × 1200 pixels.

Os arquivos enviados ficam em `backend/uploads/`, fora do Git; o banco guarda seus caminhos. Inclua essa pasta no backup junto com o banco. Para usar outro diretório persistente, defina `UPLOAD_FOLDER` com um caminho absoluto no `.env`. Trocar ou retirar a foto de um cadastro mantém o arquivo na biblioteca.

## Estrutura do projeto

| Pasta | Conteúdo |
| --- | --- |
| `FrontEnd/` | Telas, estilos, scripts e imagens da biblioteca |
| `backend/app/` | API, regras de negócio e modelos |
| `backend/database/` | Esquema completo, dados de demonstração e consultas SQL |
| `Documentação/` | Documentação técnica, modelo de dados e apresentação |

## Testes

Com o ambiente virtual ativado, execute os testes do backend a partir da raiz:

```bash
cd backend
python -m unittest discover -s tests
```

Para os testes JavaScript, use Node.js 22+ e execute na raiz:

```bash
node --test FrontEnd/tests/domain.test.cjs FrontEnd/tests/validation.test.cjs
```

Os testes de integração usam uma instância descartável: em `backend`, inicie `python -m tests.serve_fixture`. Em outro terminal, na raiz, execute `node --test FrontEnd/tests/integration.test.cjs`. O teste de fotos fica em `FrontEnd/tests/photos.browser.cjs` e requer Playwright e Chromium (`CHROMIUM_PATH` informa o executável). Reinicie a fixture antes de cada teste de integração.

A verificação MySQL fica em `backend/tests/mysql_verification.py` e usa bancos temporários. Configure `QA_DATABASE_URL` com uma conta de testes e execute `python -m tests.mysql_verification` em `backend`. O GitHub Actions executa as verificações automáticas em um ambiente descartável.

## Documentação

Consulte a [documentação técnica](Documenta%C3%A7%C3%A3o/Documentacao_final.pdf), o [modelo de dados](Documenta%C3%A7%C3%A3o/MODELO_FINAL.md) e os demais arquivos na [pasta Documentação](Documenta%C3%A7%C3%A3o/).
