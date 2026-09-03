from app import db # pega a instância do banco do pacote app.
from sqlalchemy.ext.hybrid import hybrid_property
from utils.crypt import criptografar, descriptografar
class modeloCliente(db.Model): # modela a tabela do cliente
    __tablename__ = 'clientes' # define o nome da tabela dentro do banco de dados.

    # definindo as colunas da tabela:
    id_cliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    _email = db.Column('email', db.String(256), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    @hybrid_property
    def email(self): # Getter do email: ele é chamado ao invés do _email quando cliente.email é lido
        if self._email:
            return descriptografar(self._email)
        return None

    @email.setter
    def _email_setter(self, value: str | None) -> None: # Setter do email: Quando um valor em texto puro for inserido, essa função criptografa ele automaticamente.
        if value:
            self._email = criptografar(value)
        else:
            self._email = None

    def __init__(self, nome, _email,  senha_hash, ativo): # isso aqui é so pro pylance parar de chorar mesmokkk
        self.nome = nome
        self._email = _email # Ele já chama o setter já
        self.senha_hash = senha_hash
        self.ativo = ativo
    def __repr__(self):
        return f'Cliente(nome = {self.nome}, email = {self.email}, ativo = {self.ativo})'