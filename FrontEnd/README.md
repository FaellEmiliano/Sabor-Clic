# Sabor e Clic — Versão MPA (Multi-Page Application)

Este é o mesmo protótipo, reestruturado de SPA para **MPA de verdade**: cada
seção do menu agora é um arquivo `.html` próprio, com URL própria, em vez de
um único `index.html` que trocava o conteúdo via JavaScript.

## Como abrir
Abra `index.html` (tela de login) direto no navegador — não precisa de servidor.

## O que mudou em relação à versão SPA

- **21 páginas reais**, uma por item de menu, nomeadas `<perfil>_<secao>.html`
  (ex.: `cliente_cardapio.html`, `admin_relatorios.html`).
- **Sessão via `localStorage`**: ao logar, o perfil (`cliente`/`cozinha`/`admin`)
  é salvo em `localStorage.role`. Cada página checa isso com `guardRole()`:
  sem sessão → volta pro login; sessão de outro perfil → redireciona pro
  início do perfil certo.
- **Carrinho persistente**: os itens do carrinho do cliente também ficam em
  `localStorage.cart`, então sobrevivem à navegação entre páginas reais
  (coisa que uma SPA resolve só na memória, mas que aqui precisa ser salva).
- **Menu com `<a href>` de verdade**, não mais botões com `onclick` simulando
  navegação — cada link do menu lateral aponta para o arquivo `.html` real da
  seção, com o item ativo destacado por página.
- **Sair (`handleLogout`)** limpa a sessão e redireciona para `index.html`.

## Estrutura de arquivos

```
index.html                → tela de login (única entrada sem sessão)
cliente_*.html (8)        → seções do perfil Cliente
cozinha_*.html (5)        → seções do perfil Cozinha
admin_*.html (8)          → seções do perfil Admin
assets/
  style.css               → mesmo design system de antes (sem alterações)
  data.js                 → dados de exemplo (produtos, bancadas, menus, perfis)
  site.js                 → sessão, menu, navegação entre páginas, utilitários de UI
  views.js                → conteúdo (HTML) de cada seção — igual ao app.js original
  login.js                → lógica da tela de login
  img/                    → imagens (sem alterações)
```

## Contas de demonstração
Mesmas de antes — qualquer senha funciona:
- `rafael@exemplo.com` → Cliente
- `marina@saboreclic.com` → Cozinheiro
- `ana@saboreclic.com` → Administrador

## Observação
O conteúdo visual e os dados de exemplo de cada tela são os mesmos da versão
SPA — o que mudou foi a arquitetura de navegação (páginas reais + sessão em
`localStorage`), não o design nem o conteúdo.
