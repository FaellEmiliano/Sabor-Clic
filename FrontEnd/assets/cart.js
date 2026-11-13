function addCart(id){
  try{const product=products.find(p=>p.id===id);if(!product)return;state.carrinho.adicionar(product);saveCart();showToast('Item adicionado ao carrinho.');}
  catch(error){showToast(error.message);}
}
function delCart(id){state.carrinho.remover(id);saveCart();renderCurrentPage('cliente_carrinho');}
function changeQuantity(id, input) {
  const quantity = input.valueAsNumber;
  if (!input.validity.valid || !Number.isInteger(quantity)) return;
  state.carrinho.alterarQuantidade(id, quantity);
  const item = state.cart.find(item => item.id === id);
  el(`cartSubtotal${id}`).textContent = money(item.subtotalCentavos / 100);
  el('cartTotal').textContent = money(cartTotal());
  saveCart();
}

function restoreCartQuantity(id, input) {
  const item = state.cart.find(item => item.id === id);
  input.value = item.qtd;
}
function cartTotal(){return state.carrinho.total;}
function cartItemCount(){return state.carrinho.quantidade;}
