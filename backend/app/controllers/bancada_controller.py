from sqlalchemy.exc import SQLAlchemyError
from app.models.bancada_model import Bancada_model

class BancadaController:
    @staticmethod
    def _serializar_bancada(bancada):
        """Método auxiliar interno para evitar repetição (DRY)."""
        return {
            "id_bancada": bancada.id_bancada,
            "nome": bancada.nome,
            "descricao": bancada.descricao,
            "valor_hora": float(bancada.valor_hora) if bancada.valor_hora is not None else 0.0,
            "ativa": bancada.ativa,
        }

    @staticmethod
    def criar(nome, valor_hora, descricao=None, ativa=True):
        if not nome or valor_hora is None:
            return {"erro": "Os campos 'nome' e 'valor_hora' são obrigatórios."}, 400

        try:
            nova_bancada = Bancada_model.inserir_bancada(
                nome=nome,
                valor_hora=valor_hora,
                descricao=descricao,
                ativa=ativa
            )
            return {
                "mensagem": "Bancada criada com sucesso.",
                "bancada": BancadaController._serializar_bancada(nova_bancada)
            }, 201
        except SQLAlchemyError:
            return {"erro": "Erro interno ao tentar cadastrar a bancada."}, 500

    @staticmethod
    def obter_por_id(id_bancada):
        # A consulta simples permanece igual[cite: 5]
        bancada = Bancada_model.obter_bancada(id_bancada)
        if not bancada:
            return {"erro": "Bancada não encontrada."}, 404

        return {"bancada": BancadaController._serializar_bancada(bancada)}, 200

    @staticmethod
    def obter_todos():
        bancadas = Bancada_model.obter_todos()
        # Serializa todas as instâncias em uma list comprehension limpa
        return {"bancadas": [BancadaController._serializar_bancada(b) for b in bancadas]}, 200

    @staticmethod
    def atualizar(id_bancada, **kwargs):
        try:
            # O _crud.py já faz o select primeiro. Se retornar None, a bancada não existe[cite: 4]
            bancada_atualizada = Bancada_model.atualizar_bancada(id_bancada, **kwargs)
            
            if not bancada_atualizada:
                return {"erro": "Bancada não encontrada."}, 404
                
            return {
                "mensagem": "Bancada atualizada com sucesso.", 
                "bancada": BancadaController._serializar_bancada(bancada_atualizada)
            }, 200
            
        except ValueError as e:
            # O _atualizar do Crud_model levanta ValueError se enviarem campos não mapeados[cite: 4]
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro ao atualizar a bancada no banco de dados."}, 500

    @staticmethod
    def alternar_status(id_bancada):
        # Aqui o 'obter' é necessário primeiro para sabermos qual era o valor antigo antes de inverter[cite: 5]
        bancada = Bancada_model.obter_bancada(id_bancada)
        if not bancada:
            return {"erro": "Bancada não encontrada."}, 404

        try:
            novo_status = not bancada.ativa
            Bancada_model.atualizar_bancada(id_bancada, ativa=novo_status)
            
            texto_status = "ativa" if novo_status else "inativa"
            return {"mensagem": f"Bancada alterada para {texto_status} com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Não foi possível alterar o status da bancada."}, 500

    @staticmethod
    def deletar(id_bancada):
        try:
            # O método _deletar retorna False se não encontrar o registro[cite: 4]
            sucesso = Bancada_model.deletar_bancada(id_bancada)
            if not sucesso:
                return {"erro": "Bancada não encontrada."}, 404
                
            return {"mensagem": "Bancada deletada com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao deletar. Existem vínculos que impedem a exclusão da bancada."}, 409