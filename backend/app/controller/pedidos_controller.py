# Aqui ficam os endpoints dos pedidos e do cardapio.
from reserva_controller import Reserva_model


# .../api/cardapio - metodo GET
def cardapio():
    cardapio = Cardapio_model.get_cardapio()
    return cardapio, 200

# .../api/pedido/cadastro - metodo POST
def post_pedido(dados):
    id_reserva = dados['id_reserva']
    id_item_pedido = dados['id_item']
    pedido = Pedido_model.post_pedido(id_reserva, id_item_pedido)
    return True, 200

# .../api/pedido/<int:id> - metodo GET
def get_pedido(id):
    pedido = Pedido_model.get_pedido(id)
    return pedido, 200

# .../api/kds/<int:id> - metodo GET
def get_kds(id):
    kds_nota = Pedido_model.criar_kds(id)
    return kds_nota, 200

class Cardapio_model:
    @staticmethod
    def get_cardapio():
        pass

class Pedido_model:
    @staticmethod
    def get_item(id_item):
        pass
    @staticmethod
    def post_pedido(id_reserva, id_item_pedido):
        pass
    @staticmethod
    def get_pedido(id):
        pass
    @staticmethod
    def criar_kds(id):
        pass