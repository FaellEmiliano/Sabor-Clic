# Sabor e Clic — Front-end MPA

Protótipo Multi-Page Application do Sabor e Clic. Cada seção possui um arquivo HTML próprio e os dados desta etapa são simulados no navegador.

## Objetivo do 3º bimestre

Nesta entrega o JavaScript demonstra os conteúdos pedidos na disciplina sem antecipar a integração completa do 4º bimestre:

- arrays e objetos literais;
- `for...of`, `for...in` e `forEach`;
- manipulação dinâmica do DOM;
- criação e atualização do cardápio e carrinho;
- validação de formulários;
- cálculo em memória de subtotais e total do pedido.

A Fetch API, `async/await`, integração real com Flask e refatoração completa para POO ficam para a próxima etapa.

## Organização dos scripts

```text
assets/
  data.js         -> dados simulados, estado e objetos literais
  site.js         -> sessão simulada, menu e navegação MPA
  components.js   -> componentes visuais compartilhados
  cart.js         -> regras e cálculos do carrinho
  catalog.js      -> cardápio dinâmico e manipulação do DOM
  validation.js   -> validações simples de formulários
  login.js        -> lógica e validação da tela de login
  views.js        -> registro das telas do protótipo
  a11y.js         -> recursos de acessibilidade
```

O antigo protótipo concentrava grande parte do comportamento em um único script. A versão atual separa as responsabilidades para deixar o código mais legível e facilitar a futura troca dos dados simulados pela API Flask.

## Exemplos implementados para a entrega

### Cardápio

`catalog.js` percorre o array de produtos com `forEach`, cria elementos com `document.createElement`, atualiza o DOM e permite filtrar os produtos por categoria.

### Carrinho

`cart.js` adiciona e remove itens, mantém o estado no `localStorage` e calcula o valor total em memória com `reduce`.

### Reserva

`validation.js` percorre os campos do formulário com `for...of`, verifica campos obrigatórios e valida o formato básico do e-mail. A confirmação continua simulada nesta etapa.

### Perfis

`data.js` mantém os perfis em um objeto literal. `findRoleByEmail()` utiliza `for...in` para localizar o perfil associado ao e-mail de demonstração.

## Como abrir

Abra `index.html` diretamente no navegador. Não é necessário servidor para esta etapa.

## Contas de demonstração

- `rafael@exemplo.com` — Cliente
- `marina@saboreclic.com` — Cozinheiro
- `ana@saboreclic.com` — Administrador

A autenticação é simulada com `localStorage`; não representa a autenticação final do sistema.
