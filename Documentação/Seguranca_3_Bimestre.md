# Sabor & Clic — Segurança da Informação (3º bimestre)

> **Situação:** planejamento e documentação. O login, a navegação por perfil e os dados atuais são demonstrativos; **não** há autenticação ou autorização real na API Flask. Esta política define o comportamento a implementar no 4º bimestre.

**Escopo:** usuários (cliente, cozinha e admin), bancadas, reservas, sessões de atendimento, pedidos, cardápio, insumos, KDS e relatórios. A sessão de atendimento (entidade `sessao`) **não** se confunde com a sessão de autenticação HTTP do Flask.

## 1. Regras gerais

- Negar por padrão: toda rota protegida exige autenticação e permissão expressa.
- Menor privilégio: cada perfil acessará apenas suas funções.
- Verificar **perfil e propriedade do recurso** no servidor; esconder botão no navegador não constitui proteção.
- Cadastro público sempre atribuirá `cliente`; perfil `cozinha` e `admin` somente por operação administrativa autorizada. O usuário não poderá elevar o próprio papel.
- O Flask deverá validar novamente todos os dados recebidos, independentemente do JavaScript.
- Preço e total serão calculados no servidor; identificadores informados pelo cliente não substituem a identidade autenticada.

## 2. Matriz RBAC proposta

Legenda: **Público** = sem login; **Próprio** = pertence ao usuário autenticado; **Operacional** = acesso necessário ao preparo; **Todos** = autorizado a gerenciar; **—** = proibido. A tabela descreve a **política futura**, não o comportamento implementado atualmente.

| Método / rota | Cliente | Cozinha | Admin |
| --- | --- | --- | --- |
| POST `/api/cadastro` | Público: somente cliente | Público: somente cliente | Público: somente cliente |
| POST `/api/login` | Público | Público | Público |
| GET `/api/cadastro/<id>` | Próprio | Próprio | Todos |
| GET `/api/bancadas`, GET `/api/cardapio` | Público | Público | Público |
| POST `/api/reservas` | Própria | — | Todos |
| GET `/api/reservas/<id>` | Própria | — | Todos |
| POST `/api/sessoes` | Própria, se elegível | — | Todos |
| GET `/api/sessoes/<id>` | Própria | — | Todos |
| POST `/api/sessoes/<id>/encerrar` | Própria, se elegível | — | Todos |
| POST `/api/pedido/cadastro` | Própria sessão ativa | — | Todos |
| GET `/api/pedido/<id>` | Próprio | Operacional | Todos |
| GET `/api/kds`, GET `/api/kds/<id>` | — | Operacional | Todos |

**Operações CRUD planejadas (sem endpoint ainda):** cliente consulta/edita o próprio perfil, cria e consulta suas reservas e pedidos, e cancela reserva própria quando a regra permitir; cozinha consulta pedidos e altera exclusivamente o estado de preparo, além de consultar disponibilidade de insumos; admin gerencia usuários/papéis, bancadas, produtos, fichas técnicas, substituições, estoque, reservas e relatórios. Os endpoints que faltam deverão receber política antes de serem expostos.

## 3. Validações e mensagens

| Entrada | JavaScript no 3º bimestre | Flask no 4º bimestre |
| --- | --- | --- |
| E-mail e senha | Obrigatórios; formato de e-mail | Normalização; hash de senha; limite de tentativas; resposta genérica |
| Reserva | Data atual/futura, horário válido, bancada disponível, pessoas inteiras e dentro da capacidade | Conferir conflito, propriedade, limite, estados, tipo e datas |
| Pedido | Carrinho com itens e quantidades positivas | Conferir sessão ativa e própria, itens, estoque, preços oficiais |
| Texto livre | Comprimento, campos obrigatórios, feedback | Validar tamanho/tipo; escape de saída; SQL parametrizado |
| Preço, perfil e total | Não editáveis no formulário público | Não confiar nesses campos enviados pelo navegador |

Respostas JSON planejadas: **400** dados inválidos, **401** sem autenticação, **403** sem permissão, **404** recurso inexistente ou ocultado, **409** conflito, **429** tentativas excessivas e **500** erro genérico. Mensagens não incluirão SQL, stack trace, senhas ou detalhes de configuração.

