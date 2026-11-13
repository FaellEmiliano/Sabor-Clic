"""Execute reviewed SQL scripts; schema initialization never generates MySQL DDL from ORM."""
from pathlib import Path
import json
from datetime import datetime
from decimal import Decimal
from sqlalchemy import inspect, text
from app.extensions import db

SQL_DIR=Path(__file__).resolve().parents[1]/'database'


def statements(path):
    delimiter=';';buffer=[]
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        stripped=line.strip()
        if stripped.startswith('--') or not stripped:continue
        if stripped.upper().startswith('DELIMITER '):
            delimiter=stripped.split(None,1)[1];continue
        buffer.append(line)
        if stripped.endswith(delimiter):
            yield '\n'.join(buffer).rstrip()[:-len(delimiter)]
            buffer=[]
    if buffer:raise ValueError('SQL incompleto: '+str(path))


def run_script(connection,name):
    for sql in statements(SQL_DIR/name):connection.exec_driver_sql(sql)


def initialize():
    if db.engine.dialect.name!='mysql':
        raise RuntimeError('init-db exige MySQL. SQLite é usado apenas nas fixtures de teste.')
    db.session.remove()
    with db.engine.begin() as connection:
        run_script(connection,'01_modelo_fisico.sql')


def seed(password_hash):
    with db.engine.begin() as connection:
        connection.exec_driver_sql('SET @demo_password_hash=%s',(password_hash,))
        run_script(connection,'02_insercoes_basicas.sql')


def backup(path):
    """Logical data snapshot for restoring into an already initialized empty schema."""
    inspector=inspect(db.engine);result={'format':1,'tables':{}}
    with db.engine.connect() as connection:
        for table in inspector.get_table_names():
            rows=connection.execute(text('SELECT * FROM `'+table+'`')).mappings().all()
            result['tables'][table]=[{key:({'datetime':value.isoformat()} if isinstance(value,datetime) else {'decimal':str(value)} if isinstance(value,Decimal) else value) for key,value in row.items()} for row in rows]
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as handle:json.dump(result,handle,ensure_ascii=False)
    return target


def restore(path):
    """Restore data only into an empty schema initialized by the handwritten SQL."""
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('format')!=1 or not isinstance(data.get('tables'),dict):raise ValueError('Snapshot inválido.')
    inspector=inspect(db.engine);known=set(inspector.get_table_names())
    if not set(data['tables'])<=known:raise ValueError('Inicialize todas as tabelas do snapshot antes de restaurar.')
    with db.engine.begin() as connection:
        if any(connection.execute(text('SELECT COUNT(*) FROM `'+name+'`')).scalar() for name in known):
            raise ValueError('Restauração exige banco vazio; nenhum dado existente foi alterado.')
        for name,_ in inspector.get_sorted_table_and_fkc_names():
            if not name or name not in data['tables']:continue
            columns={c['name'] for c in inspector.get_columns(name)}
            for row in data['tables'][name]:
                if not set(row)<=columns:raise ValueError('Colunas incompatíveis no snapshot.')
                values={key:(datetime.fromisoformat(value['datetime']) if isinstance(value,dict) and 'datetime'in value else Decimal(value['decimal']) if isinstance(value,dict) and 'decimal'in value else value) for key,value in row.items()}
                if name=='sessao_autenticacao':values['revogada']=True
                sql='INSERT INTO `'+name+'` ('+','.join('`'+key+'`' for key in values)+') VALUES ('+','.join(':'+key for key in values)+')'
                connection.execute(text(sql),values)
