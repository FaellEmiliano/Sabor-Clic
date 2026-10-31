# Importa as exceções do banco de dados para evitar que erros de chave estrangeira quebrem a aplicação
from sqlalchemy.exc import SQLAlchemyError

# Importa o model que se comunica diretamente com a tabela prato[cite: 10]
from app.models.prato_model import Prato_model

class PratoController:
    """Controlador que concentra as regras de negócio para a gestão de pratos no cardápio."""

    @staticmethod
    def _serializar_prato(prato):
        """
        Método auxiliar (DRY) para converter a entidade SQLAlchemy 'Prato' em um dicionário.
        Trata o tipo db.Numeric convertendo-o com segurança para float, satisfazendo o Pylance.
        """
        return {
            "id_prato": prato.id_prato,
            "nome": prato.nome,
            "descricao": prato.descricao,
            # Se vier nulo por algum problema, garante o fallback 0.0 sem perder o tipo float[cite: 10]
            "preco": float(prato.preco or 0.0),
            "ativo": prato.ativo,
        }

    @staticmethod
    def criar(nome, preco, descricao=None, ativo=True):
        """
        Valida os dados e insere um novo prato no cardápio.
        Campos obrigatórios: nome e preco[cite: 10].
        """
        # Checa presença estrita. Preço não pode ser None, mas pode ser 0 caso um prato seja "grátis/brinde"
        if not nome or preco is None:
            return {"erro": "Os campos 'nome' e 'preco' são obrigatórios."}, 400

        try:
            # Garante a conversão do preço para float antes de mandar para o model,
            # protegendo os centavos e respeitando a coluna Numeric do banco[cite: 10]
            novo_prato = Prato_model.inserir_prato(
                nome=nome,
                preco=float(preco or 0.0),
                descricao=descricao,
                ativo=ativo
            )
            return {
                "mensagem": "Prato criado com sucesso.",
                "prato": PratoController._serializar_prato(novo_prato)
            }, 201
        except SQLAlchemyError:
            return {"erro": "Erro interno ao tentar cadastrar o prato."}, 500

    @staticmethod
    def obter_por_id(id_prato):
        """Retorna os dados de um prato específico consultando sua chave primária[cite: 10]."""
        prato = Prato_model.obter_prato(id_prato)
        if not prato:
            return {"erro": "Prato não encontrado."}, 404

        return {"prato": PratoController._serializar_prato(prato)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Lista pratos, aceitando um dicionário de filtros opcional.
        Ex: {"ativo": True} para listar apenas o que está no cardápio[cite: 10].
        """
        filtros = filtros or {}
        try:
            pratos = Prato_model.obter_todos(**filtros)
            return {"pratos": [PratoController._serializar_prato(p) for p in pratos]}, 200
        except ValueError as e:
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_prato, **kwargs):
        """
        Altera as informações do prato (ex: aumento de preço ou mudança de nome).
        A filtragem de chaves inválidas já ocorre nativamente no _crud.py[cite: 10].
        """
        try:
            # O model levanta exceção caso enviem campos proibidos e retorna None se o ID não existir[cite: 10]
            prato_atualizado = Prato_model.atualizar_prato(id_prato, **kwargs)
            
            if not prato_atualizado:
                return {"erro": "Prato não encontrado."}, 404
                
            return {
                "mensagem": "Prato atualizado com sucesso.", 
                "prato": PratoController._serializar_prato(prato_atualizado)
            }, 200
            
        except ValueError as e:
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro interno ao tentar atualizar o prato."}, 500

    @staticmethod
    def alternar_status(id_prato):
        """
        Inverte o valor lógico da coluna 'ativo', permitindo "pausar" um prato sem deletá-lo.
        """
        # Consulta para saber o estado atual antes de inverter
        prato = Prato_model.obter_prato(id_prato)
        if not prato:
            return {"erro": "Prato não encontrado."}, 404

        try:
            novo_status = not prato.ativo
            Prato_model.atualizar_prato(id_prato, ativo=novo_status)
            
            texto_status = "ativo" if novo_status else "inativo"
            return {"mensagem": f"Prato alterado para {texto_status} com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Não foi possível alterar o status do prato."}, 500

    @staticmethod
    def deletar(id_prato):
        """
        Remove permanentemente o prato. 
        Pode sofrer restrição caso o prato já esteja em um item_pedido via RESTRICT[cite: 10].
        """
        try:
            sucesso = Prato_model.deletar_prato(id_prato)
            if not sucesso:
                return {"erro": "Prato não encontrado."}, 404
                
            return {"mensagem": "Prato deletado com sucesso."}, 200
        except SQLAlchemyError:
            # Mensagem focada na relação provável que vai estourar a constraint de chave estrangeira
            return {"erro": "Erro ao deletar. O prato está associado a pedidos ou fichas técnicas."}, 409