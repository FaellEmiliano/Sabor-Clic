from copy import deepcopy
from datetime import datetime


class SessaoModel:
    _originais = [
        {
            "id": 501,
            "id_reserva": 1048,
            "codigo_acesso": "SES-1048",
            "status": "ativa",
            "criada_em": "2026-09-09T18:58:00",
            "iniciada_em": "2026-09-09T19:00:00",
            "encerrada_em": None,
        }
    ]
    _sessoes = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._sessoes = deepcopy(cls._originais)

    @classmethod
    def obter(cls, id_sessao):
        sessao = next((item for item in cls._sessoes if item["id"] == id_sessao), None)
        return deepcopy(sessao)

    @classmethod
    def obter_por_reserva(cls, id_reserva):
        sessao = next((item for item in cls._sessoes if item["id_reserva"] == id_reserva), None)
        return deepcopy(sessao)

    @classmethod
    def criar(cls, id_reserva):
        agora = datetime.now().isoformat(timespec="seconds")
        sessao = {
            "id": max((item["id"] for item in cls._sessoes), default=500) + 1,
            "id_reserva": id_reserva,
            "codigo_acesso": f"SES-{id_reserva}",
            "status": "ativa",
            "criada_em": agora,
            "iniciada_em": agora,
            "encerrada_em": None,
        }
        cls._sessoes.append(sessao)
        return deepcopy(sessao)

    @classmethod
    def encerrar(cls, id_sessao):
        sessao = next((item for item in cls._sessoes if item["id"] == id_sessao), None)
        if not sessao:
            return None
        sessao["status"] = "encerrada"
        sessao["encerrada_em"] = datetime.now().isoformat(timespec="seconds")
        return deepcopy(sessao)
