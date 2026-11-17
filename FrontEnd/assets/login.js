// Escreve o erro na área de alertas do formulário de entrada.
function showLoginError(message) {
  const box = el('loginError');
  box.textContent = message;
  box.classList.add('show');
}
// Verifica os campos preenchidos antes de enviar as credenciais ao servidor.
function validateLoginForm(email,password) {
  if (!email.trim() || !password) { showLoginError('Preencha e-mail e senha.'); return false; }
  return true;
}
// Lê e valida e-mail e senha, tenta entrar na conta e abre a página inicial do perfil.
// Mostra o erro no próprio formulário.
async function handleLogin(event) {
  event.preventDefault();
  const button = event.target.querySelector('button[type="submit"]');
  if (!validateLoginForm(el('loginEmail').value,el('loginPassword').value)) return false;
  button.disabled = true;
  try {
    const data = await api('/login', {method:'POST',body:{email:el('loginEmail').value,senha:el('loginPassword').value}});
    const role = uiRole(data.usuario);
    if (!role) throw new Error('Perfil de usuário inválido.');
    localStorage.setItem('role',role);
    go(homePageFor(role));
  } catch(error) { showLoginError(error.message); }
  finally { button.disabled = false; }
  return false;
}
// Abre o formulário de cadastro de cliente e configura o envio dos dados. Quando o cadastro
// termina, permite que o cliente entre com as credenciais criadas.
function openSignup() {
  const existing = el('signupForm');
  if (existing) { existing.remove(); el('loginForm').hidden=false; return; }
  const form = document.createElement('form');
  form.id='signupForm';
  form.className='login-form';
  form.innerHTML='<h2>Criar conta de cliente</h2><label class="field">Nome<input name="nome" required maxlength="120"></label><label class="field">E-mail<input name="email" type="email" required maxlength="180"></label><label class="field">Endereço<input name="endereco_entrega" maxlength="255"></label><label class="field">Senha<input name="senha" type="password" required minlength="8"></label><p role="alert"></p><button class="btn" type="submit">Cadastrar</button><button class="btn secondary" type="button">Voltar ao login</button>';
  el('loginForm').hidden=true;
  form.querySelector('[type="button"]').onclick=()=>{form.remove();el('loginForm').hidden=false;};
  // Cria a conta, volta ao login e deixa o e-mail preenchido para facilitar a entrada.
  form.addEventListener('submit',async event=>{
    event.preventDefault();
    const button=form.querySelector('button'); button.disabled=true;
    try {
      const data=Object.fromEntries(new FormData(form));
      await api('/usuarios/cliente',{method:'POST',body:data});
      el('loginEmail').value=data.email;
      form.remove(); el('loginForm').hidden=false; showToast('Conta criada. Entre com sua senha.');
    } catch(error) { form.querySelector('[role="alert"]').textContent=error.message; }
    finally { button.disabled=false; }
  });
  el('loginForm').after(form);
}
// Se já houver uma sessão válida ao abrir a entrada, vai direto à página inicial do perfil.
(async function() {
  try { const data=await api('/me'); const role=uiRole(data.usuario); if(role) go(homePageFor(role)); }
  catch(error) { if(error.status !== 401) showLoginError(error.message); }
})();
