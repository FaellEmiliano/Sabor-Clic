const {test}=require('node:test');const assert=require('node:assert/strict');
const {Entidade,Usuario,Prato,ItemPedido,Carrinho,Pedido}=require('../assets/domain.js');
const dish=(id,preco)=>Prato.fromJSON({id_prato:id,nome:'Prato '+id,preco,ativo:true});
test('classes de domínio mantêm herança e estado privado',()=>{
 const user=Usuario.fromJSON({id_usuario:1,nome:'Cliente',email:'c@teste.com',tipo:'cliente'});
 assert.ok(user instanceof Entidade);assert.equal(user.nome,'Cliente');assert.deepEqual(Object.keys(user),[]);
});
test('carrinho calcula centavos e controla quantidades',()=>{
 const cart=new Carrinho();cart.adicionar(dish(1,.1));cart.adicionar(dish(2,.2));assert.equal(cart.total,.3);
 cart.alterarQuantidade(1,2);assert.equal(cart.total,.4);assert.throws(()=>cart.alterarQuantidade(1,0));
 cart.remover(2);assert.equal(cart.quantidade,2);
});
test('estado persistido recupera itens válidos e ignora dados corrompidos',()=>{
 const cart=new Carrinho();cart.adicionar(dish(1,12.35),2);
 const restored=Carrinho.fromJSON(JSON.parse(JSON.stringify(cart)));assert.equal(restored.total,24.7);
 assert.equal(Carrinho.fromJSON([null,{id:1,qtd:-1,preco:1}]).quantidade,0);
});
test('pedido serializa somente dados operacionais, com chave de reenvio',()=>{
 const cart=new Carrinho();cart.adicionar(dish(1,12.35),2);const order=new Pedido(3,cart,{},'chave-1234567890123456');
 assert.deepEqual(order.toPayload().itens,[{id_prato:1,quantidade:2}]);assert.equal(order.chave,'chave-1234567890123456');
 assert.throws(()=>new Pedido(1,new Carrinho()));
});
