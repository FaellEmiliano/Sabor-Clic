async function obterCliente(id) {
  try {
    const resposta = await fetch(`http://127.0.0.1:5000/api/clientes/${id}`);
    const dados_cliente = await resposta.json();
    console.log('GET dados:', dados_cliente);
  } catch (erro) {
    console.error('ERRO na requisição GET:', erro);
  }
}

async function enviarCliente(nome, email, senha) {
  try {
    const resposta = await fetch('http://127.0.0.1:5000/api/clientes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ nome: nome, email: email, senha: senha, ativo: true})});
    
        if (resposta.status === 201) {
            const clienteCriado = await resposta.json();
            console.log('Cliente cadastrado com sucesso:', clienteCriado);
        }
    } catch (erro) {
        console.error('Erro na requisição POST:', erro);
    }
}

enviarCliente('Rafael', 'rafazinholindofufuxo@gmail.com', '#Brigadeiro11')