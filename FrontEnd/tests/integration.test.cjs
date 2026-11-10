// Run the production frontend JavaScript against tests.serve_fixture on localhost:5051.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

test('frontend → HTTP API → database → rendered views, for all roles',async()=>{
  let cookie='';
  const store=new Map();
  const elements=new Map();
  const element=id=>{
    if(!elements.has(id)) elements.set(id,{innerHTML:'',textContent:'',value:'',classList:{add(){},remove(){}},setAttribute(){}});
    return elements.get(id);
  };
  const context=vm.createContext({console,Date,FormData,Number,JSON,Promise,URLSearchParams,
    document:{hidden:true,getElementById:element,addEventListener(){}},
    window:{location:{href:'',pathname:''}},
    localStorage:{getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)},
    setTimeout:()=>1,clearTimeout(){},
    fetch:async(url,options={})=>{
      const response=await fetch((process.env.SABOR_QA_URL||'http://127.0.0.1:5051')+url,{...options,headers:{...options.headers,...(cookie?{Cookie:cookie}:{})}});
      for(const value of response.headers.getSetCookie()) cookie=value.split(';')[0];
      return response;
    }
  });
  for(const file of ['domain','data','api','site','components','validation','cart','views'])
    vm.runInContext(fs.readFileSync(path.join(__dirname,'../assets/'+file+'.js'),'utf8'),context,{filename:file+'.js'});
  const run=code=>vm.runInContext(code,context);
  await run("api('/login',{method:'POST',body:{email:'cliente@teste.com',senha:'Teste1234'}})");
  for(const page of ['inicio','bancadas','reservas','sessao','cardapio','carrinho','pedidos','perfil']) {
    await run(`bootPage('cliente','cliente_${page}')`);
    assert.match(element('app').innerHTML,/<h[12]/,page+': '+element('app').innerHTML+' '+element('app').textContent);
  }
  run('addCart(1)');
  await run("bootPage('cliente','cliente_carrinho')");
  await run('submitOrder({disabled:false})');
  assert.equal(context.window.location.href,'cliente_pedidos.html');
  let data=await run("api('/pedidos')");
  assert.equal(data.pedidos.at(0).valor_total,12.35);
  const id=data.pedidos.at(0).id_pedido;
  await run("api('/logout',{method:'POST',body:{}})");
  await run("api('/login',{method:'POST',body:{email:'chef@teste.com',senha:'Teste1234'}})");
  for(const page of ['dashboard','kds','pedidos','estoque','historico']) {
    await run(`bootPage('cozinha','cozinha_${page}')`);
    assert.match(element('app').innerHTML,/<h[12]/,page+': '+element('app').innerHTML+' '+element('app').textContent);
  }
  for(const status of ['em_preparo','pronto','entregue'])
    await run(`perform('/pedidos/${id}','PATCH',{status:'${status}'})`);
  data=await run(`api('/pedidos/${id}')`);
  assert.equal(data.pedido.status,'entregue');
  await run("api('/logout',{method:'POST',body:{}})");
  await run("api('/login',{method:'POST',body:{email:'admin@teste.com',senha:'Teste1234'}})");
  for(const page of ['dashboard','reservas','bancadas','produtos','ingredientes','substituicoes','usuarios','relatorios']) {
    await run(`bootPage('admin','admin_${page}')`);
    assert.match(element('app').innerHTML,/<h[12]/,page+': '+element('app').innerHTML+' '+element('app').textContent);
  }
  await run(`api('/pratos',{method:'POST',body:{nome:'<img src=x onerror=alert(1)>',preco:10}})`);
  await run("bootPage('admin','admin_produtos')");
  assert.match(element('app').innerHTML,/&lt;img/);
  assert.doesNotMatch(element('app').innerHTML,/<img src=x/);
  // Regression: later pages and linked reservations remain reachable after >50 rows.
  const users=await run("api('/usuarios')");
  const customer=users.usuarios.find(u=>u.tipo==='cliente').id_usuario;
  for(let index=0;index<51;index++){
    await run(`api('/pratos',{method:'POST',body:{nome:'Prato QA pagina ${index}',preco:1}})`);
    await run(`api('/ingredientes',{method:'POST',body:{nome:'Ingrediente QA pagina ${index}',unidade_medida:'kg',quantidade_estoque:0}})`);
    const start=new Date(Date.UTC(2027,0,index+1,12));const end=new Date(start.getTime()+3600000);
    await run(`api('/reservas',{method:'POST',body:${JSON.stringify({id_cliente:customer,id_bancada:1,inicio:start.toISOString(),fim:end.toISOString()})}})`);
  }
  const lookup=await run("fetchReferenceOptions('ingredientes')");
  assert.ok(lookup.some(i=>i.nome==='Ingrediente QA pagina 50'));
  await run("api('/ingredientes/1',{method:'PATCH',body:{quantidade_estoque:100}})");
  await run("api('/logout',{method:'POST',body:{}})");
  await run("api('/login',{method:'POST',body:{email:'cliente@teste.com',senha:'Teste1234'}})");
  await run("bootPage('cliente','cliente_inicio')");
  assert.match(element('app').innerHTML,/Sessão #1/);
  await run("bootPage('cliente','cliente_cardapio')");
  assert.match(element('app').innerHTML,/Próxima/);
  await run("resourcePages.pratos=2; renderCurrentPage('cliente_cardapio')");
  assert.match(element('app').innerHTML,/Prato QA pagina 50/);
  let newest;
  for(let index=0;index<51;index++){
    newest=await run("api('/pedidos',{method:'POST',headers:{'Idempotency-Key':Pedido.novaChave()},body:{id_sessao:1,itens:[{id_prato:1,quantidade:1}]}})");
  }
  await run("bootPage('cliente','cliente_sessao')");
  const summary=await run("api('/sessoes/1')");
  assert.equal(summary.resumo.pedidos,52);
  assert.equal(summary.resumo.consumo,642.2);
  await run("api('/logout',{method:'POST',body:{}})");
  await run("api('/login',{method:'POST',body:{email:'chef@teste.com',senha:'Teste1234'}})");
  await run("bootPage('cozinha','cozinha_kds')");
  assert.match(element('app').innerHTML,/Próxima/);
  await run("resourcePages.kds=2;renderCurrentPage('cozinha_kds')");
  assert.ok(element('app').innerHTML.includes('Pedido #'+newest.pedido.id_pedido));

});
