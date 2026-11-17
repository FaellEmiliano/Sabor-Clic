from flask_sqlalchemy import SQLAlchemy

# Cria a instância da database.
# Conexão compartilhada pelos modelos e pelas funções que consultam ou gravam no banco.
db = SQLAlchemy()