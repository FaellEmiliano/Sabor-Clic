// Domain entities used by the UI. Money is stored in cents and quantities are validated here and again by Flask.
// Base compartilhada pelos objetos da interface que possuem um número de identificação.
class Entidade {
  #id;
  // Valida se a identificação representa um inteiro positivo e guarda esse número.
  constructor(id) { if(!Number.isInteger(Number(id))||Number(id)<1) throw new Error('Identificador inválido.'); this.#id=Number(id); }
  // Expõe o número que identifica o objeto.
  get id(){return this.#id;}
}
// Representa a conta que a interface recebeu do servidor.
class Usuario extends Entidade {
  #dados;
  // Usa o número da conta como identificação e guarda uma cópia dos dados que não pode ser
  // alterada diretamente.
  constructor(data){super(data.id_usuario);this.#dados=Object.freeze({...data});}
  // Cria uma conta a partir dos campos devolvidos pelo servidor.
  static fromJSON(data){return new Usuario(data);}
  // Expõe o mesmo número com o nome de campo usado na API.
  get id_usuario(){return this.id;}
  // Devolve o nome cadastrado.
  get nome(){return this.#dados.nome;}
  // Devolve o e-mail cadastrado.
  get email(){return this.#dados.email;}
  // Devolve o perfil da conta.
  get tipo(){return this.#dados.tipo;}
  // Indica se a conta está ativa.
  get ativo(){return this.#dados.ativo;}
  // Devolve o endereço cadastrado ou um texto vazio.
  get endereco_entrega(){return this.#dados.endereco_entrega||'';}
  // Devolve uma cópia dos campos da conta.
  toJSON(){return {...this.#dados};}
}
// Representa um produto do cardápio, com o preço guardado em centavos.
class Prato extends Entidade {
  #nome;#centavos;#ativo;#descricao;#imagem;
  // Copia identificação, nome, preço, disponibilidade, descrição e foto. Usa valores vazios
  // quando descrição ou foto faltam.
  constructor(data){super(data.id_prato);this.#nome=String(data.nome);this.#centavos=Prato.centavos(data.preco);this.#ativo=!!data.ativo;this.#descricao=data.descricao||'';this.#imagem=data.imagem||null;}
  // Cria um produto da interface a partir dos dados do servidor.
  static fromJSON(data){return new Prato(data);}
  // Confere se o preço é um número finito e não negativo e arredonda para o centavo mais
  // próximo.
  static centavos(value){const number=Number(value);if(!Number.isFinite(number)||number<0)throw new Error('Preço inválido.');return Math.round(number*100);}
  // Expõe o número do prato com o nome de campo usado na API.
  get id_prato(){return this.id;}
  // Devolve o nome do prato.
  get nome(){return this.#nome;}
  // Converte os centavos guardados em um valor em reais para exibição.
  get preco(){return this.#centavos/100;}
  // Informa se o prato está disponível para venda.
  get ativo(){return this.#ativo;}
  // Devolve a descrição usada no cartão.
  get desc(){return this.#descricao;}
  // Devolve o caminho da foto ou nulo se estiver sem foto.
  get imagem(){return this.#imagem;}
  // Identifica a categoria usada na exibição dos pratos.
  get cat(){return 'Cardápio';}
  // Traduz a disponibilidade para um rótulo que pode ser mostrado na tela.
  get status(){return this.#ativo?'Disponível':'Indisponível';}
  // Devolve os dados do prato com os nomes de campo da API e o preço em reais.
  toJSON(){return {id_prato:this.id,nome:this.nome,preco:this.preco,ativo:this.ativo,descricao:this.desc,imagem:this.imagem};}
}
// Representa um prato e sua quantidade dentro do carrinho.
class ItemPedido extends Entidade {
  #nome;#centavos;#quantidade;#imagem;
  // Usa a identificação do prato, copia seus dados de exibição e valida a quantidade
  // inicial.
  constructor(prato,quantity=1){super(prato.id);this.atualizarProduto(prato);this.qtd=quantity;}
  // Reconstrói um item do carrinho a partir dos dados que o navegador salvou.
  static fromJSON(data){return new ItemPedido(new Prato({id_prato:data.id,nome:data.nome,preco:data.preco,ativo:true,imagem:data.imagem}),data.qtd);}
  // Devolve o nome do prato registrado no item.
  get nome(){return this.#nome;}
  // Devolve a foto registrada no item.
  get imagem(){return this.#imagem;}
  // Devolve o preço de uma unidade em reais.
  get preco(){return this.#centavos/100;}
  // Devolve a quantidade de unidades.
  get qtd(){return this.#quantidade;}
  // Aceita uma nova quantidade inteira entre 1 e 1000. Fora desse intervalo, gera um erro.
  set qtd(value){if(!Number.isInteger(value)||value<1||value>1000)throw new Error('A quantidade deve estar entre 1 e 1000.');this.#quantidade=value;}
  // Multiplica os centavos de uma unidade pela quantidade.
  get subtotalCentavos(){return this.#centavos*this.#quantidade;}
  // Atualiza nome, preço e foto com os dados atuais do cardápio.
  atualizarProduto(prato){this.#nome=prato.nome;this.#centavos=Prato.centavos(prato.preco);this.#imagem=prato.imagem||null;}
  // Prepara os dados do item para guardar o carrinho no navegador.
  toJSON(){return {id:this.id,nome:this.nome,preco:this.preco,qtd:this.qtd,imagem:this.imagem};}
  // Prepara apenas a identificação e a quantidade para o servidor calcular o preço.
  toPayload(){return {id_prato:this.id,quantidade:this.qtd};}
}
// Guarda os itens pelo número do prato para evitar linhas repetidas.
class Carrinho {
  #itens=new Map();
  // Reconstrói um carrinho com as entradas válidas salvas no navegador. Ignora entradas que
  // não consegue ler.
  static fromJSON(data){const cart=new Carrinho();if(!Array.isArray(data))return cart;for(const value of data){try{const item=value instanceof ItemPedido?value:ItemPedido.fromJSON(value);cart.#itens.set(item.id,item);}catch{ /* Ignore corrupt local entries; no server data is changed. */ }}return cart;}
  // Devolve a lista de pratos incluídos no carrinho.
  get itens(){return Array.from(this.#itens.values());}
  // Soma as unidades de todos os itens.
  get quantidade(){return this.itens.reduce((sum,i)=>sum+i.qtd,0);}
  // Soma os subtotais em centavos e devolve o total em reais.
  get total(){return this.itens.reduce((sum,i)=>sum+i.subtotalCentavos,0)/100;}
  // Recusa pratos indisponíveis. Soma à quantidade de um prato já presente ou cria uma nova
  // linha.
  adicionar(prato,quantity=1){if(!prato.ativo)throw new Error('Prato indisponível.');const item=this.#itens.get(prato.id);if(item)item.qtd+=quantity;else this.#itens.set(prato.id,new ItemPedido(prato,quantity));}
  // Retira do carrinho o prato com o número indicado.
  remover(id){this.#itens.delete(id);}
  // Localiza o item e passa a nova quantidade para a validação.
  alterarQuantidade(id,quantity){const item=this.#itens.get(id);if(!item)throw new Error('Item não encontrado.');item.qtd=quantity;}
  // Atualiza os dados dos itens cujos pratos aparecem no cardápio recebido.
  atualizarCatalogo(pratos){for(const item of this.itens){const prato=pratos.find(p=>p.id===item.id);if(prato)item.atualizarProduto(prato);}}
  // Remove todos os itens após a confirmação do pedido.
  limpar(){this.#itens.clear();}
  // Prepara cada item para guardar o carrinho no navegador.
  toJSON(){return this.itens.map(i=>i.toJSON());}
}
// Prepara o conteúdo que o navegador vai enviar na confirmação do carrinho.
class Pedido {
  #sessao;#itens;#endereco;#observacoes;#chave;
  // Exige um número de sessão válido e pelo menos um item. Guarda uma cópia dos itens, os
  // dados de entrega e a chave de reenvio.
  constructor(session,cart,details={},key=Pedido.novaChave()){
    if(!Number.isInteger(session)||session<1||!cart.itens.length)throw new Error('O pedido precisa de sessão e itens.');
    this.#sessao=session;this.#itens=cart.itens.map(i=>i.toPayload());this.#endereco=details.endereco_entrega||null;this.#observacoes=details.observacoes||null;this.#chave=key;
  }
  // Gera uma identificação para a tentativa, usando um UUID do navegador quando disponível.
  static novaChave(){return typeof crypto!=='undefined'&&crypto.randomUUID?crypto.randomUUID():Date.now().toString(36)+'_'+Math.random().toString(36).slice(2)+'_'+Math.random().toString(36).slice(2);}
  // Devolve a chave enviada ao servidor para evitar pedidos duplicados.
  get chave(){return this.#chave;}
  // Devolve sessão, cópias dos itens, endereço e observações no formato que o servidor
  // recebe.
  toPayload(){return {id_sessao:this.#sessao,itens:this.#itens.map(i=>({...i})),endereco_entrega:this.#endereco,observacoes:this.#observacoes};}
  // Converte o conteúdo em texto para verificar se outra tentativa tem exatamente os mesmos
  // dados.
  get assinatura(){return JSON.stringify(this.toPayload());}
}
if(typeof module!=='undefined')module.exports={Entidade,Usuario,Prato,ItemPedido,Carrinho,Pedido};
