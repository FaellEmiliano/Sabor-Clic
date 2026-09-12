from datetime import datetime

from app.models.bancada_model import BancadaModel
from app.models.reserva_model import ReservaModel
from app.models.usuario_model import UsuarioModel


def listar_bancadas():
    return {"bancadas": BancadaModel.listar()}, 200


def obter_reserva(id_reserva):
    reserva = ReservaModel.obter(id_reserva)
    if not reserva:
        return {"erro": "Reserva não encontrada."}, 404
    return {"reserva": reserva}, 200


def criar_reserva(dados):
    campos = ("id_cliente", "id_bancada", "inicio", "fim", "pessoas")
    ausentes = [campo for campo in campos if dados.get(campo) in (None, "")]
    if ausentes:
        return {"erro": "Campos obrigatórios ausentes.", "campos": ausentes}, 400

    try:
        id_cliente = int(dados["id_cliente"])
        id_bancada = int(dados["id_bancada"])
        pessoas = int(dados["pessoas"])
        inicio = datetime.fromisoformat(str(dados["inicio"]))
        fim = datetime.fromisoformat(str(dados["fim"]))
    except (TypeError, ValueError):
        return {"erro": "IDs, quantidade de pessoas ou datas possuem formato inválido."}, 400

    cliente = UsuarioModel.obter(id_cliente)
    bancada = BancadaModel.obter(id_bancada)
    if not cliente or cliente["perfil"] != "cliente":
        return {"erro": "Cliente não encontrado."}, 404
    if not bancada:
        return {"erro": "Bancada não encontrada."}, 404
    if bancada["status"] != "disponivel":
        return {"erro": "Bancada indisponível."}, 409
    if pessoas <= 0 or pessoas > bancada["capacidade"]:
        return {"erro": "Quantidade de pessoas incompatível com a bancada."}, 400
    if fim <= inicio:
        return {"erro": "O fim da reserva deve ser posterior ao início."}, 400

    for reserva in ReservaModel.listar():
        if reserva["id_bancada"] != id_bancada or reserva["status"] in {"cancelada", "concluida"}:
            continue
        inicio_existente = datetime.fromisoformat(reserva["inicio"])
        fim_existente = datetime.fromisoformat(reserva["fim"])
        if inicio < fim_existente and fim > inicio_existente:
            return {"erro": "Já existe uma reserva para a bancada neste período."}, 409

    reserva = ReservaModel.criar(
        {
            "id_cliente": id_cliente,
            "id_bancada": id_bancada,
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            "pessoas": pessoas,
            "valor": bancada["preco"],
            "status": "confirmada",
        }
    )
    return {"mensagem": "Reserva criada em memória.", "reserva": reserva}, 201
