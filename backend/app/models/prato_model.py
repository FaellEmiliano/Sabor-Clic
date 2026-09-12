from copy import deepcopy


class PratoModel:
    _originais = [
        {"id": 1, "nome": "Bruschetta da Casa", "categoria": "Entradas", "preco": 18.9, "disponivel": True},
        {"id": 2, "nome": "Risoto de Cogumelos", "categoria": "Pratos", "preco": 42.0, "disponivel": True},
        {"id": 3, "nome": "Burger Artesanal", "categoria": "Pratos", "preco": 34.9, "disponivel": True},
        {"id": 4, "nome": "Torta de Limão", "categoria": "Sobremesas", "preco": 16.0, "disponivel": True},
        {"id": 5, "nome": "Suco de Laranja", "categoria": "Bebidas", "preco": 9.5, "disponivel": True},
        {"id": 6, "nome": "Soda Italiana", "categoria": "Bebidas", "preco": 13.0, "disponivel": True},
        {"id": 7, "nome": "Nhoque ao Sugo", "categoria": "Pratos", "preco": 37.0, "disponivel": False},
        {"id": 8, "nome": "Petit Gâteau", "categoria": "Sobremesas", "preco": 19.5, "disponivel": True},
    ]
    _pratos = deepcopy(_originais)

    @classmethod
    def reiniciar(cls):
        cls._pratos = deepcopy(cls._originais)

    @classmethod
    def listar(cls):
        return deepcopy(cls._pratos)

    @classmethod
    def obter(cls, id_prato):
        prato = next((item for item in cls._pratos if item["id"] == id_prato), None)
        return deepcopy(prato)
