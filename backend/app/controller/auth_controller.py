# Aqui ficam os endpoints de autentificação do site.

# .../api/cadastro - metodo POST
def cadastrar_cliente(dados):
    if dados:
        return True, 200 # Cada endpoint passa uma mensagem (devolvida em json normalmente), e um código do protocolo HTTP, sinalizando o que aconteceu na resposta da request
    return False, 401

# outros exemplos de endpoint:

# .../api/cadastro/<int:id> - metodo GET
def get_cadastro(id): # pega o usuario pelo id. Se o id não for um inteiro, o flask automáticamente já retorna o código 404 de página não encontrada no navegador.
    usuario = Usuario_model.get_usuario(id)
    return usuario, 200

#.../api/login - metodo POST
def login(dados): # Usuario insere os dados do login no formulário, que o javascript então passa pro endpoint do login. Esse endpoint verifica se o login existe ou não, e retorna a respota de acordo.
    login = Usuario_model.get_login(dados['email'], dados['senha'])
    return True, 200



class Usuario_model:
    @staticmethod
    def get_usuario(id):
        pass
    @staticmethod
    def get_login(email, senha):
        pass
    @staticmethod
    def get_bancadas():
        pass

