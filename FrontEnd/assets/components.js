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
  return `<div class="card">${catalogImage(p.imagem,p.nome)}<h3>${escapeHtml(p.nome)}</h3><p class="meta">${escapeHtml(p.desc)}</p><div class="detail-row"><b>${money(p.preco)}</b><span class="badge">${escapeHtml(p.status)}</span></div><button class="btn" ${p.status!=='Disponível'?'disabled':''} onclick="addCart(${p.id})">Adicionar</button></div>`;
}
function imageSource(path) {
  return typeof path==='string' && /^\/(assets\/img\/products\/[a-z0-9-]+\.jpg|media\/[a-f0-9]{32}\.webp)$/.test(path) ? path : '/assets/img/sem-foto.svg';
}
function catalogImage(path,name,small=false) {
  return `<img class="catalog-photo${small?' thumbnail':''}" src="${escapeHtml(imageSource(path))}" alt="${escapeHtml(name)}" loading="lazy" onerror="this.onerror=null;this.src='/assets/img/sem-foto.svg'">`;
}
function imagePickerHtml(record,library) {
  return `<fieldset class="image-picker"><legend>Foto (opcional)</legend>
    <input type="hidden" name="imagem" value="${escapeHtml(record.imagem||'')}">
    <img data-photo-preview class="photo-preview" src="${escapeHtml(imageSource(record.imagem))}" alt="Prévia da foto escolhida">
    <label>Enviar foto <input data-photo-file type="file" accept="image/jpeg,image/png,image/webp"></label>
    <p class="meta">JPEG, PNG ou WebP. Até 5 MB e 20 megapixels. A foto enviada fica disponível para reutilização na biblioteca.</p>
    <button class="btn secondary" type="button" data-photo-clear>Deixar sem foto</button>
    <p>Ou escolha da biblioteca:</p><div class="photo-library" aria-label="Biblioteca de imagens">
    ${library.map(item=>`<button type="button" class="photo-option" data-photo-path="${escapeHtml(item.caminho)}" aria-label="${escapeHtml(item.nome)}" aria-pressed="${record.imagem===item.caminho}">${catalogImage(item.caminho,item.nome,true)}<span>${escapeHtml(item.nome)}</span><small>${item.origem==='upload'?'Enviada':'Biblioteca'}</small></button>`).join('')}
    </div></fieldset>`;
}
function bindImagePicker(form) {
  const fileInput=form.querySelector('[data-photo-file]');
  const preview=form.querySelector('[data-photo-preview]');
  const options=[...form.querySelectorAll('[data-photo-path]')];
  let reader;
  const select=path=>{
    if(reader) reader.abort();
    fileInput.value=''; form.elements.imagem.value=path;
    preview.src=imageSource(path);
    options.forEach(option=>option.setAttribute('aria-pressed',String(option.dataset.photoPath===path)));
    form.querySelector('[role="alert"]').textContent='';
  };
  options.forEach(option=>option.addEventListener('click',()=>select(option.dataset.photoPath)));
  form.querySelector('[data-photo-clear]').addEventListener('click',()=>select(''));
  fileInput.addEventListener('change',()=>{
    if(reader) reader.abort();
    const file=fileInput.files[0];
    if(!file) { preview.src=imageSource(form.elements.imagem.value); return; }
    if(file.size>5*1024*1024 || !['image/jpeg','image/png','image/webp'].includes(file.type)) {
      fileInput.value=''; preview.src=imageSource(form.elements.imagem.value);
      form.querySelector('[role="alert"]').textContent='Use uma foto JPEG, PNG ou WebP de até 5 MB.';
      return;
    }
    form.querySelector('[role="alert"]').textContent='';
    options.forEach(option=>option.setAttribute('aria-pressed','false'));
    reader=new FileReader(); reader.onload=()=>{preview.src=reader.result;}; reader.readAsDataURL(file);
  });
}
function empty(message='Nenhum registro encontrado.') { return `<p class="card">${escapeHtml(message)}</p>`; }
function grid(cards) { return cards.length ? `<section class="grid cols-3">${cards.join('')}</section>` : empty(); }
function table(headers,rows) {
  return rows.length ? `<section class="card table-wrap"><table><thead><tr>${headers.map(h=>`<th>${escapeHtml(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(cell=>`<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table></section>` : empty();
}
