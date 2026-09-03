from app import create_app, db
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from app.model.cliente import modeloCliente
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app() # pega uma instância do flask da função create_app
CORS(app)
api = Api(app) # cria a instância da api, linkando ela com a instância do app (flask).
cliente_args = reqparse.RequestParser()
cliente_args.add_argument('nome', type=str, required=True, help='Nome não pode ficar vazio.')
cliente_args.add_argument('email', type=str, required=True, help='Email não pode ficar vazio.')
cliente_args.add_argument('senha', type=str, required=True, help='Senha não pode estar vazia')
cliente_args.add_argument('ativo', type=bool)

clienteFields = {
    'id_cliente':fields.Integer,
    'nome':fields.String,
    'email':fields.String,
    'senha_hash':fields.String,
    'ativo':fields.Boolean
}

class Clientes(Resource): # cria um 'resource' na api. Basicamente é um lugar onde as informações de todos os clientes ficam.
    @marshal_with(clienteFields)
    def get(self): # pega todos os dados de todos os clientes
        cliente = modeloCliente.query.all()
        return cliente # retorna o json criado criado com a listinha de clientes
    @marshal_with(clienteFields)
    def post(self): # cria um novo cliente, com os dados fornecidos pelo front (nesse caso o scriptzin js q eu fiz ne).
        args = cliente_args.parse_args()
        senha_com_hash_e_salt = generate_password_hash(args['senha'])
        cliente = modeloCliente(nome=args['nome'], _email=args['email'], senha_hash=senha_com_hash_e_salt, ativo=args['ativo'])
        db.session.add(cliente)
        db.session.commit()
        return cliente, 201 # retorna o cliente criado, e o código 201, que sinaliza que o recurso foi criado para o servidor.

class Cliente(Resource): # mesma coisa do de cima, mas agora é usado especificamente para >um< cliente apenas.
    @marshal_with(clienteFields)
    def get(self, id):
        cliente = modeloCliente.query.filter_by(id_cliente=id).first()
        if not cliente:
            abort(404)
        return cliente

# atribuindo os caminhos dos resources:
api.add_resource(Clientes, '/api/clientes/')
api.add_resource(Cliente, '/api/clientes/<int:id>')

@app.route('/') # so pra ter so ne
def index():
    return '<h1>API</h1>'
