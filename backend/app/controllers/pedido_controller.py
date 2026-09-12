from app.models.bancada_model import BancadaModel
from app.models.pedido_model import PedidoModel
from app.models.prato_model import PratoModel
from app.models.reserva_model import ReservaModel
from app.models.sessao_model import SessaoModel


def listar_cardapio():
    return {"pratos": PratoModel.listar()}, 200


def obter_pedido(id_pedido):
    pedido = PedidoModel.obter(id_pedido)
    if not pedido:
        return {"erro": "Pedido não encontrado."}, 404
    return {"pedido": pedido}, 200


def criar_pedido(dados):
    try:
        id_sessao = int(dados.get("id_sessao"))
    except (TypeError, ValueError):
        return {"erro": "Informe um id_sessao válido."}, 400

    sessao = SessaoModel.obter(id_sessao)
    if not sessao:
        return {"erro": "Sessão não encontrada."}, 404
    if sessao["status"] != "ativa":
        return {"erro": "Somente uma sessão ativa pode receber pedidos."}, 409

    itens_recebidos = dados.get("itens")
    if not isinstance(itens_recebidos, list) or not itens_recebidos:
        return {"erro": "O pedido deve possuir ao menos um item."}, 400

    itens = []
    valor_total = 0.0
    for item in itens_recebidos:
        try:
            id_prato = int(item.get("id_prato"))
            quantidade = int(item.get("quantidade"))
        except (AttributeError, TypeError, ValueError):
            return {"erro": "Cada item deve informar id_prato e quantidade válidos."}, 400

        prato = PratoModel.obter(id_prato)
        if not prato:
            return {"erro": f"Prato {id_prato} não encontrado."}, 404
        if not prato["disponivel"]:
            return {"erro": f"O prato {prato['nome']} está indisponível."}, 409
        if quantidade <= 0:
            return {"erro": "A quantidade de cada item deve ser positiva."}, 400

        subtotal = round(prato["preco"] * quantidade, 2)
        itens.append(
            {
                "id_prato": prato["id"],
                "nome": prato["nome"],
                "quantidade": quantidade,
                "preco_unitario": prato["preco"],
                "subtotal": subtotal,
            }
        )
        valor_total += subtotal

    pedido = PedidoModel.criar(id_sessao, itens, valor_total, str(dados.get("observacao", "")).strip())
    return {"mensagem": "Pedido criado em memória.", "pedido": pedido}, 201


def listar_kds(id_pedido=None):
    pedidos = [PedidoModel.obter(id_pedido)] if id_pedido is not None else PedidoModel.listar()
    pedidos = [pedido for pedido in pedidos if pedido]
    if id_pedido is not None and not pedidos:
        return {"erro": "Pedido não encontrado no KDS."}, 404

    fila = []
    for pedido in pedidos:
        sessao = SessaoModel.obter(pedido["id_sessao"])
        reserva = ReservaModel.obter(sessao["id_reserva"]) if sessao else None
        bancada = BancadaModel.obter(reserva["id_bancada"]) if reserva else None
        fila.append(
            {
                **pedido,
                "id_reserva": reserva["id"] if reserva else None,
                "bancada": bancada["nome"] if bancada else None,
            }
        )

    return {"pedidos": fila}, 200
