function fillLogin(email){
  el("loginEmail").value = email;
  el("loginPassword").value = "demo1234";
}
function handleLogin(event){
  event.preventDefault();
  const email = el("loginEmail").value;
  const role = findRoleByEmail(email);
  const errBox = el("loginError");
  if(!role){
    errBox.textContent = "Não encontramos essa conta. Use uma das contas de demonstração abaixo.";
    errBox.classList.add("show");
    return false;
  }
  errBox.classList.remove("show");
  localStorage.setItem("role", role);
  window.location.href = homePageFor(role) + ".html";
  return false;
}

// Se já existe sessão ativa, pula o login e vai direto pro perfil.
(function redirectIfLoggedIn(){
  const role = currentRole();
  if(role){ window.location.href = homePageFor(role) + ".html"; }
})();
