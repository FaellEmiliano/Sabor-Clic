# Importa o tratamento de erros do SQLAlchemy para evitar travamento da API em falhas do banco
from sqlalchemy.exc import SQLAlchemyError

# Importa o model que gerencia o acesso à tabela de ingredientes no banco de dados[cite: 7]
from app.models.ingrediente_model import Ingrediente_model

class IngredienteController:
    """Controlador para centralizar a regra de negócio relacionada aos ingredientes."""

    @staticmethod
    def _serializar_ingrediente(ingrediente):
        """
        Método auxiliar para converter o objeto SQLAlchemy Ingrediente em um dicionário.
        Centraliza a lógica para evitar repetição no código.
        """
        return {
            "id_ingrediente": ingrediente.id_ingrediente,
            "nome": ingrediente.nome,
            "unidade_medida": ingrediente.unidade_medida,
            # Converte o tipo Numeric (Decimal) do banco para float, permitindo serialização JSON[cite: 7]
            "quantidade_estoque": float(ingrediente.quantidade_estoque) if ingrediente.quantidade_estoque is not None else 0.0,
        }

    @staticmethod
    def criar(nome, unidade_medida, quantidade_estoque:int=0):
        """
        Valida os dados e cadastra um novo ingrediente.
        HTTP Status: 201 (Criado), 400 (Faltam dados) ou 500 (Erro no banco).
        """
        # Verifica se os campos obrigatórios (nome e unidade_medida) foram informados
        if not nome or not unidade_medida:
            return {"erro": "Os campos 'nome' e 'unidade_medida' são obrigatórios."}, 400

        try:
            # Chama o método de inserção do model[cite: 7]
            novo_ingrediente = Ingrediente_model.inserir_ingrediente(
                nome=nome,
                unidade_medida=unidade_medida,
                quantidade_estoque=quantidade_estoque
            )
            return {
                "mensagem": "Ingrediente cadastrado com sucesso.",
                "ingrediente": IngredienteController._serializar_ingrediente(novo_ingrediente)
            }, 201
        except SQLAlchemyError:
            # Captura falhas de persistência ou restrições do banco
            return {"erro": "Erro interno ao tentar cadastrar o ingrediente."}, 500

    @staticmethod
    def obter_por_id(id_ingrediente):
        """
        Busca um ingrediente específico pela chave primária[cite: 7].
        HTTP Status: 200 (Encontrado) ou 404 (Não encontrado).
        """
        ingrediente = Ingrediente_model.obter_ingrediente(id_ingrediente)
        if not ingrediente:
            return {"erro": "Ingrediente não encontrado."}, 404

        return {"ingrediente": IngredienteController._serializar_ingrediente(ingrediente)}, 200

    @staticmethod
    def obter_todos():
        """
        Retorna uma lista com todos os ingredientes cadastrados[cite: 7].
        HTTP Status: 200 (OK).
        """
        ingredientes = Ingrediente_model.obter_todos()
        # Aplica a serialização em todos os registros do banco através de uma list comprehension limpa
        lista_serializada = [IngredienteController._serializar_ingrediente(i) for i in ingredientes]
        
        return {"ingredientes": lista_serializada}, 200

    @staticmethod
    def atualizar(id_ingrediente, **kwargs):
        """
        Atualiza campos específicos de um ingrediente existente[cite: 7].
        O crud_model se encarrega de rejeitar chaves invasoras e verificar existência.
        HTTP Status: 200 (Sucesso), 400 (Campos inválidos) ou 404 (Não encontrado).
        """
        try:
            # O _crud.py já faz a consulta antes de atualizar. Retorna None se não encontrar o registro.
            ingrediente_atualizado = Ingrediente_model.atualizar_ingrediente(id_ingrediente, **kwargs)
            
            if not ingrediente_atualizado:
                return {"erro": "Ingrediente não encontrado."}, 404
                
            return {
                "mensagem": "Ingrediente atualizado com sucesso.", 
                "ingrediente": IngredienteController._serializar_ingrediente(ingrediente_atualizado)
            }, 200
            
        except ValueError as e:
            # O _atualizar do Crud_model levanta ValueError se enviarem campos não permitidos (ex: id_ingrediente)
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro interno ao atualizar o ingrediente no banco de dados."}, 500

    @staticmethod
    def deletar(id_ingrediente):
        """
        Deleta permanentemente o registro do ingrediente[cite: 7].
        HTTP Status: 200 (Sucesso), 404 (Não encontrado) ou 409 (Conflito/Vínculos).
        """
        try:
            # O método deletar do model retorna False se não encontrar o registro
            sucesso = Ingrediente_model.deletar_ingrediente(id_ingrediente)
            if not sucesso:
                return {"erro": "Ingrediente não encontrado."}, 404
                
            return {"mensagem": "Ingrediente deletado com sucesso."}, 200
        except SQLAlchemyError:
            # Tratamento focado em restrições RESTRICT nas tabelas filhas (ex: Ficha Técnica)
            return {"erro": "Erro ao deletar. O ingrediente está vinculado a fichas técnicas ou requisições."}, 409