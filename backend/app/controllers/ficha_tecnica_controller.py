# Importa a captura de exceções do banco de dados para evitar travamentos
from sqlalchemy.exc import SQLAlchemyError

# Importa o model responsável pela comunicação com a tabela ficha_tecnica[cite: 6]
from app.models.ficha_tecnica_model import FichaTecnica_model

class FichaTecnicaController:
    """Controlador de regras de negócio para as Fichas Técnicas (Pratos x Ingredientes)."""

    @staticmethod
    def _serializar_ficha(ficha):
        """Método auxiliar interno para conversão segura de dados (DRY)."""
        return {
            "id_prato": ficha.id_prato,
            "id_ingrediente": ficha.id_ingrediente,
            # Converte Numeric do SQLAlchemy para float a fim de permitir a serialização JSON
            "quantidade_necessaria": float(ficha.quantidade_necessaria) if ficha.quantidade_necessaria is not None else 0.0
        }

    @staticmethod
    def criar(id_prato, id_ingrediente, quantidade_necessaria):
        """Associa um ingrediente a um prato especificando a quantidade."""
        # Validação de presença dos dados da chave composta e da quantidade
        if not id_prato or not id_ingrediente or quantidade_necessaria is None:
            return {"erro": "Os campos 'id_prato', 'id_ingrediente' e 'quantidade_necessaria' são obrigatórios."}, 400

        # Validação preventiva baseada na CheckConstraint ('quantidade_necessaria > 0') do banco[cite: 6]
        if float(quantidade_necessaria) <= 0:
            return {"erro": "A quantidade necessária deve ser maior que zero."}, 400

        try:
            nova_ficha = FichaTecnica_model.inserir_ficha_tecnica(
                id_prato=id_prato,
                id_ingrediente=id_ingrediente,
                quantidade_necessaria=quantidade_necessaria
            )
            return {
                "mensagem": "Ingrediente adicionado à ficha técnica com sucesso.",
                "ficha_tecnica": FichaTecnicaController._serializar_ficha(nova_ficha)
            }, 201
        except SQLAlchemyError:
            # Erros comuns aqui: IDs não existem nas tabelas originais ou já existe essa mesma associação
            return {"erro": "Erro de integridade. Verifique se prato/ingrediente existem ou se já estão associados."}, 409

    @staticmethod
    def obter_por_id(id_prato, id_ingrediente):
        """Obtém uma relação específica usando a chave primária composta[cite: 6]."""
        # Passa os dois IDs para a função do model buscar a tupla correta[cite: 6]
        ficha = FichaTecnica_model.obter_ficha_tecnica(id_prato, id_ingrediente)
        if not ficha:
            return {"erro": "Associação de ficha técnica não encontrada."}, 404

        return {"ficha_tecnica": FichaTecnicaController._serializar_ficha(ficha)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Lista registros da ficha técnica. 
        Aceita filtros dinâmicos, permitindo buscar, por exemplo, todos os ingredientes de um prato específico.
        """
        filtros = filtros or {}
        try:
            # Envia os kwargs de filtro para o model (ex: id_prato=1)[cite: 6]
            fichas = FichaTecnica_model.obter_todos(**filtros)
            return {"fichas_tecnicas": [FichaTecnicaController._serializar_ficha(f) for f in fichas]}, 200
        except ValueError as e:
            # Captura o erro do _crud.py caso um filtro inválido seja enviado
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_prato, id_ingrediente, **kwargs):
        """Atualiza campos permitidos (basicamente 'quantidade_necessaria')[cite: 6]."""
        # Verifica a constraint preventiva da quantidade
        if 'quantidade_necessaria' in kwargs and float(kwargs['quantidade_necessaria']) <= 0:
            return {"erro": "A quantidade necessária deve ser maior que zero."}, 400

        try:
            # Como a PK é composta, passamos ambos os IDs e as modificações[cite: 6]
            # O _crud faz o select. Se retornar None, não existe.
            ficha_atualizada = FichaTecnica_model.atualizar_ficha_tecnica(id_prato, id_ingrediente, **kwargs)
            
            if not ficha_atualizada:
                return {"erro": "Associação de ficha técnica não encontrada."}, 404
                
            return {
                "mensagem": "Ficha técnica atualizada com sucesso.", 
                "ficha_tecnica": FichaTecnicaController._serializar_ficha(ficha_atualizada)
            }, 200
            
        except ValueError as e:
            # Retorna o ValueError do _crud se tentarem atualizar campos não mapeados
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro ao atualizar a ficha técnica no banco de dados."}, 500

    @staticmethod
    def deletar(id_prato, id_ingrediente):
        """Remove a associação entre um ingrediente e um prato."""
        try:
            # O método deletar retorna False se não encontrar o registro
            sucesso = FichaTecnica_model.deletar_ficha_tecnica(id_prato, id_ingrediente)
            if not sucesso:
                return {"erro": "Associação de ficha técnica não encontrada."}, 404
                
            return {"mensagem": "Ingrediente removido da ficha técnica com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao deletar o registro."}, 409