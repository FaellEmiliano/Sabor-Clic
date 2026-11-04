// Camada de "app shell": sessão, menu, navegação entre páginas reais e utilitários de UI.
// Cada página valida o cookie de sessão no servidor; o carrinho é local por usuário.

const ROLE_HOME = { cliente: "cliente_inicio", cozinha: "cozinha_dashboard", admin: "admin_dashboard" };

function el(id){ return document.getElementById(id); }

function showToast(msg){
  const t = el("toast");
  if(!t) return;
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 1800);
}

function toggleSidebar(){
  const open = el("sidebar").classList.toggle("open");
  const btn = el("sidebarToggle");
  if(btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
}

function currentRole(){ return localStorage.getItem("role"); }

function homePageFor(role){ return ROLE_HOME[role]; }

// Navegação real entre páginas (substitui o antigo go() de SPA por um redirect de verdade).
function go(pageId){ window.location.href = pageId + ".html"; }

async function handleLogout(){
  try {
    await api('/logout', {method:'POST',body:{}});
    localStorage.removeItem('role');
    window.location.href = 'index.html';
  } catch(error) { showToast(error.message); }
}

function renderMenu(role, activePage){
  el("menu").innerHTML = menus[role].map(([id, icon, label]) => `
    <a class="${activePage === id ? "active" : ""}" href="${id}.html" ${activePage === id ? 'aria-current="page"' : ""}><span aria-hidden="true">${icon}</span><span>${label}</span></a>
  `).join("");
}

function renderUserCard(role){
  const info = roleInfo[role];
  el("userName").textContent = info.name;
  el("userRole").textContent = info.role;
  el("avatar").textContent = info.avatar;
}

function renderCrumb(role, pageId){
  const item = menus[role].find(x => x[0] === pageId);
  const roleLabel = {cliente:"Cliente", cozinha:"Cozinha", admin:"Admin"}[role];
  el("crumb").textContent = `${roleLabel} / ${item ? item[2] : ""}`;
}

// Monta o "casco" da página (sidebar, usuário, breadcrumb, menu ativo).
function initShell(role, pageId){
  renderUserCard(role);
  renderMenu(role, pageId);
  renderCrumb(role, pageId);
}

