// Cardápio dinâmico — 3º bimestre
// Demonstra arrays, objetos, forEach e manipulação direta do DOM.

function renderCatalog(category = "Todos") {
  const grid = document.querySelector(".grid.cols-4");
  if (!grid) return;

  grid.innerHTML = "";

  products.forEach(product => {
    if (category !== "Todos" && product.cat !== category) return;

    const wrapper = document.createElement("div");
    wrapper.innerHTML = productCard(product).trim();
    grid.appendChild(wrapper.firstElementChild);
  });
}

function initCatalogFilters() {
  if (!window.location.pathname.endsWith("cliente_cardapio.html")) return;

  const buttons = document.querySelectorAll(".tabs button");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      buttons.forEach(item => item.classList.remove("active"));
      button.classList.add("active");
      renderCatalog(button.textContent.trim());
    });
  });

  renderCatalog();
}

document.addEventListener("DOMContentLoaded", initCatalogFilters);
