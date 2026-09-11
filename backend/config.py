import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent # Indica pro flask a pasta base do projeto.

class Config: # Definindo as configurações do projeto
    SECRET_KEY = os.environ.get('SECRET_KEY') # Pega a SECRET_KEY - Chave usada
    DATABASE = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'backend' / 'database' / 'saboreclic.db')) # Define o caminho do banco de dados.
    SESSION_COOKIE_HTTPONLY = True # Impede que scripts externos ao site acessem o cookie da session.
    SESSION_COOKIE_SAMESITE = "Lax" # Impede que o cookie da sessão seja enviado a requisições vindas de outros sites.
    JSON_AS_ASCII = False # Evita erro de decodificação das mensagens de resposta do backend pro front.