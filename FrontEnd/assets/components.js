// Componentes de interface compartilhados.
// Separa a geração de componentes visuais das regras do carrinho e das páginas.

function head(title, desc, action = "") {
  return `<div class="page-head"><div><h1>${title}</h1><p>${desc}</p></div>${action}</div>`;
}

function stat(label, value, extra = "") {
  return `<div class="card stat"><div class="meta">${label}</div><div class="value">${value}</div><div class="delta muted">${extra}</div></div>`;
}

function benchCard(bench) {
  const badge = bench.status === "Disponível" ? "good" : bench.status === "Ocupada" ? "warn" : "danger";
  const ring = bench.status === "Disponível" ? "ok" : bench.status === "Ocupada" ? "busy" : "off";
  const visual = bench.foto ? `<img src="${bench.foto}" alt="${bench.nome}">` : `<span>${bench.emoji}</span>`;

  let resources = "";
  for (const resource of bench.recursos) {
    resources += resources ? ` • ${resource}` : resource;
  }

  return `<div class="card bench-card">
    <div class="visual ${ring}">${visual}</div>
    <div class="detail-row" style="margin-top:12px"><h3 style="margin:0">${bench.nome}</h3><span class="badge ${badge}">${bench.status}</span></div>
    <p class="meta">Até ${bench.cap} pessoas • ${resources}</p>
    <div class="detail-row"><span class="price">${money(bench.preco)}</span><span class="meta">por período</span></div>
    <div class="actions" style="margin-top:12px">
      <button class="btn secondary" onclick="showToast('Detalhes simulados da ${bench.nome}.')">Detalhes</button>
      <button class="btn" ${bench.status !== "Disponível" ? "disabled" : ""} onclick="go('cliente_reservas')">Reservar</button>
    </div>
  </div>`;
}

function productCard(product) {
  const ring = product.status === "Disponível" ? "ok" : "off";
  const visual = product.foto ? `<img src="${product.foto}" alt="${product.nome}">` : `<span>${product.ico}</span>`;

  return `<div class="card">
    <div class="visual ${ring}">${visual}</div>
    <div class="detail-row" style="margin-top:12px"><span class="badge">${product.cat}</span><span class="badge ${product.status === "Disponível" ? "good" : "danger"}">${product.status}</span></div>
    <h3>${product.nome}</h3><p class="meta">${product.desc}</p>
    <div class="detail-row"><span class="price">${money(product.preco)}</span><button class="btn" ${product.status !== "Disponível" ? "disabled" : ""} onclick="addCart(${product.id})">Adicionar</button></div>
  </div>`;
}

function ingredient(nome, atual, minimo, status) {
  return `<div class="card"><div class="detail-row"><h3>${nome}</h3><span class="badge ${status}">${status === "good" ? "OK" : "Baixo"}</span></div><p class="meta">Atual: ${atual} • Mínimo: ${minimo}</p><div class="progress"><span style="width:${status === "good" ? "78" : "38"}%"></span></div><div class="actions" style="margin-top:12px"><button class="btn secondary">Editar</button><button class="btn ghost">Movimentação</button></div></div>`;
}

function ticket(id, bancada, tempo, itens, acao, status) {
  return `<div class="ticket"><div class="detail-row"><h4>${id}</h4><span class="badge ${status}">${bancada}</span></div><p class="timer">${tempo}</p><ul>${itens.map(item => `<li>${item}</li>`).join("")}</ul><button class="btn ${status === "danger" ? "danger" : "secondary"} full" onclick="showToast('${acao} — simulado.')">${acao}</button></div>`;
}
