from copy import deepcopy


class ReservaModel:
    _originais = [
        {
            "id": 1048,
            "id_cliente": 1,
            "id_bancada": 1,
            "inicio": "2026-09-09T19:00:00",
            "fim": "2026-09-09T22:00:00",
            "pessoas": 4,
            "valor": 85.0,
            "status": "em_andamento",
        }
    ]
    _reservas = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._reservas = deepcopy(cls._originais)

    @classmethod
    def listar(cls):
        return deepcopy(cls._reservas)

    @classmethod
    def obter(cls, id_reserva):
        reserva = next((item for item in cls._reservas if item["id"] == id_reserva), None)
        return deepcopy(reserva)

    @classmethod
    def criar(cls, dados):
        reserva = {"id": max((item["id"] for item in cls._reservas), default=1000) + 1, **dados}
        cls._reservas.append(reserva)
        return deepcopy(reserva)

    @classmethod
    def atualizar_status(cls, id_reserva, status):
        reserva = next((item for item in cls._reservas if item["id"] == id_reserva), None)
        if not reserva:
            return None
        reserva["status"] = status
        return deepcopy(reserva)
