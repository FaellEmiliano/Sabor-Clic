const state = {
  cart: JSON.parse(localStorage.getItem("cart") || "null") || [
    {id:2,nome:"Risoto de Cogumelos",preco:42,qtd:1},
    {id:5,nome:"Suco de Laranja",preco:9.5,qtd:2}
  ]
};
function saveCart(){ localStorage.setItem("cart", JSON.stringify(state.cart)); }

const benches = [
  {id:1,nome:"Bancada Toscana",cap:4,preco:85,status:"Disponível",recursos:["Cooktop","Pia","Tomadas"],emoji:"🍳",foto:"assets/img/benches/toscana.jpg"},
  {id:2,nome:"Bancada Provence",cap:6,preco:120,status:"Disponível",recursos:["Cooktop duplo","Forno","Pia"],emoji:"🔥",foto:"assets/img/benches/provence.jpg"},
  {id:3,nome:"Bancada Aurora",cap:2,preco:65,status:"Ocupada",recursos:["Cooktop","Pia"],emoji:"🥘",foto:"assets/img/benches/aurora.jpg"},
  {id:4,nome:"Bancada Ipê",cap:5,preco:105,status:"Disponível",recursos:["Cooktop","Air fryer","Pia"],emoji:"🍲",foto:"assets/img/benches/ipe.jpg"},
  {id:5,nome:"Bancada Cedro",cap:4,preco:95,status:"Manutenção",recursos:["Cooktop","Forno"],emoji:"🧰",foto:"assets/img/benches/cedro.jpg"},
  {id:6,nome:"Bancada Manacá",cap:3,preco:78,status:"Disponível",recursos:["Cooktop","Pia","Geladeira"],emoji:"🥗",foto:"assets/img/benches/manaca.jpg"}
];

const products = [
  {id:1,nome:"Bruschetta da Casa",cat:"Entradas",preco:18.9,ico:"🥖",foto:"assets/img/products/bruschetta.jpg",status:"Disponível",desc:"Pão italiano, tomate, manjericão e azeite."},
  {id:2,nome:"Risoto de Cogumelos",cat:"Pratos",preco:42,ico:"🍚",foto:"assets/img/products/risoto.jpg",status:"Disponível",desc:"Arroz arbóreo, cogumelos e parmesão."},
  {id:3,nome:"Burger Artesanal",cat:"Pratos",preco:34.9,ico:"🍔",foto:"assets/img/products/burger.jpg",status:"Disponível",desc:"Brioche, carne, queijo e molho da casa."},
  {id:4,nome:"Torta de Limão",cat:"Sobremesas",preco:16,ico:"🥧",foto:"assets/img/products/torta-limao.jpg",status:"Disponível",desc:"Base crocante, creme de limão e merengue."},
  {id:5,nome:"Suco de Laranja",cat:"Bebidas",preco:9.5,ico:"🍊",foto:"assets/img/products/suco-laranja.jpg",status:"Disponível",desc:"Suco natural 400 ml."},
  {id:6,nome:"Soda Italiana",cat:"Bebidas",preco:13,ico:"🥤",foto:"assets/img/products/soda-italiana.jpg",status:"Disponível",desc:"Maçã verde ou frutas vermelhas."},
  {id:7,nome:"Nhoque ao Sugo",cat:"Pratos",preco:37,ico:"🍝",foto:"assets/img/products/nhoque.jpg",status:"Indisponível",desc:"Nhoque artesanal com molho de tomate."},
  {id:8,nome:"Petit Gâteau",cat:"Sobremesas",preco:19.5,ico:"🍫",foto:"assets/img/products/petit-gateau.jpg",status:"Disponível",desc:"Chocolate quente com sorvete."}
];

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

const roleInfo = {
  cliente:{name:"Rafael Gomes",role:"Cliente",avatar:"RG",email:"rafael@exemplo.com"},
  cozinha:{name:"Marina Souza",role:"Cozinheira",avatar:"MS",email:"marina@saboreclic.com"},
  admin:{name:"Ana Martins",role:"Administradora",avatar:"AM",email:"ana@saboreclic.com"}
};

function findRoleByEmail(email){
  const e=(email||"").trim().toLowerCase();
  for(const r in roleInfo){ if(roleInfo[r].email.toLowerCase()===e) return r; }
  return null;
}
function money(v){return v.toLocaleString("pt-BR",{style:"currency",currency:"BRL"})}
