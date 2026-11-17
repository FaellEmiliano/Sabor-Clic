// Camada de "app shell": sessão, menu, navegação entre páginas reais e utilitários de UI.
// Cada página valida o cookie de sessão no servidor; o carrinho é local por usuário.

const ROLE_HOME = { cliente: "cliente_inicio", cozinha: "cozinha_dashboard", admin: "admin_dashboard" };

// Busca na página o elemento com a identificação indicada.
function el(id){ return document.getElementById(id); }

// Mostra um aviso curto na tela e o oculta após alguns segundos.
function showToast(msg){
  const t = el("toast");
  if(!t) return;
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 1800);
}

// Abre ou fecha o menu lateral.
function toggleSidebar(){
  const open = el("sidebar").classList.toggle("open");
  const btn = el("sidebarToggle");
  if(btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
}

// Lê o perfil de navegação guardado no navegador.
function currentRole(){ return localStorage.getItem("role"); }

// Devolve o nome da página inicial do perfil indicado.
function homePageFor(role){ return ROLE_HOME[role]; }

// Navegação real entre páginas (substitui o antigo go() de SPA por um redirect de verdade).
// Abre o arquivo HTML da página escolhida.
function go(pageId){ window.location.href = pageId + ".html"; }

// Pede ao servidor para encerrar o acesso, limpa os dados locais de navegação e volta à
// página de entrada.
async function handleLogout(){
  try {
    await api('/logout', {method:'POST',body:{}});
    localStorage.removeItem('role');
    window.location.href = 'index.html';
  } catch(error) { showToast(error.message); }
}

// Preenche o menu lateral com as opções daquele perfil e destaca a página aberta.
function renderMenu(role, activePage){
  el("menu").innerHTML = menus[role].map(([id, icon, label]) => `
    <a class="${activePage === id ? "active" : ""}" href="${id}.html" ${activePage === id ? 'aria-current="page"' : ""}><span aria-hidden="true">${icon}</span><span>${label}</span></a>
  `).join("");
}

// Mostra nome, perfil e iniciais da conta no cartão do menu.
function renderUserCard(role){
  const info = roleInfo[role];
  el("userName").textContent = info.name;
  el("userRole").textContent = info.role;
  el("avatar").textContent = info.avatar;
}

// Mostra no topo a localização da página dentro da área do perfil.
function renderCrumb(role, pageId){
  const item = menus[role].find(x => x[0] === pageId);
  const roleLabel = {cliente:"Cliente", cozinha:"Cozinha", admin:"Admin"}[role];
  el("crumb").textContent = `${roleLabel} / ${item ? item[2] : ""}`;
}

// Monta o "casco" da página (sidebar, usuário, breadcrumb, menu ativo).
// Monta os elementos que as telas internas compartilham, como o menu e a identificação da
// conta.
function initShell(role, pageId){
  renderUserCard(role);
  renderMenu(role, pageId);
  renderCrumb(role, pageId);
}

