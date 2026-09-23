// As funções de componentes ficam em components.js e as regras do carrinho em cart.js.
const views = {
cliente_inicio:()=>`
  <section class="hero">
    <div class="panel hero-main">
      <span class="badge good">Sessão ativa até 22:00</span>
      <h1>Boa noite, Rafael.</h1>
      <p>Sua reserva na Bancada Toscana está em andamento. Você pode acessar o cardápio, fazer novos pedidos e acompanhar o preparo em tempo real.</p>
      <div class="actions">
        <button class="btn" onclick="go('cliente_cardapio')">Abrir cardápio</button>
        <button class="btn secondary" onclick="go('cliente_sessao')">Ver sessão</button>
      </div>
    </div>
    <div class="panel">
      <h3 style="margin-top:0">Reserva atual</h3>
      <p><b>#RSV-1048</b></p>
      <div class="detail-row"><span class="muted">Bancada</span><b>Toscana</b></div>
      <div class="detail-row"><span class="muted">Horário</span><b>19:00–22:00</b></div>
      <div class="detail-row"><span class="muted">Pessoas</span><b>4</b></div>
      <div class="hr"></div>
      <span class="badge good">Em andamento</span>
    </div>
  </section>
  <section class="grid cols-4">
    ${stat("Pedidos na sessão","2","1 em preparo")}
    ${stat("Consumo atual",money(79.9),"sem contar aluguel")}
    ${stat("Tempo restante","1h 34min","até 22:00")}
    ${stat("Bancada","Toscana","4 lugares")}
  </section>
  <div class="section-title"><div><h2>Acesso rápido</h2><p>Principais ações do cliente.</p></div></div>
  <section class="grid cols-3">
    <div class="card role-card"><h3>Reservar outra bancada</h3><p class="meta">Consulte datas, horários e capacidade.</p><button class="btn secondary" onclick="go('cliente_bancadas')">Ver bancadas</button></div>
    <div class="card role-card"><h3>Fazer pedido</h3><p class="meta">Veja pratos, bebidas e sobremesas.</p><button class="btn secondary" onclick="go('cliente_cardapio')">Abrir cardápio</button></div>
    <div class="card role-card"><h3>Acompanhar preparo</h3><p class="meta">Veja o status dos pedidos da sessão.</p><button class="btn secondary" onclick="go('cliente_pedidos')">Meus pedidos</button></div>
  </section>
`,
cliente_bancadas:()=>`
  ${head("Bancadas","Consulte disponibilidade por data, horário e capacidade.")}
  <div class="filterbar"><input type="date" value="2026-09-12"><select><option>19:00</option><option>20:00</option></select><select><option>2 pessoas</option><option selected>4 pessoas</option><option>6 pessoas</option></select><button class="btn secondary">Aplicar filtros</button></div>
  <section class="grid cols-3">${benches.map(benchCard).join("")}</section>
`,
cliente_reservas:()=>`
  ${head("Minhas reservas","Crie, consulte e acompanhe suas reservas.",`<button class="btn" onclick="showToast('Fluxo de nova reserva simulado.')">+ Nova reserva</button>`)}
  <section class="grid cols-3">
    <div class="card"><div class="detail-row"><b>#RSV-1048</b><span class="badge good">Em andamento</span></div><h3>Bancada Toscana</h3><p class="meta">09/09/2026 • 19:00–22:00 • 4 pessoas</p><div class="actions"><button class="btn" onclick="go('cliente_sessao')">Abrir sessão</button><button class="btn secondary">Detalhes</button></div></div>
    <div class="card"><div class="detail-row"><b>#RSV-1056</b><span class="badge info">Confirmada</span></div><h3>Bancada Provence</h3><p class="meta">18/09/2026 • 20:00–23:00 • 6 pessoas</p><div class="actions"><button class="btn secondary">Alterar</button><button class="btn danger">Cancelar</button></div></div>
    <div class="card"><div class="detail-row"><b>#RSV-0991</b><span class="badge">Concluída</span></div><h3>Bancada Ipê</h3><p class="meta">22/08/2026 • 18:00–21:00 • 5 pessoas</p><div class="actions"><button class="btn secondary">Ver histórico</button></div></div>
  </section>
  <div class="section-title"><div><h2>Nova reserva — exemplo de formulário</h2></div></div>
  <section class="split">
    <div class="card"><div class="form-grid">
      <label>Data<input id="reservaData" type="date" required></label>
      <label>Horário<select id="reservaHorario" required><option>20:00–23:00</option></select></label>
      <label>Bancada<select id="reservaBancada" required><option>Provence</option><option>Toscana</option></select></label>
      <label>Pessoas<input id="reservaPessoas" type="number" min="1" max="6" step="1" value="6" required></label>
      <label>Telefone<input id="reservaTelefone" type="tel" value="(11) 99999-0000" autocomplete="tel"></label>
      <label>E-mail<input id="reservaEmail" type="email" value="cliente@exemplo.com" required></label>
    </div><label class="field" style="margin-top:14px">Observações<textarea>Comemoração de aniversário.</textarea></label></div>
    <div class="card sticky"><h3>Resumo</h3><div class="detail-row"><span>Bancada</span><b>Provence</b></div><div class="detail-row"><span>Período</span><b>3 horas</b></div><div class="detail-row"><span>Total</span><span class="price">${money(120)}</span></div><button id="confirmarReserva" type="button" class="btn good full" onclick="validateReservation()">Confirmar reserva</button></div>
  </section>
`,
cliente_sessao:()=>`
  ${head("Sessão #RSV-1048","Bancada Toscana • 19:00–22:00",`<span class="badge good">Em andamento</span>`)}
  <section class="grid cols-4">
    ${stat("Tempo restante","1h 34min","")}
    ${stat("Pedidos","2","1 em preparo")}
    ${stat("Consumo",money(79.9),"parcial")}
    ${stat("Pessoas","4","na reserva")}
  </section>
  <div class="section-title"><div><h2>Resumo da sessão</h2></div></div>
  <section class="split">
    <div class="card"><h3>Pedidos vinculados</h3><div class="list">
      <div class="list-item"><div class="detail-row"><b>#PED-209</b><span class="badge warn">Em preparo</span></div><p class="meta">Risoto de Cogumelos + 2 Sucos de Laranja</p></div>
      <div class="list-item"><div class="detail-row"><b>#PED-205</b><span class="badge good">Entregue</span></div><p class="meta">2 Bruschettas da Casa</p></div>
    </div></div>
    <div class="card sticky"><h3>Ações</h3><div class="actions"><button class="btn full" onclick="go('cliente_cardapio')">Fazer novo pedido</button><button class="btn secondary full" onclick="go('cliente_pedidos')">Acompanhar pedidos</button><button class="btn danger full" onclick="showToast('Encerramento simulado.')">Encerrar sessão</button></div></div>
  </section>
`,
cliente_cardapio:()=>`
  ${head("Cardápio","Os pedidos desta tela serão vinculados à sessão #RSV-1048.",`<button class="btn secondary" onclick="go('cliente_carrinho')">Carrinho (${state.cart.reduce((s,i)=>s+i.qtd,0)})</button>`)}
  <div class="tabs"><button class="active">Todos</button><button>Entradas</button><button>Pratos</button><button>Bebidas</button><button>Sobremesas</button></div>
  <section class="grid cols-4">${products.map(productCard).join("")}</section>
`,
cliente_carrinho:()=>`
  ${head("Carrinho","Revise os itens antes de enviar à cozinha.")}
  <section class="split">
    <div class="card"><div class="table-wrap"><table><thead><tr><th>Item</th><th>Qtd.</th><th>Preço</th><th></th></tr></thead><tbody>${state.cart.map(i=>`<tr><td>${i.nome}</td><td>${i.qtd}</td><td>${money(i.preco*i.qtd)}</td><td><button class="btn danger" onclick="delCart(${i.id})">Remover</button></td></tr>`).join("")}</tbody></table></div><label class="field" style="margin-top:14px">Observação do pedido<textarea>Sem cebola no burger.</textarea></label></div>
    <div class="card sticky"><h3>Resumo</h3><div class="detail-row"><span>Reserva</span><b>#RSV-1048</b></div><div class="detail-row"><span>Subtotal</span><b>${money(cartTotal())}</b></div><div class="hr"></div><div class="detail-row"><span>Total</span><span class="price">${money(cartTotal())}</span></div><button class="btn good full" onclick="go('cliente_pedidos')">Enviar pedido</button></div>
  </section>
`,
cliente_pedidos:()=>`
  ${head("Meus pedidos","Acompanhe todos os pedidos da sessão atual.")}
  <section class="card">
    <div class="detail-row"><div><b>#PED-209</b><p class="meta">20:14 • Bancada Toscana</p></div><span class="badge warn">Em preparo</span></div>
    <div class="timeline"><div class="on">Recebido</div><div class="on">Confirmado</div><div class="on">Em preparo</div><div>Pronto</div><div>Entregue</div></div>
    <ul><li>1× Risoto de Cogumelos</li><li>2× Suco de Laranja</li></ul>
  </section>
  <section class="card" style="margin-top:16px">
    <div class="detail-row"><div><b>#PED-205</b><p class="meta">19:42 • Bancada Toscana</p></div><span class="badge good">Entregue</span></div>
    <div class="timeline"><div class="on">Recebido</div><div class="on">Confirmado</div><div class="on">Em preparo</div><div class="on">Pronto</div><div class="on">Entregue</div></div>
    <ul><li>2× Bruschetta da Casa</li></ul>
  </section>
`,
cliente_perfil:()=>`
  ${head("Meu perfil","Dados pessoais e preferências.")}
  <section class="grid cols-2">
    <div class="card"><h3>Dados</h3><div class="form-grid"><label>Nome<input value="Rafael Gomes"></label><label>E-mail<input value="rafael@exemplo.com"></label><label>Telefone<input value="(11) 99999-0000"></label><label>Senha<input type="password" value="12345678"></label></div><button class="btn" style="margin-top:14px">Salvar alterações</button></div>
    <div class="card"><h3>Preferências</h3><div class="list"><div class="list-item">Receber confirmação de reserva por e-mail</div><div class="list-item">Receber aviso quando o pedido estiver pronto</div><div class="list-item">Salvar dados para futuras reservas</div></div></div>
  </section>
`,

cozinha_dashboard:()=>`
  ${head("Visão geral da cozinha","Resumo operacional do turno atual.")}
  <section class="grid cols-4">
    ${stat("Pedidos recebidos","18","+3 na última hora")}
    ${stat("Em preparo","5","")}
    ${stat("Prontos","2","aguardando retirada")}
    ${stat("Tempo médio","11 min","")}
  </section>
  <div class="section-title"><div><h2>Prioridades agora</h2></div></div>
  <section class="grid cols-3">
    <div class="card"><span class="badge danger">Atrasado</span><h3>#PED-201</h3><p>14 min • Bancada Provence</p><button class="btn danger" onclick="go('cozinha_kds')">Abrir no KDS</button></div>
    <div class="card"><span class="badge warn">Em preparo</span><h3>#PED-209</h3><p>8 min • Bancada Toscana</p><button class="btn secondary" onclick="go('cozinha_kds')">Abrir no KDS</button></div>
    <div class="card"><span class="badge info">Novo</span><h3>#PED-212</h3><p>1 min • Bancada Ipê</p><button class="btn secondary" onclick="go('cozinha_kds')">Abrir no KDS</button></div>
  </section>
`,
cozinha_kds:()=>`
  ${head("KDS","Pedidos organizados por etapa de preparo.",`<span class="badge good">Atualização automática</span>`)}
  <section class="kds-board">
    <div class="kds-col"><h3>Recebidos</h3>
      ${ticket("#PED-212","Ipê","1 min",["2× Bruschetta da Casa"],"Iniciar preparo","info")}
      ${ticket("#PED-213","Provence","3 min",["1× Burger Artesanal","1× Soda Italiana"],"Iniciar preparo","info")}
    </div>
    <div class="kds-col"><h3>Em preparo</h3>
      ${ticket("#PED-209","Toscana","8 min",["1× Risoto de Cogumelos","2× Suco de Laranja"],"Marcar pronto","warn")}
      ${ticket("#PED-201","Provence","14 min",["2× Burger Artesanal","1× Torta de Limão"],"Marcar pronto","danger")}
    </div>
    <div class="kds-col"><h3>Prontos</h3>
      ${ticket("#PED-206","Aurora","10 min",["1× Torta de Limão"],"Marcar entregue","good")}
    </div>
  </section>
`,
cozinha_pedidos:()=>`
  ${head("Pedidos","Consulta detalhada dos pedidos do turno.")}
  <div class="filterbar"><select><option>Todos os status</option><option>Recebidos</option><option>Em preparo</option><option>Prontos</option></select><input placeholder="Buscar pedido"><button class="btn secondary">Filtrar</button></div>
  <section class="card table-wrap"><table><thead><tr><th>Pedido</th><th>Bancada</th><th>Horário</th><th>Status</th><th>Itens</th><th>Ação</th></tr></thead><tbody>
    <tr><td>#PED-213</td><td>Provence</td><td>20:19</td><td><span class="badge info">Recebido</span></td><td>2</td><td><button class="btn secondary">Abrir</button></td></tr>
    <tr><td>#PED-209</td><td>Toscana</td><td>20:14</td><td><span class="badge warn">Em preparo</span></td><td>3</td><td><button class="btn secondary">Abrir</button></td></tr>
    <tr><td>#PED-206</td><td>Aurora</td><td>20:08</td><td><span class="badge good">Pronto</span></td><td>1</td><td><button class="btn secondary">Abrir</button></td></tr>
  </tbody></table></section>
`,
cozinha_estoque:()=>`
  ${head("Disponibilidade do cardápio","Controle rápido do que pode ou não ser vendido.")}
  <section class="grid cols-4">${products.map(p=>`<div class="card"><div class="detail-row"><div><b>${p.nome}</b><p class="meta">${p.cat}</p></div><span class="badge ${p.status==="Disponível"?"good":"danger"}">${p.status}</span></div><button class="btn secondary full" onclick="showToast('Disponibilidade alterada no protótipo.')">Alternar status</button></div>`).join("")}</section>
`,
cozinha_historico:()=>`
  ${head("Histórico","Pedidos concluídos recentemente.")}
  <section class="card table-wrap"><table><thead><tr><th>Pedido</th><th>Bancada</th><th>Início</th><th>Fim</th><th>Tempo</th></tr></thead><tbody>
    <tr><td>#PED-205</td><td>Toscana</td><td>19:42</td><td>19:53</td><td>11 min</td></tr>
    <tr><td>#PED-198</td><td>Ipê</td><td>19:31</td><td>19:44</td><td>13 min</td></tr>
    <tr><td>#PED-194</td><td>Provence</td><td>19:20</td><td>19:30</td><td>10 min</td></tr>
  </tbody></table></section>
`,

admin_dashboard:()=>`
  ${head("Dashboard","Visão geral do funcionamento do Sabor e Clic.")}
  <section class="grid cols-5">
    ${stat("Reservas hoje","12","+2 vs ontem")}
    ${stat("Bancadas ocupadas","3/6","50%")}
    ${stat("Pedidos ativos","7","")}
    ${stat("Receita do dia",money(1640),"+8%")}
    ${stat("Clientes hoje","31","")}
  </section>
  <div class="section-title"><div><h2>Operação atual</h2></div></div>
  <section class="grid cols-2">
    <div class="card"><h3>Próximas reservas</h3><div class="list">
      <div class="list-item"><div class="detail-row"><b>18:30 • Aurora</b><span class="badge info">Confirmada</span></div><span class="meta">2 pessoas • Lucas Lima</span></div>
      <div class="list-item"><div class="detail-row"><b>19:00 • Toscana</b><span class="badge good">Em andamento</span></div><span class="meta">4 pessoas • Rafael Gomes</span></div>
      <div class="list-item"><div class="detail-row"><b>20:00 • Provence</b><span class="badge info">Confirmada</span></div><span class="meta">6 pessoas • Camila Rocha</span></div>
    </div></div>
    <div class="card"><h3>Alertas</h3><div class="list">
      <div class="list-item"><span class="badge danger">Bancada</span><p>Bancada Cedro em manutenção.</p></div>
      <div class="list-item"><span class="badge warn">Produto</span><p>Nhoque ao Sugo indisponível.</p></div>
      <div class="list-item"><span class="badge warn">Estoque</span><p>Cogumelos abaixo do estoque mínimo.</p></div>
    </div></div>
  </section>
`,
admin_reservas:()=>`
  ${head("Reservas","Gerencie reservas, horários e sessões.",`<button class="btn">+ Nova reserva</button>`)}
  <div class="filterbar"><input type="date" value="2026-09-09"><select><option>Todos os status</option><option>Confirmada</option><option>Em andamento</option></select><input placeholder="Cliente ou código"><button class="btn secondary">Filtrar</button></div>
  <section class="card table-wrap"><table><thead><tr><th>Código</th><th>Cliente</th><th>Bancada</th><th>Horário</th><th>Pessoas</th><th>Status</th><th>Ações</th></tr></thead><tbody>
    <tr><td>#RSV-1048</td><td>Rafael Gomes</td><td>Toscana</td><td>19:00–22:00</td><td>4</td><td><span class="badge good">Em andamento</span></td><td><button class="btn secondary">Abrir</button></td></tr>
    <tr><td>#RSV-1050</td><td>Lucas Lima</td><td>Aurora</td><td>18:30–20:30</td><td>2</td><td><span class="badge info">Confirmada</span></td><td><button class="btn secondary">Editar</button></td></tr>
    <tr><td>#RSV-1056</td><td>Camila Rocha</td><td>Provence</td><td>20:00–23:00</td><td>6</td><td><span class="badge info">Confirmada</span></td><td><button class="btn secondary">Editar</button></td></tr>
  </tbody></table></section>
`,
admin_bancadas:()=>`
  ${head("Bancadas","Cadastro, capacidade, recursos e disponibilidade.",`<button class="btn">+ Nova bancada</button>`)}
  <section class="grid cols-3">${benches.map(b=>`<div class="card"><div class="detail-row"><h3>${b.nome}</h3><span class="badge ${b.status==="Disponível"?"good":b.status==="Ocupada"?"warn":"danger"}">${b.status}</span></div><p class="meta">${b.cap} pessoas • ${b.recursos.join(" • ")}</p><div class="detail-row"><span class="price">${money(b.preco)}</span><div class="actions"><button class="btn secondary">Editar</button><button class="btn ghost">Status</button></div></div></div>`).join("")}</section>
`,
admin_produtos:()=>`
  ${head("Produtos e pratos","Cadastre itens do cardápio e controle disponibilidade.",`<button class="btn">+ Novo produto</button>`)}
  <section class="card table-wrap"><table><thead><tr><th>Produto</th><th>Categoria</th><th>Preço</th><th>Status</th><th>Ações</th></tr></thead><tbody>${products.map(p=>`<tr><td>${p.nome}</td><td>${p.cat}</td><td>${money(p.preco)}</td><td><span class="badge ${p.status==="Disponível"?"good":"danger"}">${p.status}</span></td><td><button class="btn secondary">Editar</button></td></tr>`).join("")}</tbody></table></section>
`,
admin_ingredientes:()=>`
  ${head("Ingredientes","Controle de ingredientes usados nos pratos.",`<button class="btn">+ Novo ingrediente</button>`)}
  <section class="grid cols-3">
    ${ingredient("Cogumelos","2,1 kg","5 kg","warn")}
    ${ingredient("Arroz arbóreo","8 kg","5 kg","good")}
    ${ingredient("Tomate","12 kg","6 kg","good")}
    ${ingredient("Pão brioche","18 un","20 un","warn")}
    ${ingredient("Parmesão","4,3 kg","3 kg","good")}
    ${ingredient("Limão","9 kg","4 kg","good")}
  </section>
`,
admin_substituicoes:()=>`
  ${head("Substituições","Defina alternativas de ingredientes quando houver indisponibilidade.",`<button class="btn">+ Nova substituição</button>`)}
  <div class="note">Exemplo alinhado ao seu DER: um ingrediente pode apontar para outro ingrediente como substituto.</div>
  <section class="card table-wrap" style="margin-top:16px"><table><thead><tr><th>Ingrediente original</th><th>Substituto</th><th>Prioridade</th><th>Status</th><th>Ações</th></tr></thead><tbody>
    <tr><td>Pão brioche</td><td>Pão australiano</td><td>1</td><td><span class="badge good">Ativa</span></td><td><button class="btn secondary">Editar</button></td></tr>
    <tr><td>Muçarela</td><td>Queijo prato</td><td>1</td><td><span class="badge good">Ativa</span></td><td><button class="btn secondary">Editar</button></td></tr>
    <tr><td>Cogumelo paris</td><td>Shimeji</td><td>2</td><td><span class="badge info">Opcional</span></td><td><button class="btn secondary">Editar</button></td></tr>
  </tbody></table></section>
`,
admin_usuarios:()=>`
  ${head("Usuários","Clientes, cozinheiros e administradores.",`<button class="btn">+ Novo usuário</button>`)}
  <section class="card table-wrap"><table><thead><tr><th>Nome</th><th>Perfil</th><th>E-mail</th><th>Status</th><th>Ações</th></tr></thead><tbody>
    <tr><td>Rafael Gomes</td><td>Cliente</td><td>rafael@exemplo.com</td><td><span class="badge good">Ativo</span></td><td><button class="btn secondary">Abrir</button></td></tr>
    <tr><td>Marina Souza</td><td>Cozinheira</td><td>marina@saboreclic.com</td><td><span class="badge good">Ativo</span></td><td><button class="btn secondary">Abrir</button></td></tr>
    <tr><td>Ana Martins</td><td>Administrador</td><td>ana@saboreclic.com</td><td><span class="badge good">Ativo</span></td><td><button class="btn secondary">Abrir</button></td></tr>
  </tbody></table></section>
`,
admin_relatorios:()=>`
  ${head("Relatórios","Indicadores simples para gestão.")}
  <section class="grid cols-4">
    ${stat("Receita mensal",money(28640),"+12%")}
    ${stat("Reservas no mês","214","+18")}
    ${stat("Ticket médio",money(133.8),"+4%")}
    ${stat("Tempo médio pedido","11 min","-2 min")}
  </section>
  <div class="section-title"><div><h2>Resumo por bancada</h2></div></div>
  <section class="card table-wrap"><table><thead><tr><th>Bancada</th><th>Reservas</th><th>Ocupação</th><th>Receita</th></tr></thead><tbody>
    <tr><td>Toscana</td><td>49</td><td>82%</td><td>${money(6240)}</td></tr>
    <tr><td>Provence</td><td>38</td><td>76%</td><td>${money(5910)}</td></tr>
    <tr><td>Ipê</td><td>41</td><td>79%</td><td>${money(5480)}</td></tr>
    <tr><td>Aurora</td><td>33</td><td>68%</td><td>${money(3320)}</td></tr>
  </tbody></table></section>
`
};

function renderCurrentPage(pageId){
  el("app").innerHTML = views[pageId]();
}
