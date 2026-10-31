# Importa o módulo de captura de falhas do SQLAlchemy para evitar interrupções severas na API
from sqlalchemy.exc import SQLAlchemyError

# Importa o model focado na tabela de substituição de ingredientes[cite: 13]
from substituicao_model import Substituicao_model

class SubstituicaoController:
    """Controlador que agrupa as regras de negócio para substituições de ingredientes."""

    @staticmethod
    def _serializar_substituicao(substituicao):
        """
        Função auxiliar para traduzir a entidade do banco para um dicionário JSON.
        Trata o casting seguro para int na prioridade e float no fator_conversao[cite: 13], 
        agradando analisadores estáticos como o Pylance.
        """
        return {
            "id_ingrediente_original": substituicao.id_ingrediente_original,
            "id_ingrediente_substituto": substituicao.id_ingrediente_substituto,
            "prioridade": int(substituicao.prioridade or 1),
            "fator_conversao": float(substituicao.fator_conversao or 1.0)
        }

    @staticmethod
    def criar(id_ingrediente_original, id_ingrediente_substituto, prioridade=1, fator_conversao=1.0):
        """
        Valida e cadastra uma nova regra de substituição entre dois ingredientes.
        """
        # Checa a presença estrita da chave composta[cite: 13]
        if not id_ingrediente_original or not id_ingrediente_substituto:
            return {"erro": "Os IDs do ingrediente original e do substituto são obrigatórios."}, 400

        # Verificação preventiva espelhada nas constraints do banco ('chk_substituicao_fator' e 'chk_substituicao_prioridade')[cite: 13]
        if int(prioridade or 1) <= 0:
            return {"erro": "A prioridade deve ser um número inteiro maior que zero."}, 400
        if float(fator_conversao or 1.0) <= 0:
            return {"erro": "O fator de conversão deve ser maior que zero."}, 400

        try:
            # Passagem das variáveis com tipagem blindada contra falhas ou valores nulos inesperados
            nova_substituicao = Substituicao_model.inserir_substituicao(
                id_ingrediente_original=int(id_ingrediente_original),
                id_ingrediente_substituto=int(id_ingrediente_substituto),
                prioridade=int(prioridade or 1),
                fator_conversao=float(fator_conversao or 1.0) # type: ignore (caso o model ainda use default 1 int)[cite: 13]
            )
            return {
                "mensagem": "Substituição cadastrada com sucesso.",
                "substituicao": SubstituicaoController._serializar_substituicao(nova_substituicao)
            }, 201
        except SQLAlchemyError:
            # Erro provável de violação de Unique, ou se os ingredientes originais/substitutos não existirem
            return {"erro": "Erro de integridade. Verifique se os ingredientes existem ou se essa substituição já foi cadastrada."}, 409

    @staticmethod
    def obter_por_id(id_ingrediente_original, id_ingrediente_substituto):
        """Busca o detalhe de uma substituição usando a tupla da chave primária composta[cite: 13]."""
        substituicao = Substituicao_model.obter_substituicao(id_ingrediente_original, id_ingrediente_substituto)
        if not substituicao:
            return {"erro": "Substituição de ingrediente não encontrada."}, 404

        return {"substituicao": SubstituicaoController._serializar_substituicao(substituicao)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Lista substituições.
        Permite usar os filtros para buscar, por exemplo, todos os substitutos de um único ingrediente original.
        """
        filtros = filtros or {}
        try:
            substituicoes = Substituicao_model.obter_todos(**filtros)
            return {"substituicoes": [SubstituicaoController._serializar_substituicao(s) for s in substituicoes]}, 200
        except ValueError as e:
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_ingrediente_original, id_ingrediente_substituto, **kwargs):
        """
        Altera as configurações de fator de conversão e prioridade de uma substituição existente[cite: 13].
        """
        # Checa as constraints do banco preventivamente caso essas colunas estejam no payload
        if 'prioridade' in kwargs and int(kwargs['prioridade']) <= 0:
            return {"erro": "A prioridade deve ser maior que zero."}, 400
        if 'fator_conversao' in kwargs and float(kwargs['fator_conversao']) <= 0:
            return {"erro": "O fator de conversão deve ser maior que zero."}, 400

        try:
            # Envia a chave composta e os novos campos para o método do _crud.py[cite: 13]
            sub_atualizada = Substituicao_model.atualizar_substituicao(id_ingrediente_original, id_ingrediente_substituto, **kwargs)
            
            if not sub_atualizada:
                return {"erro": "Substituição não encontrada."}, 404
                
            return {
                "mensagem": "Substituição atualizada com sucesso.", 
                "substituicao": SubstituicaoController._serializar_substituicao(sub_atualizada)
            }, 200
            
        except ValueError as e:
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro interno ao atualizar a substituição no banco de dados."}, 500

    @staticmethod
    def deletar(id_ingrediente_original, id_ingrediente_substituto):
        """Exclui permanentemente uma relação de substituição usando a chave primária[cite: 13]."""
        try:
            sucesso = Substituicao_model.deletar_substituicao(id_ingrediente_original, id_ingrediente_substituto)
            if not sucesso:
                return {"erro": "Substituição não encontrada."}, 404
                
            return {"mensagem": "Substituição deletada com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao tentar deletar o registro."}, 409