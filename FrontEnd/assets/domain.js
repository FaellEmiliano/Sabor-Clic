// Domain entities used by the UI. Money is stored in cents and quantities are validated here and again by Flask.
class Entidade {
  #id;
  constructor(id) { if(!Number.isInteger(Number(id))||Number(id)<1) throw new Error('Identificador inválido.'); this.#id=Number(id); }
  get id(){return this.#id;}
}
class Usuario extends Entidade {
  #dados;
  constructor(data){super(data.id_usuario);this.#dados=Object.freeze({...data});}
  static fromJSON(data){return new Usuario(data);}
  get id_usuario(){return this.id;}
  get nome(){return this.#dados.nome;}
  get email(){return this.#dados.email;}
  get tipo(){return this.#dados.tipo;}
  get ativo(){return this.#dados.ativo;}
  get endereco_entrega(){return this.#dados.endereco_entrega||'';}
  toJSON(){return {...this.#dados};}
}
class Prato extends Entidade {
  #nome;#centavos;#ativo;#descricao;#imagem;
  constructor(data){super(data.id_prato);this.#nome=String(data.nome);this.#centavos=Prato.centavos(data.preco);this.#ativo=!!data.ativo;this.#descricao=data.descricao||'';this.#imagem=data.imagem||null;}
  static fromJSON(data){return new Prato(data);}
  static centavos(value){const number=Number(value);if(!Number.isFinite(number)||number<0)throw new Error('Preço inválido.');return Math.round(number*100);}
  get id_prato(){return this.id;}
  get nome(){return this.#nome;}
  get preco(){return this.#centavos/100;}
  get ativo(){return this.#ativo;}
  get desc(){return this.#descricao;}
  get imagem(){return this.#imagem;}
  get cat(){return 'Cardápio';}
  get status(){return this.#ativo?'Disponível':'Indisponível';}
  toJSON(){return {id_prato:this.id,nome:this.nome,preco:this.preco,ativo:this.ativo,descricao:this.desc,imagem:this.imagem};}
}
class ItemPedido extends Entidade {
  #nome;#centavos;#quantidade;#imagem;
  constructor(prato,quantity=1){super(prato.id);this.atualizarProduto(prato);this.qtd=quantity;}
  static fromJSON(data){return new ItemPedido(new Prato({id_prato:data.id,nome:data.nome,preco:data.preco,ativo:true,imagem:data.imagem}),data.qtd);}
  get nome(){return this.#nome;}
  get imagem(){return this.#imagem;}
  get preco(){return this.#centavos/100;}
  get qtd(){return this.#quantidade;}
  set qtd(value){if(!Number.isInteger(value)||value<1||value>1000)throw new Error('A quantidade deve estar entre 1 e 1000.');this.#quantidade=value;}
  get subtotalCentavos(){return this.#centavos*this.#quantidade;}
  atualizarProduto(prato){this.#nome=prato.nome;this.#centavos=Prato.centavos(prato.preco);this.#imagem=prato.imagem||null;}
  toJSON(){return {id:this.id,nome:this.nome,preco:this.preco,qtd:this.qtd,imagem:this.imagem};}
  toPayload(){return {id_prato:this.id,quantidade:this.qtd};}
}
class Carrinho {
  #itens=new Map();
  static fromJSON(data){const cart=new Carrinho();if(!Array.isArray(data))return cart;for(const value of data){try{const item=value instanceof ItemPedido?value:ItemPedido.fromJSON(value);cart.#itens.set(item.id,item);}catch{ /* Ignore corrupt local entries; no server data is changed. */ }}return cart;}
  get itens(){return Array.from(this.#itens.values());}
  get quantidade(){return this.itens.reduce((sum,i)=>sum+i.qtd,0);}
  get total(){return this.itens.reduce((sum,i)=>sum+i.subtotalCentavos,0)/100;}
  adicionar(prato,quantity=1){if(!prato.ativo)throw new Error('Prato indisponível.');const item=this.#itens.get(prato.id);if(item)item.qtd+=quantity;else this.#itens.set(prato.id,new ItemPedido(prato,quantity));}
  remover(id){this.#itens.delete(id);}
  alterarQuantidade(id,quantity){const item=this.#itens.get(id);if(!item)throw new Error('Item não encontrado.');item.qtd=quantity;}
  atualizarCatalogo(pratos){for(const item of this.itens){const prato=pratos.find(p=>p.id===item.id);if(prato)item.atualizarProduto(prato);}}
  limpar(){this.#itens.clear();}
  toJSON(){return this.itens.map(i=>i.toJSON());}
}
class Pedido {
  #sessao;#itens;#endereco;#observacoes;#chave;
  constructor(session,cart,details={},key=Pedido.novaChave()){
    if(!Number.isInteger(session)||session<1||!cart.itens.length)throw new Error('O pedido precisa de sessão e itens.');
    this.#sessao=session;this.#itens=cart.itens.map(i=>i.toPayload());this.#endereco=details.endereco_entrega||null;this.#observacoes=details.observacoes||null;this.#chave=key;
  }
  static novaChave(){return typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID():Date.now().toString(36)+'_'+Math.random().toString(36).slice(2)+'_'+Math.random().toString(36).slice(2);}
  get chave(){return this.#chave;}
  toPayload(){return {id_sessao:this.#sessao,itens:this.#itens.map(i=>({...i})),endereco_entrega:this.#endereco,observacoes:this.#observacoes};}
  get assinatura(){return JSON.stringify(this.toPayload());}
}
if(typeof module!=='undefined')module.exports={Entidade,Usuario,Prato,ItemPedido,Carrinho,Pedido};
