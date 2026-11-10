# Importa as entidades para que todos os mapeamentos e FKs sejam conhecidos pelo SQLAlchemy.
# Este arquivo não cria tabelas e não executa consultas ao MySQL.
# Os CRUDs retornam entidades, None para buscas/edições ausentes e bool nas exclusões.
# confirmar=False executa flush; salvar_alteracoes() confirma o conjunto de operações.
# Erros SQL fazem rollback e são repassados ao chamador, sem esconder a causa.
from app.models.usuario_model import (
    Usuario, Cliente, Cozinheiro, Administrador,
    Usuario_model, Cliente_model, Cozinheiro_model, Administrador_model,
)
from app.models.bancada_model import Bancada, Bancada_model
from app.models.reserva_model import Reserva, Reserva_model
from app.models.sessao_model import Sessao, Sessao_model
from app.models.prato_model import Prato, Prato_model
from app.models.pedido_model import Pedido, Pedido_model
from app.models.item_pedido_model import ItemPedido, ItemPedido_model
from app.models.ingrediente_model import Ingrediente, Ingrediente_model
from app.models.ficha_tecnica_model import FichaTecnica, FichaTecnica_model
from app.models.substituicao_model import SubstituicaoIngrediente, Substituicao_model
from app.models._crud import salvar_alteracoes

from app.models.operacao_model import SessaoAutenticacao, LimiteAcesso, EventoAuditoria, MovimentacaoEstoque
