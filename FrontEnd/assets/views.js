// All views consume authenticated API data. No demo records or fallback statistics.
let pageData = {};
let activePage = '';
let refreshTimer;
let pageLoading = false;
const e = escapeHtml;
const labelStatus = status => ({confirmada:'Confirmada',em_andamento:'Em andamento',concluida:'Concluída',cancelada:'Cancelada',ativa:'Ativa',encerrada:'Encerrada',recebido:'Recebido',em_preparo:'Em preparo',pronto:'Pronto',entregue:'Entregue',cancelado:'Cancelado'}[status] || status);
const badge = status => `<span class="badge">${e(labelStatus(status))}</span>`;
const button = (label,action,style='secondary') => `<button class="btn ${style}" onclick="${action}">${e(label)}</button>`;
const dates = value => value ? new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'short',timeStyle:'short'}).format(new Date(value)) : '—';
function dateToInput(value){const parts=new Intl.DateTimeFormat('sv-SE',{timeZone:'America/Sao_Paulo',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date(value));return parts.replace(' ','T');}
function benchName(id) { return (pageData.bancadas || []).find(b=>b.id_bancada===id)?.nome || `Bancada #${id}`; }
function dishName(id) { return (pageData.pratos || []).find(p=>p.id_prato===id)?.nome || `Prato #${id}`; }
function ingredientName(id) { return (pageData.ingredientes || []).find(i=>i.id_ingrediente===id)?.nome || `Ingrediente #${id}`; }
function userName(id) { return (pageData.usuarios || []).find(u=>u.id_usuario===id)?.nome || `Cliente #${id}`; }
function activeSession(){const list=(pageData.sessoes||[]).filter(s=>s.status==='ativa');const id=Number(localStorage.getItem('selected-session:'+currentUser.id_usuario)||0);return list.find(s=>s.id_sessao===id)||list[0];}
function sessionSelector(){const list=(pageData.sessoes||[]).filter(s=>s.status==='ativa');if(list.length<2)return '';return `<label class="field">Sessão do atendimento<select onchange="selectSession(this.value)">${list.map(s=>`<option value="${s.id_sessao}" ${activeSession()?.id_sessao===s.id_sessao?'selected':''}>Sessão #${s.id_sessao} · Reserva #${s.id_reserva}</option>`).join('')}</select></label>`;}
function selectSession(id){localStorage.setItem('selected-session:'+currentUser.id_usuario,id);resourcePages.pedidos=1;renderCurrentPage(activePage);}
const resourcePages={};
const resourceSearch={};
let reportPeriod={};
let orderFilter={};
const PAGE_RESOURCES={
 cliente_inicio:['bancadas','reservas','sessoes','pedidos'],cliente_bancadas:['bancadas'],cliente_reservas:['bancadas','reservas'],
 cliente_sessao:['bancadas','reservas','sessoes','pedidos'],cliente_cardapio:['pratos','sessoes'],cliente_carrinho:['pratos','sessoes'],cliente_pedidos:['pedidos'],cliente_perfil:[],
 cozinha_dashboard:['kds','resumo-cozinha'],cozinha_kds:['kds'],cozinha_pedidos:['pedidos'],cozinha_estoque:['pratos'],cozinha_historico:['pedidos'],
 admin_dashboard:['pedidos','relatorios'],admin_reservas:['bancadas','reservas','sessoes','usuarios'],admin_bancadas:['bancadas'],
 admin_produtos:['pratos','ingredientes','fichas-tecnicas'],admin_ingredientes:['ingredientes','movimentacoes'],admin_substituicoes:['ingredientes','substituicoes'],admin_usuarios:['usuarios','auditoria'],admin_relatorios:['relatorios']
};
async function loadPageData(pageId){
 const resources=PAGE_RESOURCES[pageId]||[];
 const result=await Promise.all(resources.map(resource=>{
   if(resource==='sessoes'&&pageId.startsWith('cliente_'))return fetchReferenceOptions('sessoes','&status=ativa').then(sessoes=>({sessoes}));
   const args=new URLSearchParams();
   if(resource==='sessoes'&&(pageId.startsWith('cliente_')||pageId==='admin_reservas'))args.set('status','ativa');
   if(resource==='pedidos'&&pageId==='admin_dashboard')args.set('situacao','ativos');
   if(resource!=='relatorios'){
     if(resourcePages[resource]>1)args.set('pagina',resourcePages[resource]);
     if(resourceSearch[resource])args.set('q',resourceSearch[resource]);
   }
   if(resource==='relatorios')for(const [key,value]of Object.entries(reportPeriod))if(value)args.set(key,value);
   if(resource==='pedidos'){
     if(pageId==='cozinha_historico')args.set('situacao','finalizados');
     if(['cozinha_pedidos','cliente_pedidos'].includes(pageId))for(const [key,value]of Object.entries(orderFilter))if(value)args.set(key,value);
   }
   return api('/'+resource+(args.size?'?'+args:''));
 }));
 pageData={metadados:{}};
 for(let index=0;index<result.length;index++){const {metadados,...values}=result[index];if(resources[index]==='relatorios')pageData.relatorios=values;else Object.assign(pageData,values);Object.assign(pageData.metadados,metadados||{});}
 if(pageData.pratos)products.splice(0,products.length,...pageData.pratos.map(Prato.fromJSON));
 if(pageData.bancadas)benches.splice(0,benches.length,...pageData.bancadas);
 const lookups={cliente_reservas:['bancadas'],admin_reservas:['bancadas','usuarios'],admin_produtos:['ingredientes'],admin_substituicoes:['ingredientes']}[pageId]||[];
 for(const resource of lookups)pageData[resource]=await fetchReferenceOptions(resource);
 const active=activeSession();
 if(['cliente_inicio','cliente_sessao'].includes(pageId)&&active&&pageData.reservas&&!pageData.reservas.some(r=>r.id_reserva===active.id_reserva)){
   const linked=await api('/reservas/'+active.id_reserva);pageData.reservas.push(linked.reserva);
 }
 if(['cliente_inicio','cliente_sessao'].includes(pageId)&&active){
   const detail=await api('/sessoes/'+active.id_sessao);pageData.resumo_sessao=detail.resumo;
   const orders=await api('/pedidos?id_sessao='+active.id_sessao+'&pagina='+(resourcePages.pedidos||1));pageData.pedidos=orders.pedidos;Object.assign(pageData.metadados,orders.metadados||{});
 }
 state.carrinho.atualizarCatalogo(products);saveCart();
}
async function fetchReferenceOptions(resource,filters=''){
 const key=resource.replaceAll('-','_');const records=[];let page=1;
 while(true){const result=await api('/'+resource+'?limite=100&pagina='+page+filters);records.push(...result[key]);const meta=result.metadados?.[key];if(!meta||records.length>=meta.total)break;page++;}
 return records;
}
function pager(resource,key=resource.replaceAll('-','_')){
 const meta=pageData.metadados?.[key];if(!meta||meta.total<=meta.limite)return '';
 return `<div class="actions"><button class="btn secondary" ${meta.pagina===1?'disabled':''} onclick="setResourcePage('${resource}',${meta.pagina-1})">Anterior</button><span>Página ${meta.pagina} de ${Math.ceil(meta.total/meta.limite)} · ${meta.total} registros</span><button class="btn secondary" ${meta.pagina*meta.limite>=meta.total?'disabled':''} onclick="setResourcePage('${resource}',${meta.pagina+1})">Próxima</button></div>`;
}
function setResourcePage(resource,page){resourcePages[resource]=page;renderCurrentPage(activePage);}
function searchResource(event,resource){event.preventDefault();resourceSearch[resource]=new FormData(event.target).get('q');resourcePages[resource]=1;renderCurrentPage(activePage);}
function searchForm(resource){return `<form class="filterbar" onsubmit="searchResource(event,'${resource}')"><label>Buscar<input name="q" value="${e(resourceSearch[resource]||'')}" placeholder="Nome ou descrição"></label><button class="btn secondary" type="submit">Buscar</button></form>`;}

async function renderCurrentPage(pageId,quiet=false) {
  if (pageLoading) return;
  activePage=pageId;
  pageLoading=true;
  clearTimeout(refreshTimer);
  if(!quiet) el('app').innerHTML='<p role="status">Carregando…</p>';
  try {
    await loadPageData(pageId);
    el('app').innerHTML=views[pageId]();
  } catch(error) {
    if(error.status===401) { localStorage.removeItem('role'); window.location.href='index.html'; return; }
    if(!quiet) el('app').innerHTML=`<p class="card" role="alert">${e(error.message)}</p>${button('Tentar novamente',`renderCurrentPage('${pageId}')`)}`;
    else showToast(error.message);
  } finally {
    pageLoading=false;
    if(['cliente_inicio','cliente_sessao','cliente_pedidos','cozinha_dashboard','cozinha_pedidos','cozinha_kds','cozinha_historico','admin_dashboard'].includes(pageId)) {
      refreshTimer=setTimeout(()=>{if(!document.hidden) renderCurrentPage(pageId,true); else renderLater(pageId);},10000);
    }
  }
}
function renderLater(pageId) { refreshTimer=setTimeout(()=>renderCurrentPage(pageId,true),10000); }
async function perform(path,method,body,success) {
  try {
    await api(path,{method,body});
    if(success) showToast(success);
    await renderCurrentPage(activePage);
    return true;
  } catch(error) { showToast(error.message); return false; }
}
function reservationCards() {
  return grid((pageData.reservas||[]).map(r=>`<div class="card"><div class="detail-row"><b>#${r.id_reserva} · ${e(benchName(r.id_bancada))}</b>${badge(r.status)}</div><p>${e(dates(r.inicio))} a ${e(dates(r.fim))}</p><p>${money(r.valor_total)}</p>${r.status==='confirmada'?button('Reagendar',`editReservation(${r.id_reserva})`)+button('Iniciar sessão',`perform('/sessoes','POST',{id_reserva:${r.id_reserva}},'Sessão iniciada.')`)+button('Cancelar',`perform('/reservas/${r.id_reserva}','PATCH',{status:'cancelada'},'Reserva cancelada.')`,'danger'):''}</div>`));
}
function reservationForm(admin=false) {
  return `<form id="reservationForm" class="card" onsubmit="submitReservation(event)"><h2>Nova reserva</h2><div class="form-grid">
    ${admin?`<label>Cliente<select name="id_cliente" required>${(pageData.usuarios||[]).filter(u=>u.tipo==='cliente'&&u.ativo).map(u=>`<option value="${u.id_usuario}">${e(u.nome)}</option>`).join('')}</select></label>`:''}
    <label>Bancada<select name="id_bancada" required>${pageData.bancadas.filter(b=>b.ativa).map(b=>`<option value="${b.id_bancada}">${e(b.nome)} · ${money(b.valor_hora)}/hora</option>`).join('')}</select></label>
    <label>Início<input name="inicio" type="datetime-local" required></label><label>Fim<input name="fim" type="datetime-local" required></label></div>
    <p class="meta">O servidor confirma a disponibilidade e calcula o valor pela duração e tarifa da bancada.</p><p role="alert"></p><button class="btn" type="submit">Confirmar reserva</button></form>`;
}
async function submitReservation(event) {
  event.preventDefault();
  const form=event.target;
  const data=Object.fromEntries(new FormData(form));
  const error=reservationPeriodError(data.inicio,data.fim);
  if(error) { form.querySelector('[role="alert"]').textContent=error; return; }
  const submit=form.querySelector('[type="submit"]'); submit.disabled=true;
  try {
    const id=form.dataset.reservationId;
    await api('/reservas'+(id?'/'+id:''),{method:id?'PATCH':'POST',body:data});
    form.closest('dialog')?.close();
    showToast(id?'Reserva atualizada.':'Reserva criada.'); await renderCurrentPage(activePage);
  }
  catch(error) { form.querySelector('[role="alert"]').textContent=error.message; }
  finally { submit.disabled=false; }
}
function editReservation(id) {
  const record=pageData.reservas.find(r=>r.id_reserva===id);
  const dialog=document.createElement('dialog'); dialog.className='card';
  dialog.innerHTML=reservationForm(currentUser.tipo==='administrador');
  const form=dialog.querySelector('form');
  form.removeAttribute('id'); form.dataset.reservationId=id;
  form.querySelector('h2').textContent='Reagendar reserva #'+id;
  form.querySelector('[type="submit"]').textContent='Salvar alterações';
  for(const field of ['id_cliente','id_bancada','inicio','fim']) {
    if(form.elements[field]) form.elements[field].value=field==='inicio'||field==='fim'?dateToInput(record[field]):record[field];
  }
  const cancel=document.createElement('button'); cancel.type='button'; cancel.className='btn secondary'; cancel.textContent='Cancelar'; cancel.onclick=()=>dialog.close(); form.append(cancel);
  document.body.append(dialog); dialog.addEventListener('close',()=>dialog.remove()); dialog.showModal();
}
function orderCards(records,kitchen=false,compact=false){
 const cards=records.map(p=>{
   const next={recebido:'em_preparo',em_preparo:'pronto',pronto:'entregue'}[p.status];
   const minutes=Math.max(0,Math.floor((Date.now()-new Date(p.preparo_em||p.criado_em).getTime())/60000));
   const late=p.tempo_estimado!=null&&minutes>p.tempo_estimado&&!['entregue','cancelado'].includes(p.status);
   return `<article class="card"><div class="detail-row"><h3>Pedido #${p.id_pedido}</h3>${badge(p.status)}</div><p>${e(p.bancada)} · ${e(dates(p.criado_em))}</p>
    <p class="${late?'badge danger':'meta'}">${minutes} min · ${p.tempo_estimado==null?'Sem estimativa':'Estimativa: '+p.tempo_estimado+' min'}${late?' · Atrasado':''}</p>
    <div class="timeline">${['recebido','em_preparo','pronto','entregue'].map((status,index)=>`<div class="${index<=['recebido','em_preparo','pronto','entregue'].indexOf(p.status)?'on':''}">${e(labelStatus(status))}</div>`).join('')}</div>
    <ul>${p.itens.map(i=>`<li>${i.quantidade} × ${e(i.nome)} · ${money(i.subtotal)}</li>`).join('')}</ul>
    ${p.observacoes?`<p>Observações: ${e(p.observacoes)}</p>`:''}${p.endereco_entrega?`<p>Entrega: ${e(p.endereco_entrega)}</p>`:''}<p><b>${money(p.valor_total)}</b></p>
    ${kitchen&&next?button({recebido:'Iniciar preparo',em_preparo:'Marcar pronto',pronto:'Marcar entregue'}[p.status],`perform('/pedidos/${p.id_pedido}','PATCH',{status:'${next}'},'Pedido atualizado.')`):''}
    ${kitchen&&next?`<form onsubmit="setEstimate(event,${p.id_pedido})"><label>Estimativa em minutos<input type="number" name="minutos" min="0" max="1440" required value="${p.tempo_estimado??15}"></label><button class="btn secondary" type="submit">Salvar estimativa</button></form>`:''}
    ${currentUser.tipo==='administrador'&&next?button('Cancelar pedido',`cancelOrder(${p.id_pedido})`,'danger'):''}
   </article>`;
 });
 return cards.length?(compact?`<div class="list">${cards.join('')}</div>`:grid(cards)):empty();
}
async function setEstimate(event,id){event.preventDefault();const form=event.target;const button=form.querySelector('button');button.disabled=true;await perform('/pedidos/'+id,'PATCH',{tempo_estimado:Number(new FormData(form).get('minutos'))},'Estimativa salva.');button.disabled=false;}
async function cancelOrder(id){if(window.confirm('Cancelar este pedido? Ingredientes só serão devolvidos se o preparo ainda não começou.'))await perform('/pedidos/'+id,'PATCH',{status:'cancelado'},'Pedido cancelado.');}
function orderFilters(){return `<form class="filterbar" onsubmit="applyOrderFilters(event)"><label>Estado<select name="status"><option value="">Todos</option>${['recebido','em_preparo','pronto','entregue','cancelado'].map(s=>`<option value="${s}" ${orderFilter.status===s?'selected':''}>${e(labelStatus(s))}</option>`).join('')}</select></label><label>Número do pedido<input name="id_pedido" type="number" min="1" value="${e(orderFilter.id_pedido||'')}"></label><button class="btn secondary" type="submit">Filtrar</button></form>`;}
function applyOrderFilters(event){event.preventDefault();orderFilter=Object.fromEntries(new FormData(event.target));resourcePages.pedidos=1;renderCurrentPage(activePage);}

function sessionView() {
  const s=activeSession();
  if(!s) return head('Sessão atual','Nenhuma sessão ativa.')+button('Ver reservas',"go('cliente_reservas')");
  const r=pageData.reservas.find(r=>r.id_reserva===s.id_reserva);
  const orders=pageData.pedidos.filter(p=>p.id_sessao===s.id_sessao);
  return head(`Sessão #${s.id_sessao}`,`${benchName(r.id_bancada)} · até ${dates(r.fim)}`)+sessionSelector()+
    `<section class="grid cols-3">${stat('Pedidos',pageData.resumo_sessao.pedidos)}${stat('Consumo',money(pageData.resumo_sessao.consumo))}${stat('Aluguel',money(r.valor_total))}</section>`+
    `<p>${button('Abrir cardápio',"go('cliente_cardapio')")}${button('Encerrar sessão',`perform('/sessoes/${s.id_sessao}/encerrar','POST',{},'Sessão encerrada.')`,'danger')}</p>`+orderCards(orders)+pager('pedidos');
}
function cartView() {
  const session=activeSession();
  return head('Carrinho','O preço final é confirmado pelo servidor ao enviar o pedido.')+sessionSelector()+
    table(['Item','Quantidade','Subtotal','Ação'],state.cart.map(i=>[e(i.nome),`<input aria-label="Quantidade de ${e(i.nome)}" type="number" min="1" max="1000" value="${i.qtd}" id="cartQty${i.id}">`,money(i.preco*i.qtd),button('Atualizar',`changeQuantity(${i.id},document.getElementById('cartQty${i.id}').value)`)+button('Remover',`delCart(${i.id})`,'danger')]))+
    `<div class="card"><label class="field">Endereço do pedido (opcional)<input id="orderAddress" maxlength="255" value="${e(currentUser.endereco_entrega)}"></label><label class="field">Observações<textarea id="orderNotes" maxlength="500"></textarea></label><p>Total estimado: <b>${money(state.carrinho.total)}</b></p><p>${session?`Sessão #${session.id_sessao}`:'Inicie uma sessão na tela de reservas para fazer um pedido.'}</p><button class="btn" onclick="submitOrder(this)" ${!session||!state.cart.length?'disabled':''}>Enviar pedido</button></div>`;
}
async function submitOrder(button) {
  const session=activeSession();
  if(!session||!state.cart.length) return;
  button.disabled=true;
  try {
    const order=new Pedido(session.id_sessao,state.carrinho,{
      endereco_entrega:el('orderAddress')?.value,observacoes:el('orderNotes')?.value});
    const storageKey='pending-order:'+currentUser.id_usuario;
    let pending;
    try{pending=JSON.parse(localStorage.getItem(storageKey)||'null');}catch{pending=null;}
    const key=pending?.assinatura===order.assinatura?pending.chave:order.chave;
    localStorage.setItem(storageKey,JSON.stringify({assinatura:order.assinatura,chave:key}));
    await api('/pedidos',{method:'POST',headers:{'Idempotency-Key':key},body:order.toPayload()});
    localStorage.removeItem(storageKey);
    state.cart=[]; saveCart(); showToast('Pedido enviado à cozinha.'); go('cliente_pedidos');
  } catch(error) { showToast(error.message); button.disabled=false; }
}
function profileView() {
  return head('Meu perfil','Atualize seus dados.')+`<form class="card" onsubmit="saveProfile(event)"><div class="form-grid"><label>Nome<input name="nome" value="${e(currentUser.nome)}" required maxlength="120"></label><label>E-mail<input name="email" type="email" value="${e(currentUser.email)}" required maxlength="180"></label><label>Endereço<input name="endereco_entrega" value="${e(currentUser.endereco_entrega||'')}" maxlength="255"></label><label>Nova senha<input name="senha" type="password" minlength="8" autocomplete="new-password"></label></div><p role="alert"></p><button class="btn" type="submit">Salvar alterações</button></form>`;
}
async function saveProfile(event) {
  event.preventDefault(); const form=event.target; const data=Object.fromEntries(new FormData(form)); if(!data.senha) delete data.senha;
  const submit=form.querySelector('button'); submit.disabled=true;
  try {
    const result=await api('/usuarios/'+currentUser.id_usuario,{method:'PATCH',body:data}); currentUser=Usuario.fromJSON(result.usuario);
    roleInfo.cliente.name=currentUser.nome; renderUserCard('cliente'); showToast('Perfil atualizado.');
  } catch(error) { form.querySelector('[role="alert"]').textContent=error.message; }
  finally { submit.disabled=false; }
}
function dashboard(admin=false) {
  const orders=pageData.pedidos;
  const summary=admin?{ativos:pageData.relatorios.pedidos_ativos,entregues:pageData.relatorios.pedidos_entregues,em_preparo:null}:pageData.resumo;
  const cards=[stat('Pedidos ativos',summary.ativos),stat('Entregues',summary.entregues),stat('Em preparo',summary.em_preparo??orders.filter(p=>p.status==='em_preparo').length)];
  if(admin) cards.push(stat('Reservas',pageData.relatorios.reservas),stat('Receita concluída',money(pageData.relatorios.receita_pedidos+pageData.relatorios.receita_reservas)));
  return head(admin?'Dashboard':'Visão geral da cozinha','Dados atuais do sistema.')+`<section class="grid cols-3">${cards.join('')}</section>`+orderCards(orders.filter(p=>!['entregue','cancelado'].includes(p.status)),true)+pager(admin?'pedidos':'kds','pedidos');
}
function catalogTable(resource) {
  const definitions={
    bancadas:{title:'Bancadas',headers:['Nome','Tarifa/hora','Ativa'],cells:r=>[e(r.nome),money(r.valor_hora),r.ativa?'Sim':'Não'],key:r=>r.id_bancada},
    pratos:{title:'Produtos',headers:['Foto','Nome','Preço','Ativo'],cells:r=>[catalogImage(r.imagem,r.nome,true),e(r.nome),money(r.preco),r.ativo?'Sim':'Não'],key:r=>r.id_prato},
    ingredientes:{title:'Ingredientes',headers:['Foto','Nome','Unidade','Estoque'],cells:r=>[catalogImage(r.imagem,r.nome,true),e(r.nome),e(r.unidade_medida),e(r.quantidade_estoque)],key:r=>r.id_ingrediente},
    substituicoes:{title:'Substituições',headers:['Original','Substituto','Prioridade','Fator'],cells:r=>[e(ingredientName(r.id_ingrediente_original)),e(ingredientName(r.id_ingrediente_substituto)),e(r.prioridade),e(r.fator_conversao)],key:r=>`${r.id_ingrediente_original}/substitutos/${r.id_ingrediente_substituto}`},
    'fichas-tecnicas':{title:'Fichas técnicas',headers:['Prato','Ingrediente','Quantidade'],cells:r=>[e(dishName(r.id_prato)),e(ingredientName(r.id_ingrediente)),e(r.quantidade_necessaria)],key:r=>`${r.id_prato}/ingredientes/${r.id_ingrediente}`}
  };
  const d=definitions[resource]; const records=pageData[resource.replaceAll('-','_')]||[];
  return head(d.title,'Cadastros persistidos no banco.',button('Adicionar',`editRecord('${resource}')`))+(['bancadas','pratos','ingredientes'].includes(resource)?searchForm(resource):'')+
    table([...d.headers,'Ações'],records.map((r,index)=>[...d.cells(r),button('Editar',`editRecord('${resource}',${index})`)+button(resource==='pratos'?'Inativar':'Excluir',`deleteRecord('${resource}','${d.key(r)}')`,'danger')]))+pager(resource);
}
const schemas={
  bancadas:[['nome','Nome','text'],['descricao','Descrição','text'],['valor_hora','Valor por hora','number'],['ativa','Ativa','checkbox']],
  pratos:[['nome','Nome','text'],['descricao','Descrição','text'],['preco','Preço','number'],['ativo','Ativo','checkbox']],
  ingredientes:[['nome','Nome','text'],['unidade_medida','Unidade de medida','text'],['quantidade_estoque','Estoque','number']],
  'fichas-tecnicas':[['id_prato','Prato','pratos'],['id_ingrediente','Ingrediente','ingredientes'],['quantidade_necessaria','Quantidade necessária','number']],
  substituicoes:[['id_ingrediente_original','Ingrediente original','ingredientes'],['id_ingrediente_substituto','Ingrediente substituto','ingredientes'],['prioridade','Prioridade','number'],['fator_conversao','Fator de conversão','number']],
  usuarios:[['tipo','Perfil','perfis'],['nome','Nome','text'],['email','E-mail','email'],['senha','Senha','password'],['endereco_entrega','Endereço do cliente','text'],['turno','Turno do cozinheiro','text'],['especialidade','Especialidade do cozinheiro','text'],['ativo','Ativo','checkbox']]
};
function fieldHtml(field,record,edit,formOptions={}) {
  const [name,label,type]=field;
  const fixed=edit&&(name.startsWith('id_')||name==='tipo');
  let input;
  if(['pratos','ingredientes','perfis'].includes(type)) {
    const options=type==='perfis'?[{id:'cliente',nome:'Cliente'},{id:'cozinheiro',nome:'Cozinheiro'},{id:'administrador',nome:'Administrador'}]:(formOptions[type]||pageData[type]).map(r=>({id:r[type==='pratos'?'id_prato':'id_ingrediente'],nome:r.nome}));
    input=`<select name="${name}" ${fixed?'disabled':''}>${options.map(o=>`<option value="${o.id}" ${String(record[name])===String(o.id)?'selected':''}>${e(o.nome)}</option>`).join('')}</select>`;
  } else if(type==='checkbox') input=`<input type="checkbox" name="${name}" ${record[name]!==false?'checked':''}>`;
  else input=`<input name="${name}" type="${type}" value="${type==='password'?'':e(record[name]??(['prioridade','fator_conversao'].includes(name)?1:name==='quantidade_estoque'?0:''))}" ${['nome','email','valor_hora','preco','unidade_medida','quantidade_necessaria'].includes(name)||type==='password'&&!edit?'required':''} ${type==='number'?'min="0" step="any"':''} ${type==='password'?'minlength="8" autocomplete="new-password"':''}>`;
  return `<label>${e(label)}${input}</label>`;
}
function recordKey(resource,r) {
  if(resource==='fichas-tecnicas') return `${r.id_prato}/ingredientes/${r.id_ingrediente}`;
  if(resource==='substituicoes') return `${r.id_ingrediente_original}/substitutos/${r.id_ingrediente_substituto}`;
  return r[{bancadas:'id_bancada',pratos:'id_prato',ingredientes:'id_ingrediente',usuarios:'id_usuario'}[resource]];
}
async function editRecord(resource,index) {
  const edit=Number.isInteger(index); const record=edit?pageData[resource.replaceAll('-','_')][index]:{};
  const formOptions={};
  const hasImage=['pratos','ingredientes'].includes(resource);
  let library=[];
  try{if(hasImage) library=(await api('/imagens')).imagens;for(const lookup of new Set(schemas[resource].map(field=>field[2]).filter(type=>['pratos','ingredientes'].includes(type))))formOptions[lookup]=await fetchReferenceOptions(lookup);}catch(error){showToast(error.message);return;}
  const dialog=document.createElement('dialog'); dialog.className='card'; dialog.style.maxWidth='720px';
  dialog.innerHTML=`<form><h2>${edit?'Editar':'Adicionar'}</h2><div class="form-grid">${schemas[resource].map(f=>fieldHtml(f,record,edit,formOptions)).join('')}</div>${hasImage?imagePickerHtml(record,library):''}<p role="alert"></p><div class="actions"><button type="submit" class="btn">Salvar</button><button type="button" data-cancel class="btn secondary">Cancelar</button></div></form>`;
  document.body.append(dialog);
  dialog.addEventListener('close',()=>dialog.remove());
  dialog.querySelector('[data-cancel]').onclick=()=>dialog.close();
  const form=dialog.querySelector('form');
  if(hasImage) bindImagePicker(form);
  if(resource==='usuarios') {
    const updateFields=()=>{
      const type=form.elements.tipo.value;
      for(const name of ['endereco_entrega','turno','especialidade']) {
        const enabled=name==='endereco_entrega'?type==='cliente':type==='cozinheiro';
        form.elements[name].disabled=!enabled; form.elements[name].closest('label').hidden=!enabled;
      }
    };
    form.elements.tipo.addEventListener('change',updateFields); updateFields();
  }
  form.addEventListener('submit',async event=>{
    event.preventDefault(); const data=Object.fromEntries(new FormData(form));
    for(const [name,,type] of schemas[resource]) if(type==='checkbox'&&!form.elements[name].disabled) data[name]=form.elements[name].checked;
    if(resource==='usuarios') {
      if(edit&&!data.senha) delete data.senha;
      if(data.tipo==='cliente'&&!edit) delete data.ativo;
    }
    let path='/'+resource+(edit?'/'+recordKey(resource,record):'');
    if(resource==='usuarios'&&!edit) path+='/'+data.tipo;
    delete data.tipo;
    const submit=form.querySelector('[type="submit"]'); submit.disabled=true;
    const imagePicker=form.querySelector('.image-picker');
    if(imagePicker) imagePicker.disabled=true;
    try {
      if(hasImage) {
        const file=form.querySelector('[data-photo-file]').files[0];
        if(file) {
          const upload=new FormData(); upload.append('foto',file);
          const result=await api('/imagens',{method:'POST',body:upload});
          data.imagem=result.imagem.caminho;
          form.elements.imagem.value=data.imagem;
          form.querySelector('[data-photo-file]').value='';
        }
        data.imagem=data.imagem||null;
      }
      await api(path,{method:edit?'PATCH':'POST',body:data}); dialog.close(); showToast('Registro salvo.'); await renderCurrentPage(activePage); }
    catch(error) { form.querySelector('[role="alert"]').textContent=error.message; }
    finally { submit.disabled=false; if(imagePicker) imagePicker.disabled=false; }
  });
  dialog.showModal();
}
async function deleteRecord(resource,key) {
  if(!window.confirm(resource==='pratos'?'Inativar este prato?':'Excluir este registro? Registros com histórico serão preservados.')) return;
  await perform('/'+resource+'/'+key,'DELETE',undefined,'Registro excluído.');
}
function usersView() {
  return head('Usuários','Gerencie clientes, cozinheiros e administradores.',button('Adicionar',"editRecord('usuarios')"))+searchForm('usuarios')+
    table(['Nome','E-mail','Perfil','Ativo','Ações'],pageData.usuarios.map((u,index)=>[e(u.nome),e(u.email),e(u.tipo),u.ativo?'Sim':'Não',button('Editar',`editRecord('usuarios',${index})`)+button(u.ativo?'Desativar':'Ativar',`perform('/usuarios/${u.id_usuario}/status','PATCH',{},'Usuário atualizado.')`)+button('Excluir',`deleteRecord('usuarios','${u.id_usuario}')`,'danger')]))+pager('usuarios')+head('Auditoria','Operações críticas, sem senhas ou tokens.')+table(['Data','Usuário','Operação','Recurso','Resultado'],(pageData.eventos||[]).map(a=>[e(dates(a.criado_em)),e(a.id_usuario||'Anônimo'),e(a.acao),e(a.recurso),e(a.resultado)]))+pager('auditoria','eventos');
}
const views={
  cliente_inicio:()=>head(`Olá, ${currentUser.nome}.`,'Gerencie sua reserva, sessão e pedidos.')+sessionView(),
  cliente_bancadas:benchesView,
  cliente_reservas:()=>head('Minhas reservas','Reservas e horários de atendimento.')+reservationCards()+pager('reservas')+reservationForm(),
  cliente_sessao:sessionView,
  cliente_cardapio:()=>head('Cardápio',activeSession()?`Pedidos para a sessão #${activeSession().id_sessao}`:'Inicie uma sessão antes de enviar o pedido.',button('Carrinho',"go('cliente_carrinho')"))+sessionSelector()+grid(products.map(productCard))+pager('pratos'),
  cliente_carrinho:cartView,
  cliente_pedidos:()=>head('Meus pedidos','Atualização automática a cada 10 segundos.')+orderFilters()+orderCards(pageData.pedidos)+pager('pedidos'),
  cliente_perfil:profileView,
  cozinha_dashboard:()=>dashboard(),
  cozinha_pedidos:()=>head('Pedidos','Acompanhe e avance as etapas de preparo.')+orderFilters()+orderCards(pageData.pedidos,true)+pager('pedidos'),
  cozinha_kds:()=>head('KDS','Atualização automática a cada 10 segundos.')+`<section class="kds-board">${['recebido','em_preparo','pronto'].map(status=>`<div class="kds-col"><h2>${e(labelStatus(status))}</h2>${orderCards(pageData.pedidos.filter(p=>p.status===status),true,true)}</div>`).join('')}</section>`+pager('kds','pedidos'),
  cozinha_historico:()=>head('Histórico','Pedidos concluídos e cancelados.')+orderCards(pageData.pedidos.filter(p=>['entregue','cancelado'].includes(p.status)))+pager('pedidos'),
  cozinha_estoque:()=>head('Disponibilidade do cardápio','Controle dos pratos disponíveis para venda.')+grid(pageData.pratos.map(p=>`<div class="card">${catalogImage(p.imagem,p.nome)}<h3>${e(p.nome)}</h3><p>${p.ativo?'Disponível':'Indisponível'}</p>${button('Alternar disponibilidade',`perform('/pratos/${p.id_prato}','PATCH',{ativo:${!p.ativo}},'Disponibilidade atualizada.')`)}</div>`))+pager('pratos'),
  admin_dashboard:()=>dashboard(true),
  admin_reservas:()=>head('Reservas','Gerencie reservas e inicie o atendimento.')+reservationCards()+pager('reservas')+reservationForm(true)+head('Sessões ativas','Encerre após concluir os pedidos.')+grid(pageData.sessoes.filter(s=>s.status==='ativa').map(s=>`<div class="card"><h3>Sessão #${s.id_sessao}</h3>${button('Encerrar',`perform('/sessoes/${s.id_sessao}/encerrar','POST',{},'Sessão encerrada.')`,'danger')}</div>`))+pager('sessoes'),
  admin_bancadas:()=>catalogTable('bancadas'),
  admin_produtos:()=>catalogTable('pratos')+catalogTable('fichas-tecnicas'),
  admin_ingredientes:()=>catalogTable('ingredientes')+head('Movimentações','Consumos, ajustes e estornos registrados pelo backend.')+table(['Data','Ingrediente','Tipo','Quantidade','Pedido'],(pageData.movimentacoes||[]).map(m=>[e(dates(m.criado_em)),e(ingredientName(m.id_ingrediente)),e(m.tipo),e(m.quantidade),e(m.id_pedido||'—')]))+pager('movimentacoes'),
  admin_substituicoes:()=>catalogTable('substituicoes'),
  admin_usuarios:usersView,
  admin_relatorios:reportsView
};

function reportsView(){
 const r=pageData.relatorios;
 return head('Relatórios','Resultados do período selecionado. Receitas incluem somente atendimentos concluídos.')+
 `<form class="filterbar" onsubmit="applyReportPeriod(event)"><label>De<input name="de" type="date" value="${e(reportPeriod.de?.slice(0,10)||'')}"></label><label>Até<input name="ate" type="date"></label><button class="btn secondary" type="submit">Filtrar período</button><button class="btn ghost" type="button" onclick="reportPeriod={};renderCurrentPage(activePage)">Limpar</button></form>`+
 `<section class="grid cols-3">${stat('Reservas',r.reservas)}${stat('Pedidos',r.pedidos)}${stat('Receita de pedidos',money(r.receita_pedidos))}${stat('Receita de reservas',money(r.receita_reservas))}${stat('Ticket médio',money(r.ticket_medio))}${stat('Tempo médio de preparo',r.tempo_medio_preparo==null?'Sem amostra':r.tempo_medio_preparo.toFixed(1)+' min')}</section>`+
 table(['Bancada','Reservas concluídas','Receita'],r.por_bancada.map(b=>[e(b.nome),e(b.reservas),money(b.receita)]));
}
function applyReportPeriod(event){event.preventDefault();const data=Object.fromEntries(new FormData(event.target));reportPeriod={};if(data.de)reportPeriod.de=data.de+'T00:00:00';if(data.ate){const date=new Date(data.ate+'T00:00:00');date.setDate(date.getDate()+1);reportPeriod.ate=`${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}T00:00:00`;}renderCurrentPage(activePage);}

let availableBenches=null;
function benchesView(){return head('Bancadas','Consulte a disponibilidade para o período desejado.')+`<form class="filterbar" onsubmit="checkAvailableBenches(event)"><label>Início<input name="inicio" type="datetime-local" required></label><label>Fim<input name="fim" type="datetime-local" required></label><button class="btn secondary" type="submit">Consultar disponibilidade</button></form><div id="benchResults">${benchResults(availableBenches||pageData.bancadas)}</div>`+pager('bancadas');}
function benchResults(records){return grid(records.map(b=>`<div class="card"><h3>${e(b.nome)}</h3><p>${e(b.descricao||'')}</p><p>${money(b.valor_hora)}/hora · ${b.ativa?'Ativa':'Indisponível'}</p>${b.ativa?button('Reservar',"go('cliente_reservas')"):''}</div>`));}
async function checkAvailableBenches(event){event.preventDefault();const data=Object.fromEntries(new FormData(event.target));const error=reservationPeriodError(data.inicio,data.fim);if(error){showToast(error);return;}try{const result=await api('/disponibilidade?'+new URLSearchParams(data));availableBenches=result.bancadas;el('benchResults').innerHTML=benchResults(availableBenches);}catch(error){showToast(error.message);}}
