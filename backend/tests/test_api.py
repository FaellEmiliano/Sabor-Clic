import unittest

from app import criar_app
from app.models import reiniciar_dados


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        reiniciar_dados()
        self.cliente = criar_app({"TESTING": True}).test_client()

    def criar_fluxo(self):
        resposta = self.cliente.post(
            "/api/reservas",
            json={
                "id_cliente": 1,
                "id_bancada": 2,
                "inicio": "2026-09-10T19:00:00",
                "fim": "2026-09-10T22:00:00",
                "pessoas": 6,
            },
        )
        self.assertEqual(resposta.status_code, 201)
        id_reserva = resposta.get_json()["reserva"]["id"]

        resposta = self.cliente.post("/api/sessoes", json={"id_reserva": id_reserva})
        self.assertEqual(resposta.status_code, 201)
        return resposta.get_json()["sessao"]["id"]

    def test_api_expoe_dados_json(self):
        resposta = self.cliente.get("/api")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.content_type, "application/json")
        self.assertEqual(resposta.get_json()["persistencia"], "memoria")

        resposta = self.cliente.get("/api/bancadas")
        self.assertEqual(len(resposta.get_json()["bancadas"]), 6)

    def test_fluxo_reserva_sessao_pedido_kds(self):
        id_sessao = self.criar_fluxo()

        resposta = self.cliente.post(
            "/api/pedido/cadastro",
            json={
                "id_sessao": id_sessao,
                "itens": [
                    {"id_prato": 1, "quantidade": 2},
                    {"id_prato": 5, "quantidade": 1},
                ],
            },
        )
        self.assertEqual(resposta.status_code, 201)
        pedido = resposta.get_json()["pedido"]
        self.assertEqual(pedido["id_sessao"], id_sessao)
        self.assertEqual(pedido["valor_total"], 47.3)

        resposta = self.cliente.get(f"/api/kds/{pedido['id']}")
        item_kds = resposta.get_json()["pedidos"][0]
        self.assertEqual(item_kds["bancada"], "Bancada Provence")

    def test_pedido_exige_sessao_ativa(self):
        id_sessao = self.criar_fluxo()
        self.cliente.post(f"/api/sessoes/{id_sessao}/encerrar")

        resposta = self.cliente.post(
            "/api/pedido/cadastro",
            json={"id_sessao": id_sessao, "itens": [{"id_prato": 1, "quantidade": 1}]},
        )
        self.assertEqual(resposta.status_code, 409)

    def test_reserva_rejeita_conflito_de_horario(self):
        resposta = self.cliente.post(
            "/api/reservas",
            json={
                "id_cliente": 1,
                "id_bancada": 1,
                "inicio": "2026-09-09T20:00:00",
                "fim": "2026-09-09T21:00:00",
                "pessoas": 2,
            },
        )
        self.assertEqual(resposta.status_code, 409)

    def test_login_e_cadastro_continuam_demonstrativos(self):
        resposta = self.cliente.post(
            "/api/login",
            json={"email": "rafael@exemplo.com", "senha": "qualquer-valor"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("simulada", resposta.get_json()["autenticacao"])

        resposta = self.cliente.post(
            "/api/cadastro",
            json={"nome": "Novo Cliente", "email": "novo@exemplo.com"},
        )
        self.assertEqual(resposta.status_code, 201)
        usuario = resposta.get_json()["usuario"]
        self.assertNotIn("senha", usuario)

        resposta = self.cliente.get(f"/api/cadastro/{usuario['id']}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["usuario"]["email"], "novo@exemplo.com")


if __name__ == "__main__":
    unittest.main()
