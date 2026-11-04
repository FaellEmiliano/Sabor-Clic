from datetime import timedelta
from uuid import uuid4
from pathlib import Path
import click
from flask import g, Flask, abort, jsonify, request, send_from_directory
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException
from config import Config
from app.extensions import db
from app.controllers.http import fail, protect
from app.routes.api_routes import api_bp


def criar_app(configuracao=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    # Explicit test configuration bypasses the local .env and MySQL entirely.
    if configuracao and configuracao.get('SQLALCHEMY_DATABASE_URI'):
        app.config.update(SECRET_KEY='test-only' if configuracao.get('TESTING') else None, CORS_ORIGINS=[], SQLALCHEMY_ENGINE_OPTIONS={'connect_args':{'init_command':"SET time_zone = '+00:00'"}} if str(configuracao['SQLALCHEMY_DATABASE_URI']).startswith('mysql') else {})
    else:
        app.config.update(Config.environment())
    app.config.update(PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
    if configuracao:
        app.config.update(configuracao)
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError('Configure SECRET_KEY.')
    db.init_app(app)
    app.register_blueprint(api_bp)

    @app.before_request
    def access():
        g.request_id=uuid4().hex
        origin = request.headers.get('Origin')
        if request.path.startswith('/api') and origin and origin != request.host_url.rstrip('/') and origin not in app.config['CORS_ORIGINS']:
            fail('Origem não autorizada.',403)
        protect()

    @app.after_request
    def cors(response):
        origin = request.headers.get('Origin')
        if origin and origin in app.config['CORS_ORIGINS']:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRF-Token, Idempotency-Key'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, DELETE, OPTIONS'
            response.vary.add('Origin')
        if response.is_json and getattr(g,'pagination',None):
            data=response.get_json()
            if isinstance(data,dict):
                data['metadados']=g.pagination
                response.set_data(app.json.dumps(data))
        if request.path.startswith('/api'):
            response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Referrer-Policy']='same-origin'
        response.headers['X-Request-ID']=g.request_id
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        if request.is_secure:response.headers['Strict-Transport-Security']='max-age=31536000'
        if response.status_code==429:response.headers['Retry-After']=str(app.config['LOGIN_WINDOW_SECONDS'])
        from app.controllers.seguranca_controller import record_audit
        return record_audit(response)

    @app.get('/api')
    def status_api():
        return jsonify(aplicacao='Sabor e Clic',status='online',persistencia='banco de dados',fluxo=['reserva','sessao','pedido','kds'])

    @app.errorhandler(HTTPException)
    def http_error(error):
        db.session.rollback()
        return jsonify(erro=error.description,codigo={400:'INVALID_INPUT',401:'UNAUTHENTICATED',403:'FORBIDDEN',404:'NOT_FOUND',409:'CONFLICT',429:'RATE_LIMIT'}.get(error.code,'HTTP_ERROR')),error.code

    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        db.session.rollback()
        return jsonify(erro='Dados em conflito: registro duplicado, vínculo inválido ou exclusão impedida.'),409

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.error('Falha de persistência (%s).',type(error).__name__)
        return jsonify(erro='Não foi possível acessar o banco de dados.'),503

    @app.errorhandler(Exception)
    def unexpected_error(error):
        db.session.rollback()
        app.logger.error('Erro inesperado %s; correlation=%s',type(error).__name__,getattr(g,'request_id',''))
        return jsonify(erro='Não foi possível concluir a operação.',codigo='INTERNAL_ERROR'),500

    frontend = Path(__file__).resolve().parents[2] / 'FrontEnd'

    @app.get('/')
    def index():
        return send_from_directory(frontend,'index.html')

    @app.get('/<path:path>')
    def frontend_file(path):
        if not (path.endswith('.html') and '/' not in path or path.startswith('assets/')):
            abort(404)
        return send_from_directory(frontend,path)

    @app.cli.command('init-db')
    def init_db():
        """Create missing tables, without dropping existing data."""
        from app.database import migrate
        migrate()
        click.echo('SQL aplicado sem triggers e sem apagar registros.')

    @app.cli.command('migrate-db')
    def migrate_db():
        from app.database import migrate
        migrate()
        click.echo('Migração SQL aditiva concluída.')

    @app.cli.command('seed-demo')
    @click.option('--senha',prompt=True,hide_input=True,confirmation_prompt=True)
    def seed_demo(senha):
        from app.database import seed
        from werkzeug.security import generate_password_hash
        if len(senha)<8:raise click.ClickException('A senha deve ter pelo menos oito caracteres.')
        seed(generate_password_hash(senha))
        click.echo('Demonstração criada: admin@demo.local, cliente@demo.local, chef@demo.local.')

    @app.cli.command('backup-db')
    @click.argument('path',type=click.Path())
    def backup_db(path):
        from app.database import backup
        backup(path)
        click.echo('Snapshot de dados criado. Trate-o como arquivo confidencial.')

    @app.cli.command('restore-db')
    @click.argument('path',type=click.Path(exists=True))
    def restore_db(path):
        from app.database import restore
        try:restore(path)
        except ValueError as error:raise click.ClickException(str(error)) from None
        click.echo('Snapshot restaurado em banco vazio.')

    @app.cli.command('create-admin')
    @click.option('--nome',prompt=True)
    @click.option('--email',prompt=True)
    @click.option('--senha',prompt=True,hide_input=True,confirmation_prompt=True)
    def create_admin(nome,email,senha):
        """Bootstrap an administrator without exposing a public privileged signup."""
        from app.models import Usuario_model
        if len(senha)<8 or '@' not in email:
            raise click.ClickException('Informe um e-mail e uma senha de pelo menos 8 caracteres.')
        try:
            Usuario_model.inserir_administrador(nome,email.strip().lower(),senha)
        except IntegrityError:
            raise click.ClickException('E-mail já cadastrado.') from None
        click.echo('Administrador criado.')

    return app
