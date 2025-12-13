from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
import os

from models import db
from resources import *

load_dotenv()

app = Flask(__name__)


# --- INÍCIO DA NOVA CONFIGURAÇÃO ---
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Verifica qual tipo de banco está definido no arquivo .env
db_tipo = os.getenv('DB_TIPO', 'sqlite') # Padrão é sqlite se não encontrar nada

if db_tipo == 'sqlite':
    print("--- Usando Banco de Dados: SQLite (Local) ---")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'banco_teste.db')

else:
    print("--- Usando Banco de Dados: MySQL (Empresa) ---")
    USUARIO = os.getenv('DB_USUARIO')
    SENHA = os.getenv('DB_SENHA')
    HOST = os.getenv('DB_HOST')
    BANCO = os.getenv('DB_NOME')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}/{BANCO}'
    
# --- FIM DA NOVA CONFIGURAÇÃO ---

db.init_app(app) 

# Inicialização da Apiz
api = Api(app)

# Rotas
api.add_resource(Especialidades, '/api/especialidades') 
api.add_resource(Especialidade, '/api/especialidades/<int:id>')

api.add_resource(Responsaveis, '/api/responsaveis') 
api.add_resource(Responsavel, '/api/responsaveis/<int:id>')

api.add_resource(Medicos, '/api/medicos') 
api.add_resource(Medico, '/api/medicos/<int:id>')

api.add_resource(Cirurgias, '/api/cirurgias') 
api.add_resource(Cirurgia, '/api/cirurgias/<int:id>')

api.add_resource(Planos, '/api/planos') 
api.add_resource(Plano, '/api/planos/<int:id>')

api.add_resource(UploadDados, '/api/upload')

# Rota da home
@app.route('/')
def home():
    return '<h1>Upload de Tags API</h1>'


# Main
if __name__ == '__main__':
    with app.app_context():
        from models import EspecialidadeModel, MedicoModel, CirurgiaModel, ResponsavelModel, PlanoModel
        # db.create_all() garante que as tabelas sejam criadas se não existirem.
        # Para um ambiente de produção, é recomendado usar uma ferramenta de migração
        # como o Flask-Migrate para gerenciar mudanças no esquema do banco de dados.
        db.create_all()
        print("Banco de dados conectado e tabelas verificadas.")
    
    app.run(debug=True)