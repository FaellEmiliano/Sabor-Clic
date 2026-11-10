"""Configuration is evaluated by the factory, so tests need no database credentials."""
import os
from pathlib import Path
from secrets import token_hex
from sqlalchemy import URL


def load_environment():
    # Existing process variables always take precedence over the local .env.
    path = Path(__file__).resolve().parents[1] / '.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip().strip('"\''), value.strip().strip('\"\''))


class Config:
    JSON_SORT_KEYS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    LOGIN_LIMIT = 5
    LOGIN_IP_LIMIT = 30
    LOGIN_WINDOW_SECONDS = 900
    SESSION_IDLE_MINUTES = 30
    MAX_CONTENT_LENGTH = 1024 * 1024

    @staticmethod
    def environment():
        load_environment()
        uri = os.environ.get('DATABASE_URL')
        if not uri:
            required = ('DB_USER', 'DB_PASSWORD', 'DB_NAME')
            missing = [key for key in required if key not in os.environ]
            if missing:
                raise RuntimeError('Configure DATABASE_URL ou ' + ', '.join(missing) + ' no .env.')
            uri = URL.create('mysql+pymysql', username=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD'], host=os.environ.get('DB_HOST', 'localhost'),
                port=int(os.environ.get('DB_PORT', '3306')), database=os.environ['DB_NAME'],
                query={'charset': 'utf8mb4'})
        secret = os.environ.get('SECRET_KEY')
        if not secret:
            key_path = Path(__file__).resolve().parents[1] / '.session-key'
            try:
                with key_path.open('x', encoding='utf-8') as handle: handle.write(token_hex(32))
            except FileExistsError:
                pass
            secret = key_path.read_text(encoding='utf-8').strip()
        return {'SQLALCHEMY_DATABASE_URI': uri,
                'SECRET_KEY': secret,
                'SQLALCHEMY_ENGINE_OPTIONS': {'connect_args': {'init_command': "SET time_zone = '+00:00'"}} if not str(uri).startswith('sqlite') else {},
                'SESSION_COOKIE_SECURE': os.environ.get('COOKIE_SECURE', 'false').lower() == 'true',
                'CORS_ORIGINS': [s.strip() for s in os.environ.get('CORS_ORIGINS', '').split(',') if s.strip()]}
