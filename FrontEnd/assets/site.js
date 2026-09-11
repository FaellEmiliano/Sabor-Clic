// Camada de "app shell": sessão, menu, navegação entre páginas reais e utilitários de UI.
// Cada página HTML é um arquivo próprio (MPA); o estado de sessão e o carrinho
// são persistidos em localStorage para sobreviver ao recarregamento de página.

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

function handleLogout(){
  localStorage.removeItem("role");
  window.location.href = "index.html";
}

// Garante que só o dono da sessão certa acessa cada página.
// Sem login -> volta pro index. Login de outro perfil -> manda pro início do perfil correto.
function guardRole(expectedRole){
  const role = currentRole();
  if(!role){ window.location.href = "index.html"; return null; }
  if(role !== expectedRole){ window.location.href = homePageFor(role) + ".html"; return null; }
  return role;
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

