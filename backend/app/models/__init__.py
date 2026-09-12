from app.models.bancada_model import BancadaModel
from app.models.pedido_model import PedidoModel
from app.models.prato_model import PratoModel
from app.models.reserva_model import ReservaModel
from app.models.sessao_model import SessaoModel
from app.models.usuario_model import UsuarioModel


def reiniciar_dados():
    """Restaura os dados demonstrativos, principalmente para testes locais."""
    UsuarioModel.reiniciar()
    BancadaModel.reiniciar()
    ReservaModel.reiniciar()
    SessaoModel.reiniciar()
    PratoModel.reiniciar()
    PedidoModel.reiniciar()
