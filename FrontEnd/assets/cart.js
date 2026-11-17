// Adiciona o prato selecionado ao carrinho e salva o resultado. Exibe na tela um aviso de
// sucesso ou a mensagem do erro.
function addCart(id){
  try{const product=products.find(p=>p.id===id);if(!product)return;state.carrinho.adicionar(product);saveCart();showToast('Item adicionado ao carrinho.');}
  catch(error){showToast(error.message);}
}
// Remove o prato pelo número, salva o carrinho e redesenha sua página.
function delCart(id){state.carrinho.remover(id);saveCart();renderCurrentPage('cliente_carrinho');}
// Aplica a quantidade digitada se o campo aceitar o valor e ele for inteiro.
// Depois atualiza o subtotal, o total e os dados salvos no navegador.
function changeQuantity(id, input) {
  const quantity = input.valueAsNumber;
  if (!input.validity.valid || !Number.isInteger(quantity)) return;
  state.carrinho.alterarQuantidade(id, quantity);
  const item = state.cart.find(item => item.id === id);
  el(`cartSubtotal${id}`).textContent = money(item.subtotalCentavos / 100);
  el('cartTotal').textContent = money(cartTotal());
  saveCart();
}

// Volta a exibir no campo a quantidade registrada para aquele prato.
function restoreCartQuantity(id, input) {
  const item = state.cart.find(item => item.id === id);
  input.value = item.qtd;
}
// Devolve o valor total do carrinho em reais.
function cartTotal(){return state.carrinho.total;}
// Devolve a soma das unidades de todos os pratos.
function cartItemCount(){return state.carrinho.quantidade;}
