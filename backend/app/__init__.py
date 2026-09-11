from flask import app
# aqui são definidas todas as configurações do app antes do run.py rodar ele.

@staticmethod
def criar_app(): # essa função é chamada no run.py, assim criando a instância do app (backend).
    inst_app = app
    return inst_app