from copy import deepcopy


class BancadaModel:
    _originais = [
        {"id": 1, "nome": "Bancada Toscana", "capacidade": 4, "preco": 85.0, "status": "disponivel"},
        {"id": 2, "nome": "Bancada Provence", "capacidade": 6, "preco": 120.0, "status": "disponivel"},
        {"id": 3, "nome": "Bancada Aurora", "capacidade": 2, "preco": 65.0, "status": "ocupada"},
        {"id": 4, "nome": "Bancada Ipê", "capacidade": 5, "preco": 105.0, "status": "disponivel"},
        {"id": 5, "nome": "Bancada Cedro", "capacidade": 4, "preco": 95.0, "status": "manutencao"},
        {"id": 6, "nome": "Bancada Manacá", "capacidade": 3, "preco": 78.0, "status": "disponivel"},
    ]
    _bancadas = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._bancadas = deepcopy(cls._originais)

    @classmethod
    def listar(cls):
        return deepcopy(cls._bancadas)

    @classmethod
    def obter(cls, id_bancada):
        bancada = next((item for item in cls._bancadas if item["id"] == id_bancada), None)
        return deepcopy(bancada)
