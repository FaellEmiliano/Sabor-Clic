from app.models.reserva_model import ReservaModel
from app.models.sessao_model import SessaoModel


def obter_sessao(id_sessao):
    sessao = SessaoModel.obter(id_sessao)
    if not sessao:
        return {"erro": "Sessão não encontrada."}, 404
    return {"sessao": sessao}, 200


def criar_sessao(dados):
    try:
        id_reserva = int(dados.get("id_reserva"))
    except (TypeError, ValueError):
        return {"erro": "Informe um id_reserva válido."}, 400

    reserva = ReservaModel.obter(id_reserva)
    if not reserva:
        return {"erro": "Reserva não encontrada."}, 404
    if reserva["status"] not in {"confirmada", "em_andamento"}:
        return {"erro": "A reserva não pode iniciar uma sessão."}, 409
    if SessaoModel.obter_por_reserva(id_reserva):
        return {"erro": "A reserva já possui uma sessão."}, 409

    sessao = SessaoModel.criar(id_reserva)
    ReservaModel.atualizar_status(id_reserva, "em_andamento")
    return {"mensagem": "Sessão criada e ativada em memória.", "sessao": sessao}, 201


def encerrar_sessao(id_sessao):
    sessao = SessaoModel.obter(id_sessao)
    if not sessao:
        return {"erro": "Sessão não encontrada."}, 404
    if sessao["status"] == "encerrada":
        return {"erro": "A sessão já está encerrada."}, 409

    sessao = SessaoModel.encerrar(id_sessao)
    ReservaModel.atualizar_status(sessao["id_reserva"], "concluida")
    return {"mensagem": "Sessão encerrada em memória.", "sessao": sessao}, 200
