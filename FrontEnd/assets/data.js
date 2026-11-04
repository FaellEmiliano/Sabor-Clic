// Catalogs are populated exclusively from the API.
const state = { carrinho:new Carrinho(), get cart(){return this.carrinho.itens;}, set cart(items){this.carrinho=Carrinho.fromJSON(items);} };
const benches = [];
const products = [];
let currentUser = null;
function saveCart() {
  if (currentUser) localStorage.setItem(`cart:${currentUser.id_usuario}`, JSON.stringify(state.cart));
}
function loadCart() {
  try { state.cart = JSON.parse(localStorage.getItem(`cart:${currentUser.id_usuario}`) || '[]'); }
  catch { state.cart = []; }
  if (!Array.isArray(state.cart)) state.cart = [];

}
const menus = {
  cliente:[
    ["cliente_inicio","⌂","Início"],
    ["cliente_bancadas","▦","Bancadas"],
    ["cliente_reservas","▣","Minhas reservas"],
    ["cliente_sessao","◉","Sessão atual"],
    ["cliente_cardapio","☰","Cardápio"],
    ["cliente_carrinho","<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='9' cy='20' r='1'/><circle cx='18' cy='20' r='1'/><path d='M2.5 3h2l2.6 12.4a2 2 0 002 1.6h8.4a2 2 0 002-1.6L21 8H6'/></svg>","Carrinho"],
    ["cliente_pedidos","✓","Meus pedidos"],
    ["cliente_perfil","⚙","Meu perfil"]
  ],
  cozinha:[
    ["cozinha_dashboard","⌂","Visão geral"],
    ["cozinha_kds","▦","KDS"],
    ["cozinha_pedidos","☷","Pedidos"],
    ["cozinha_estoque","◫","Disponibilidade"],
    ["cozinha_historico","↺","Histórico"]
  ],
  admin:[
    ["admin_dashboard","⌂","Dashboard"],
    ["admin_reservas","▣","Reservas"],
    ["admin_bancadas","▦","Bancadas"],
    ["admin_produtos","☰","Produtos"],
    ["admin_ingredientes","◫","Ingredientes"],
    ["admin_substituicoes","⇄","Substituições"],
    ["admin_usuarios","♟","Usuários"],
    ["admin_relatorios","▤","Relatórios"]
  ]
};

const roleInfo = {};
function money(value) { return Number(value || 0).toLocaleString('pt-BR', {style:'currency', currency:'BRL'}); }
