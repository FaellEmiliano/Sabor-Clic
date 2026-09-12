// Lógica do carrinho — 3º bimestre
// Mantém os cálculos em memória e usa os dados simulados de data.js.

function addCart(id) {
  const product = products.find(item => item.id === id);
  if (!product || product.status !== "Disponível") return;

  const existingItem = state.cart.find(item => item.id === id);

  if (existingItem) {
    existingItem.qtd++;
  } else {
    state.cart.push({
      id: product.id,
      nome: product.nome,
      preco: product.preco,
      qtd: 1
    });
  }

  saveCart();
  showToast("Item adicionado ao carrinho.");
}

function delCart(id) {
  state.cart = state.cart.filter(item => item.id !== id);
  saveCart();
  renderCurrentPage("cliente_carrinho");
}

function cartTotal() {
  return state.cart.reduce((total, item) => total + item.preco * item.qtd, 0);
}

function cartItemCount() {
  let total = 0;

  state.cart.forEach(item => {
    total += item.qtd;
  });

  return total;
}
