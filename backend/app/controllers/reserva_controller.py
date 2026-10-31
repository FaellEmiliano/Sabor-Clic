# Importa o tratamento de erros do SQLAlchemy para evitar travamento da API por quebra de constraints
from sqlalchemy.exc import SQLAlchemyError

# Para validação preventiva de datas antes de bater no banco de dados
from datetime import datetime

# Importa o model que gerencia o acesso à tabela reserva[cite: 11]
from app.models.reserva_model import Reserva_model

class ReservaController:
    """Controlador que concentra as regras de negócio de agendamento de reservas."""

    @staticmethod
    def _serializar_reserva(reserva):
        """
        Método auxiliar (DRY) para converter a entidade SQLAlchemy 'Reserva' em dicionário.
        Lida com a conversão de Numeric para float e formata objetos DateTime para String ISO 8601.
        """
        return {
            "id_reserva": reserva.id_reserva,
            "id_cliente": reserva.id_cliente,
            "id_bancada": reserva.id_bancada,
            # Converte as datas para string no formato ISO (ex: '2026-10-30T19:00:00')
            "inicio": reserva.inicio.isoformat() if reserva.inicio else None,
            "fim": reserva.fim.isoformat() if reserva.fim else None,
            "status": reserva.status,
            # Mantém a segurança de tipagem abordada anteriormente[cite: 11]
            "valor_total": float(reserva.valor_total or 0.0),
            "criado_em": reserva.criado_em.isoformat() if reserva.criado_em else None
        }

    @staticmethod
    def criar(id_cliente, id_bancada, inicio, fim, status, valor_total=0.0):
        """
        Valida e cadastra uma nova reserva.
        Campos obrigatórios: id_cliente, id_bancada, inicio, fim, status[cite: 11].
        """
        if not id_cliente or not id_bancada or not inicio or not fim or not status:
            return {"erro": "Os campos 'id_cliente', 'id_bancada', 'inicio', 'fim' e 'status' são obrigatórios."}, 400

        # Validação preventiva básica de datas, evitando viagem desnecessária ao banco
        # Caso 'inicio' e 'fim' venham como strings ISO 8601 do frontend
        try:
            if isinstance(inicio, str) and isinstance(fim, str):
                dt_inicio = datetime.fromisoformat(inicio.replace("Z", "+00:00"))
                dt_fim = datetime.fromisoformat(fim.replace("Z", "+00:00"))
                if dt_fim <= dt_inicio:
                    return {"erro": "A data/hora de 'fim' deve ser posterior ao 'inicio'."}, 400
        except ValueError:
            return {"erro": "Formato de data inválido. Utilize o formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)."}, 400

        try:
            # Envia os dados convertidos e tipados conforme assinatura do model[cite: 11]
            nova_reserva = Reserva_model.inserir_reserva(
                id_cliente=int(id_cliente),
                id_bancada=int(id_bancada),
                inicio=inicio,
                fim=fim,
                status=str(status),
                valor_total=float(valor_total or 0.0)
            )
            return {
                "mensagem": "Reserva criada com sucesso.",
                "reserva": ReservaController._serializar_reserva(nova_reserva)
            }, 201
        except SQLAlchemyError:
            # Captura erros como violação da CheckConstraint 'chk_reserva_periodo'[cite: 11]
            # ou tentativa de agendar para id_cliente/id_bancada inexistentes
            return {"erro": "Erro ao tentar criar a reserva. Verifique se o cliente/bancada existem e se as datas são válidas."}, 409

    @staticmethod
    def obter_por_id(id_reserva):
        """Busca os dados de uma reserva pela chave primária[cite: 11]."""
        reserva = Reserva_model.obter_reserva(id_reserva)
        if not reserva:
            return {"erro": "Reserva não encontrada."}, 404

        return {"reserva": ReservaController._serializar_reserva(reserva)}, 200

    @staticmethod
    def obter_todos(filtros=None):
        """
        Lista reservas cadastradas. Permite aplicar filtros opcionais (ex: id_cliente=3)[cite: 11].
        """
        filtros = filtros or {}
        try:
            reservas = Reserva_model.obter_todos(**filtros)
            return {"reservas": [ReservaController._serializar_reserva(r) for r in reservas]}, 200
        except ValueError as e:
            return {"erro": str(e)}, 400

    @staticmethod
    def atualizar(id_reserva, **kwargs):
        """
        Altera as informações da reserva. 
        Permitido: id_cliente, id_bancada, inicio, fim, status, valor_total[cite: 11].
        """
        try:
            # O crud_model impede chaves invasoras usando 'campos_atualizaveis'[cite: 11]
            reserva_atualizada = Reserva_model.atualizar_reserva(id_reserva, **kwargs)
            
            if not reserva_atualizada:
                return {"erro": "Reserva não encontrada."}, 404
                
            return {
                "mensagem": "Reserva atualizada com sucesso.", 
                "reserva": ReservaController._serializar_reserva(reserva_atualizada)
            }, 200
            
        except ValueError as e:
            return {"erro": str(e)}, 400
        except SQLAlchemyError:
            return {"erro": "Erro interno ao atualizar a reserva. Conflito de regras de negócio."}, 409

    @staticmethod
    def deletar(id_reserva):
        """
        Remove a reserva permanentemente.
        Pode sofrer bloqueio caso o banco possua regras rigorosas, mas a PK resolve a exclusão[cite: 11].
        """
        try:
            sucesso = Reserva_model.deletar_reserva(id_reserva)
            if not sucesso:
                return {"erro": "Reserva não encontrada."}, 404
                
            return {"mensagem": "Reserva deletada com sucesso."}, 200
        except SQLAlchemyError:
            return {"erro": "Erro ao tentar deletar a reserva."}, 409