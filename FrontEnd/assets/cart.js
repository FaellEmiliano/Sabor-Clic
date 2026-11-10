function addCart(id){
  try{const product=products.find(p=>p.id===id);if(!product)return;state.carrinho.adicionar(product);saveCart();showToast('Item adicionado ao carrinho.');}
  catch(error){showToast(error.message);}
}
function delCart(id){state.carrinho.remover(id);saveCart();renderCurrentPage('cliente_carrinho');}
function changeQuantity(id,value){try{state.carrinho.alterarQuantidade(id,Number(value));saveCart();renderCurrentPage('cliente_carrinho');}catch(error){showToast(error.message);}}
function cartTotal(){return state.carrinho.total;}
function cartItemCount(){return state.carrinho.quantidade;}
