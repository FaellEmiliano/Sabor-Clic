from copy import deepcopy
from datetime import datetime


class PedidoModel:
    _originais = [
        {
            "id": 209,
            "id_sessao": 501,
            "itens": [
                {"id_prato": 2, "nome": "Risoto de Cogumelos", "quantidade": 1, "preco_unitario": 42.0, "subtotal": 42.0},
                {"id_prato": 5, "nome": "Suco de Laranja", "quantidade": 2, "preco_unitario": 9.5, "subtotal": 19.0},
            ],
            "valor_total": 61.0,
            "observacao": "",
            "status": "em_preparo",
            "criado_em": "2026-09-09T20:14:00",
        }
    ]
    _pedidos = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._pedidos = deepcopy(cls._originais)

    @classmethod
    def obter(cls, id_pedido):
        pedido = next((item for item in cls._pedidos if item["id"] == id_pedido), None)
        return deepcopy(pedido)

    @classmethod
    def listar(cls):
        return deepcopy(cls._pedidos)

    @classmethod
    def criar(cls, id_sessao, itens, valor_total, observacao=""):
        pedido = {
            "id": max((item["id"] for item in cls._pedidos), default=200) + 1,
            "id_sessao": id_sessao,
            "itens": deepcopy(itens),
            "valor_total": round(valor_total, 2),
            "observacao": observacao,
            "status": "recebido",
            "criado_em": datetime.now().isoformat(timespec="seconds"),
        }
        cls._pedidos.append(pedido)
        return deepcopy(pedido)
