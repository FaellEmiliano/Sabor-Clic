import os
import re
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

from flask import Flask
from sqlalchemy import event
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

# A configuração é importada sem credenciais reais; todos os testes usam SQLite em memória.
with patch.dict(os.environ, {"DB_USER": "teste", "DB_PASSWORD": "teste", "DB_NAME": "teste"}):
    from app.extensions import db
    from app import models as m


class ModelTestCase(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", TESTING=True)
        db.init_app(self.app)
        self.contexto = self.app.app_context()
        self.contexto.push()

        @event.listens_for(db.engine, "connect")
        def ativar_chaves_estrangeiras(conexao, _registro):
            conexao.execute("PRAGMA foreign_keys=ON")

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.contexto.pop()

    def test_mapeamento_corresponde_ao_schema_mysql(self):
        esquema = (Path(__file__).parents[1] / "database" / "01_modelo_fisico.sql").read_text(encoding="utf-8")
        tabelas = re.findall(r"CREATE TABLE IF NOT EXISTS `([^`]+)` \((.*?)\) ENGINE=", esquema, re.S)
        self.assertEqual(set(db.metadata.tables), {nome for nome, _ in tabelas})
        for nome, corpo in tabelas:
            with self.subTest(tabela=nome):
                tabela = db.metadata.tables[nome]
                colunas = re.findall(r"^  `([^`]+)` ([a-z]+(?:\([\d,]+\))?)([^\n]*)", corpo, re.M)
                self.assertEqual(set(tabela.columns.keys()), {coluna for coluna, _, _ in colunas})
                for coluna, tipo_sql, definicao in colunas:
                    tipo_python = str(tabela.columns[coluna].type.compile(dialect=mysql.dialect())).lower().replace(" ", "")
                    tipo_python = tipo_python.replace("numeric(", "decimal(")
                    tipo_python = {"integer": "int", "bool": "tinyint(1)"}.get(tipo_python, tipo_python)
                    self.assertEqual(tipo_python, tipo_sql)
                    self.assertEqual(tabela.columns[coluna].nullable, "NOT NULL" not in definicao)
                pk = re.search(r"PRIMARY KEY \(([^)]+)\)", corpo).group(1)
                self.assertEqual(list(tabela.primary_key.columns.keys()), re.findall(r"`([^`]+)`", pk))
                fks = re.findall(r"FOREIGN KEY \(`([^`]+)`\) REFERENCES `([^`]+)` \(`([^`]+)`\) ON DELETE (CASCADE|RESTRICT|SET NULL) ON UPDATE (CASCADE|RESTRICT|SET NULL)", corpo)
                esperado = {(coluna, f"{destino}.{chave}", excluir, atualizar) for coluna, destino, chave, excluir, atualizar in fks}
                real = {(fk.parent.name, fk.target_fullname, fk.ondelete, fk.onupdate) for fk in tabela.foreign_keys}
                self.assertEqual(real, esperado)

    def criar_contexto(self):
        cliente = m.Usuario_model.inserir_cliente("Cliente", "cliente@teste.com", "senha")
        bancada = m.Bancada_model.inserir_bancada("Toscana", Decimal("85.00"))
        inicio = datetime(2026, 10, 30, 19)
        reserva = m.Reserva_model.inserir_reserva(
            cliente.id_usuario, bancada.id_bancada, inicio,
            inicio + timedelta(hours=2), "CONFIRMADA", Decimal("170.00"),
        )
        sessao = m.Sessao_model.inserir_sessao(reserva.id_reserva, "CODIGO-TESTE", "ATIVA")
        prato = m.Prato_model.inserir_prato("Risoto", Decimal("42.50"))
        return cliente, bancada, reserva, sessao, prato

    def test_crud_das_nove_entidades(self):
        _, bancada, reserva, sessao, prato = self.criar_contexto()
        pedido = m.Pedido_model.inserir_pedido(sessao.id_sessao, "AGUARDANDO", Decimal("85.00"))
        item = m.ItemPedido_model.inserir_item_pedido(
            pedido.id_pedido, prato.id_prato, 2, Decimal("42.50"), Decimal("85.00"),
        )
        ingrediente = m.Ingrediente_model.inserir_ingrediente("Arroz", "kg", Decimal("10.125"))
        substituto = m.Ingrediente_model.inserir_ingrediente("Arroz alternativo", "kg", 5)
        ficha = m.FichaTecnica_model.inserir_ficha_tecnica(prato.id_prato, ingrediente.id_ingrediente, Decimal("0.150"))
        substituicao = m.Substituicao_model.inserir_substituicao(
            ingrediente.id_ingrediente, substituto.id_ingrediente, 1, Decimal("1.2500"),
        )

        casos = [
            (m.Bancada_model, "bancada", (bancada.id_bancada,), {"descricao": "Editada"}),
            (m.Reserva_model, "reserva", (reserva.id_reserva,), {"status": "EM_USO"}),
            (m.Sessao_model, "sessao", (sessao.id_sessao,), {"status": "ENCERRADA"}),
            (m.Prato_model, "prato", (prato.id_prato,), {"preco": Decimal("43.00")}),
            (m.Pedido_model, "pedido", (pedido.id_pedido,), {"tempo_estimado": 15}),
            (m.ItemPedido_model, "item_pedido", (item.id_item_pedido,), {"quantidade": 3, "subtotal": Decimal("127.50")}),
            (m.Ingrediente_model, "ingrediente", (ingrediente.id_ingrediente,), {"quantidade_estoque": Decimal("8.500")}),
            (m.FichaTecnica_model, "ficha_tecnica", (ficha.id_prato, ficha.id_ingrediente), {"quantidade_necessaria": Decimal("0.200")}),
            (m.Substituicao_model, "substituicao", (substituicao.id_ingrediente_original, substituicao.id_ingrediente_substituto), {"prioridade": 2}),
        ]
        for model, nome, chave, campos in casos:
            with self.subTest(model=nome):
                registro = getattr(model, "obter_" + nome)(*chave)
                self.assertIsNotNone(registro)
                self.assertIn(registro, model.obter_todos())
                atualizado = getattr(model, "atualizar_" + nome)(*chave, **campos)
                for campo, valor in campos.items():
                    self.assertEqual(getattr(atualizado, campo), valor)

        # Exclui os dependentes antes dos pais para respeitar as FKs restritivas.
        ordem = [casos[i] for i in (8, 7, 5, 4, 2, 1, 0, 3, 6)]
        for model, nome, chave, _ in ordem:
            self.assertTrue(getattr(model, "deletar_" + nome)(*chave))
            self.assertIsNone(getattr(model, "obter_" + nome)(*chave))

    def test_usuarios_e_especializacoes_sem_coluna_tipo(self):
        self.assertNotIn("tipo", m.Usuario.__table__.columns)
        cliente = m.Usuario_model.inserir_cliente("Cliente", "cliente@teste.com", "segredo")
        cozinheiro = m.Usuario_model.inserir_cozinheiro("Cozinheiro", "cozinha@teste.com", "segredo", "noite", "massas")
        admin = m.Usuario_model.inserir_administrador("Admin", "admin@teste.com", "segredo")
        self.assertEqual(cliente.usuario.nome, "Cliente")
        self.assertTrue(check_password_hash(cliente.usuario.senha_hash, "segredo"))
        self.assertEqual(m.Usuario_model.obter_usuario_email("admin@teste.com").id_usuario, admin.id_usuario)
        m.Usuario_model.atualizar_usuario(cliente.id_usuario, nome="Novo nome", ativo=False)
        self.assertFalse(cliente.usuario.ativo)
        m.Usuario_model.atualizar_senha(cliente.id_usuario, "outra senha")
        self.assertTrue(check_password_hash(cliente.usuario.senha_hash, "outra senha"))
        m.Cliente_model.atualizar_cliente(cliente.id_usuario, endereco_entrega="Rua 1")
        m.Cozinheiro_model.atualizar_cozinheiro(cozinheiro.id_usuario, turno="tarde")
        self.assertEqual(cliente.endereco_entrega, "Rua 1")
        self.assertEqual(cozinheiro.turno, "tarde")
        for entidade in (cliente, cozinheiro, admin):
            id_usuario = entidade.id_usuario
            self.assertTrue(m.Usuario_model.deletar_usuario(id_usuario))
            self.assertIsNone(m.Usuario_model.obter_usuario_id(id_usuario))
        self.assertEqual(m.Cliente_model.obter_todos(), [])
        self.assertEqual(m.Cozinheiro_model.obter_todos(), [])
        self.assertEqual(m.Administrador_model.obter_todos(), [])

    def test_vinculos_de_usuarios_existentes(self):
        usuario = m.Usuario_model.inserir_usuario("Usuario", "usuario@teste.com", "senha")
        id_usuario = usuario.id_usuario
        for model, nome in ((m.Cliente_model, "cliente"), (m.Cozinheiro_model, "cozinheiro"), (m.Administrador_model, "administrador")):
            with self.subTest(perfil=nome):
                registro = getattr(model, "inserir_" + nome)(id_usuario)
                self.assertIs(getattr(model, "obter_" + nome)(id_usuario), registro)
                self.assertIn(registro, model.obter_todos())
                self.assertTrue(getattr(model, "deletar_" + nome)(id_usuario))
                self.assertIsNotNone(m.Usuario_model.obter_usuario_id(id_usuario))

    def test_rollback_recupera_sessao_apos_erro(self):
        m.Usuario_model.inserir_cliente("Primeiro", "duplicado@teste.com", "senha")
        with self.assertRaises(IntegrityError):
            m.Usuario_model.inserir_cliente("Segundo", "duplicado@teste.com", "senha")
        self.assertEqual(len(m.Usuario_model.obter_todos()), 1)
        self.assertEqual(len(m.Cliente_model.obter_todos()), 1)
        m.Prato_model.inserir_prato("Ainda funciona", 10)

    def test_operacoes_podem_compartilhar_transacao(self):
        _, _, _, sessao, prato = self.criar_contexto()
        pedido = m.Pedido_model.inserir_pedido(sessao.id_sessao, "AGUARDANDO", confirmar=False)
        self.assertIsNotNone(pedido.id_pedido)
        m.ItemPedido_model.inserir_item_pedido(pedido.id_pedido, prato.id_prato, 1, 10, 10, confirmar=False)
        db.session.rollback()
        self.assertEqual(m.Pedido_model.obter_todos(), [])
        self.assertEqual(m.ItemPedido_model.obter_todos(), [])
        pedido = m.Pedido_model.inserir_pedido(sessao.id_sessao, "AGUARDANDO", confirmar=False)
        m.ItemPedido_model.inserir_item_pedido(pedido.id_pedido, prato.id_prato, 1, 10, 10, confirmar=False)
        m.salvar_alteracoes()
        self.assertEqual(len(m.Pedido_model.obter_todos()), 1)
        self.assertEqual(len(m.ItemPedido_model.obter_todos()), 1)

    def test_restricoes_e_chaves_compostas(self):
        _, bancada, reserva, sessao, prato = self.criar_contexto()
        with self.assertRaises(IntegrityError):
            m.Sessao_model.inserir_sessao(reserva.id_reserva, "OUTRO-CODIGO", "ATIVA")
        with self.assertRaises(IntegrityError):
            m.Bancada_model.deletar_bancada(bancada.id_bancada)
        with self.assertRaises(IntegrityError):
            m.Pedido_model.inserir_pedido(999999, "AGUARDANDO")
        ingrediente = m.Ingrediente_model.inserir_ingrediente("Ingrediente", "kg", 1)
        m.FichaTecnica_model.inserir_ficha_tecnica(prato.id_prato, ingrediente.id_ingrediente, Decimal("0.100"))
        with self.assertRaises(IntegrityError):
            m.FichaTecnica_model.inserir_ficha_tecnica(prato.id_prato, ingrediente.id_ingrediente, Decimal("0.200"))
        with self.assertRaises(IntegrityError):
            m.Ingrediente_model.deletar_ingrediente(ingrediente.id_ingrediente)
        self.assertEqual(len(m.FichaTecnica_model.obter_todos(id_prato=prato.id_prato)), 1)

    def test_chaves_e_campos_desconhecidos_nao_sao_alterados(self):
        prato = m.Prato_model.inserir_prato("Prato", 10)
        with self.assertRaises(TypeError):
            m.Prato_model.atualizar_prato(prato.id_prato, id_prato=999)
        with self.assertRaises(ValueError):
            m.Prato_model.atualizar_prato(prato.id_prato, inexistente="valor")
        with self.assertRaises(ValueError):
            m.Prato_model.obter_todos(inexistente="valor")
        self.assertIsNone(m.Prato_model.atualizar_prato(999, nome="Ausente"))
        self.assertFalse(m.Prato_model.deletar_prato(999))
        self.assertEqual(m.Prato_model.obter_todos(nome="Ausente"), [])


if __name__ == "__main__":
    main()
