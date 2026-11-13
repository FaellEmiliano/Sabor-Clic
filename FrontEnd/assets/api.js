// Cookie authentication. CSRF token lives only in memory and is fetched on every page load.
let csrfToken = '';
async function api(path, options = {}) {
  const headers = {...options.headers};
  const multipart = options.body instanceof FormData;
  if (options.body !== undefined && !multipart) headers['Content-Type'] = 'application/json';
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;
  let response;
  try {
    response = await fetch((window.SABOR_API_BASE || '/api') + path, {
      ...options, headers, credentials: 'include',
      body: options.body === undefined ? undefined : multipart ? options.body : JSON.stringify(options.body)
    });
  } catch {
    throw new Error('Não foi possível conectar à API. Abra o sistema pelo servidor Flask.');
  }
  const data = await response.json().catch(() => ({erro: 'Resposta inválida da API.'}));
  if (!response.ok) {
    const error = new Error(data.erro || `Falha na requisição (${response.status}).`);
    error.status = response.status;
    throw error;
  }
  if (data.csrf_token) csrfToken = data.csrf_token;
  return data;
}
function uiRole(user) {
  return {cliente:'cliente', cozinheiro:'cozinha', administrador:'admin'}[user.tipo];
}
async function bootPage(expectedRole, pageId) {
  try {
    const data = await api('/me');
    currentUser = Usuario.fromJSON(data.usuario);
    const role = uiRole(currentUser);
    if (!role) throw new Error('Perfil de usuário inválido.');
    localStorage.setItem('role', role);
    if (role !== expectedRole) { go(homePageFor(role)); return; }
    roleInfo[role] = {name:currentUser.nome, role:currentUser.tipo,
      avatar:currentUser.nome.split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase()};
    loadCart();
    initShell(role, pageId);
    await renderCurrentPage(pageId);
  } catch (error) {
    if (error.status === 401) { localStorage.removeItem('role'); window.location.href='index.html'; return; }
    el('app').textContent = error.message;
  }
}