## 4. OWASP Top 10:2021 — riscos e plano de mitigação

A numeração **2021** foi escolhida porque o enunciado da disciplina cita A03 — Injection e A07 — Identification and Authentication Failures. Os controles abaixo são **planejados**, exceto as validações explicitamente existentes no protótipo.

| Categoria | Aplicação no Sabor & Clic | Medidas previstas / evidência |
| --- | --- | --- |
| **A01 Broken Access Control** | Acesso a reservas de terceiros, KDS e autoconcessão de papel | RBAC no Flask; checagem de propriedade; cliente de uma reserva não lê outra; acesso ao KDS requer cozinha/admin |
| **A02 Cryptographic Failures** | Exposição de senha, cookie ou dados pessoais | HTTPS; hash com salt via Werkzeug; chave em variável de ambiente; cookies HttpOnly/Secure/SameSite; nunca registrar segredos |
| **A03 Injection** | Campos de filtro e observações podem afetar consultas/HTML | SQL com placeholders; allowlist para colunas; `textContent`/escape de saída; testes com caracteres especiais |
| **A04 Insecure Design** | Reservas simultâneas, pedidos em sessão encerrada e baixa duplicada | Invariantes no domínio, transações, estados válidos e testes de conflito/concorrência |
| **A05 Security Misconfiguration** | Debug, segredo fixo, permissões do MySQL e CORS permissivo | Configuração por ambiente, debug desligado, privilégio mínimo, headers e revisão antes de publicar |
| **A06 Vulnerable and Outdated Components** | Dependências Flask e recursos de terceiros | Fixar versões e auditoria de dependências; atualização controlada com regressão |
| **A07 Identification and Authentication Failures** | Login demonstrativo atualmente aceita qualquer senha; role no localStorage | Sessão real no Flask, `check_password_hash`, logout, expiração, limitação de tentativas e testes negativos |
| **A08 Software and Data Integrity Failures** | Preço manipulado no navegador, migrations/seed alterados | Recalcular valores, preço histórico, transações, revisão por Git e recuperação de backups |
| **A09 Security Logging and Monitoring Failures** | Negativas de acesso e alterações administrativas sem trilha | Logs com hora/usuário/ação/resultado sem credenciais; acompanhamento e testes de eventos 401/403 |
| **A10 Server-Side Request Forgery** | Risco futuro caso API passe a buscar URLs externas enviadas por usuário | Evitar URLs arbitrárias; allowlist, bloquear IPs privados/metadados, validar redirects e limitar tempo de conexão |

### Exemplos conceituais para o 4º bimestre

```python
# Exemplo isolado: autenticar ANTES de avaliar a propriedade do recurso.
usuario = obter_usuario_da_sessao_http()
if usuario is None:
    return {"erro": "Autenticação necessária."}, 401
reserva = buscar_reserva(id_reserva)
if reserva is None:
    return {"erro": "Recurso não encontrado."}, 404
if usuario["perfil"] != "admin" and reserva["id_cliente"] != usuario["id"]:
    return {"erro": "Acesso negado."}, 403
```

```python
# Valores parametrizados. Nunca concatenar campos enviados pelo usuário.
cursor.execute(
    "SELECT id_reserva FROM reserva WHERE id_reserva = %s AND id_cliente = %s",
    (id_reserva, usuario["id"])
)
```

**CSRF/XSS:** operações que alteram estado e usam cookie de autenticação terão token CSRF validado pelo servidor; usar `SameSite` como defesa complementar. Texto de observação será exibido com `textContent`, sem interpretá-lo como HTML.

## 5. Evidências e implementação

- **3º bimestre:** exibir matriz, mensagens e validações demonstrativas; documentar limitações da autenticação.
- **4º bimestre:** implementar autenticação, RBAC no servidor, banco físico, SQL parametrizado, proteção CSRF/XSS, configurações e testes positivos/negativos. A baixa de estoque por trigger seguirá o item 5.4 do enunciado.
- Registrar screenshots reais e resultado dos testes; **não** apresentar cenários planejados como testes já executados. Ver `Evidencias_Seguranca_3_Bimestre.md`.

## Referências

- [OWASP Top 10:2021](https://top10.owasp.org/2021/)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Repositório Sabor & Clic](https://github.com/FaellEmiliano/Sabor-Clic)
