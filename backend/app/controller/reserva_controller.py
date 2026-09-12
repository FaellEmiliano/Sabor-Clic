# Os endpoints da bancada e das reservas ficam aqui.

#.../api/bancadas - metodo GET
def get_bancadas(): # Retorna a lista de todas as bancadas disponiveis e suas informações basicas.
    lista_bancadas = Bancada_model.get_bancadas()
    return lista_bancadas, 200

# .../api/reservas - metodo POST
def post_reserva(dados): # Cria uma reserva em uma das bancadas disponíveis.
    cliente = dados['cliente']
    bancada = dados['bancada']
    reserva = Reserva_model.post_reserva(cliente, bancada)
    return True, 200

# .../api/reservas/<int:id> - metodo GET
def get_reserva(id): # retorna uma reserva cadastrada pelo o id dela.
    reserva = Reserva_model.get_reserva(id)
    return reserva, 200

class Bancada_model:
    @staticmethod
    def get_bancadas():
        pass

class Reserva_model:
    @staticmethod
    def post_reserva(cliente, bancada):
        pass
    
    @staticmethod
    def get_reserva(id):
        pass