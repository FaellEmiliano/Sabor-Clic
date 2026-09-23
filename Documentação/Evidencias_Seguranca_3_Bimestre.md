# Sabor & Clic — roteiro de evidências para Segurança (3º bimestre)

> **Importante:** este documento é um **roteiro de apresentação**. Uma ação marcada como "planejada" não constitui evidência executada. Capturas e registros devem ser produzidos pela equipe no navegador, sem simular resultados.

## 1. Como apresentar

1. Mostrar o DER/MER e explicar a diferença entre `sessao` do atendimento e sessão HTTP de login.
2. Exibir `Seguranca_3_Bimestre.md`: papéis, matriz por rota e por operação CRUD, propriedade das reservas/pedidos e políticas de erro.
3. Abrir `FrontEnd/index.html`; usar contas de demonstração. Explicar que qualquer senha não vazia funciona **somente no protótipo**.
4. Abrir a página de reservas do Cliente, alterar os campos e verificar os erros.
5. Exibir a API Flask e os testes existentes. Deixar claro que RBAC, hash/cookies e CSRF ainda serão implementados no 4º bimestre.

## 2. Casos para capturar no navegador (protótipo)

| ID | Procedimento | Resultado esperado | Evidência a inserir |
| --- | --- | --- | --- |
| JS-01 | Login com e-mail sem `@` | "Informe um e-mail válido." | Captura do formulário |
| JS-02 | Login com e-mail vazio ou senha vazia | "Preencha e-mail e senha." (ou validação HTML nativa) | Captura |
| JS-03 | Reserva sem e-mail | Alerta de campo obrigatório | Captura |
| JS-04 | Reserva com e-mail malformado | "Informe um e-mail válido." | Captura |
| JS-05 | Reserva com data anterior à atual | Impedir data antiga e mostrar mensagem; o calendário tem mínimo dinâmico | Captura |
| JS-06 | Selecionar Toscana e informar 6 pessoas (capacidade 4) | Mensagem de capacidade, sem confirmação | Captura |
| JS-07 | Reserva com 0 ou 1,5 pessoas | Mensagem de quantidade inválida, sem confirmação | Captura |
| JS-08 | Reserva com telefone preenchido de forma inválida | Mensagem de telefone com DDD | Captura |
| JS-09 | Preencher data válida, Provence, 6 pessoas, e-mail e telefone corretos | "Dados válidos! Reserva demonstrativa confirmada." | Captura |

**Observações:** os valores do protótipo são fictícios e a reserva válida **não** é persistida nem enviada à API. O navegador pode exibir primeiro sua mensagem nativa para entradas incompatíveis com `type=email/number`; nesse caso, registrar o comportamento observado.

## 3. Testes de API Flask já escritos no repositório

Executar a partir de `backend/`:

```bash
python -m unittest discover -s tests -v
```

O arquivo `backend/tests/test_api.py` já contempla respostas JSON, fluxo Reserva → Sessão → Pedido → KDS, rejeição de pedidos em sessão encerrada e conflito de reservas. Registrar a saída **real** obtida ao executar o comando no ambiente da equipe. Os testes de autenticação no arquivo verificam **somente o comportamento demonstrativo**.

## 4. Casos planejados para o 4º bimestre — NÃO implementados agora

| ID | Operação futura | Resultado esperado |
| --- | --- | --- |
| RBAC-01 | Usuário sem login consulta `/api/kds` | 401 |
| RBAC-02 | Cliente consulta reserva de outro cliente | 403 ou 404 sem vazamento |
| RBAC-03 | Cliente tenta criar conta com perfil `admin` | Perfil imposto como `cliente` |
| RBAC-04 | Cozinheiro tenta atualizar usuários | 403 |
| AUTH-01 | Senha incorreta no login real | 401, sem criar sessão |
| AUTH-02 | Logout e reutilização do cookie antigo | Operação protegida negada |
| SEC-01 | Total/preço manipulados no JSON de pedido | Recalcular a partir do cadastro |
| SEC-02 | Observação com texto contendo tags HTML | Exibir como texto, não como HTML executável |
| SEC-03 | Tentativa de SQL Injection | Query parametrizada preserva a estrutura SQL |
| SEC-04 | Requisição mutável sem token CSRF válido | 403 ou 400, conforme configuração |

## 5. O que não afirmar na apresentação

- Não dizer que `localStorage` protege o acesso: ele só simula a navegação por perfil.
- Não dizer que a API Flask já autentica: o login demonstrativo não compara senhas.
- Não dizer que resultados planejados foram testados antes de executar os testes.
- Não dizer que os arquivos SQL, triggers e o banco físico estão implementados neste bimestre.
