function fillLogin(email) {
  el("loginEmail").value = email;
  el("loginPassword").value = "demo1234";
}

function showLoginError(message) {
  const errBox = el("loginError");
  errBox.textContent = message;
  errBox.classList.add("show");
}

function validateLoginForm(email, password) {
  if (!email.trim() || !password.trim()) {
    showLoginError("Preencha e-mail e senha.");
    return false;
  }

  if (!email.includes("@") || !email.includes(".")) {
    showLoginError("Informe um e-mail válido.");
    return false;
  }

  return true;
}

function handleLogin(event) {
  event.preventDefault();

  const email = el("loginEmail").value;
  const password = el("loginPassword").value;
  const errBox = el("loginError");

  if (!validateLoginForm(email, password)) return false;

  const role = findRoleByEmail(email);
  if (!role) {
    showLoginError("Não encontramos essa conta. Use uma das contas de demonstração abaixo.");
    return false;
  }

  errBox.classList.remove("show");
  localStorage.setItem("role", role);
  window.location.href = homePageFor(role) + ".html";
  return false;
}

// Se já existe sessão ativa, pula o login e vai direto pro perfil.
(function redirectIfLoggedIn() {
  const role = currentRole();
  if (role) window.location.href = homePageFor(role) + ".html";
})();
