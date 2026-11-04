function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function head(title,desc,action='') {
  return `<div class="page-head"><div><h1>${escapeHtml(title)}</h1><p>${escapeHtml(desc)}</p></div>${action}</div>`;
}
function stat(label,value,extra='') {
  return `<div class="card stat"><div class="meta">${escapeHtml(label)}</div><div class="value">${escapeHtml(value)}</div><div class="delta muted">${escapeHtml(extra)}</div></div>`;
}
function productCard(p) {
  return `<div class="card"><h3>${escapeHtml(p.nome)}</h3><p class="meta">${escapeHtml(p.desc)}</p><div class="detail-row"><b>${money(p.preco)}</b><span class="badge">${escapeHtml(p.status)}</span></div><button class="btn" ${p.status!=='Disponível'?'disabled':''} onclick="addCart(${p.id})">Adicionar</button></div>`;
}
function empty(message='Nenhum registro encontrado.') { return `<p class="card">${escapeHtml(message)}</p>`; }
function grid(cards) { return cards.length ? `<section class="grid cols-3">${cards.join('')}</section>` : empty(); }
function table(headers,rows) {
  return rows.length ? `<section class="card table-wrap"><table><thead><tr>${headers.map(h=>`<th>${escapeHtml(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(cell=>`<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table></section>` : empty();
}
