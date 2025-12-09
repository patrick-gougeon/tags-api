from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
import os

from models import db
from resources import *

load_dotenv()

app = Flask(__name__)

# Configuração de conexão do DB
USUARIO = os.getenv('DB_USUARIO')
SENHA = os.getenv('DB_SENHA')
HOST = os.getenv('DB_HOST')
BANCO = os.getenv('DB_NOME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}/{BANCO}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do Banco
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

# Rota da home
@app.route('/')
def home():
    return '<h1>Upload de Tags API</h1>'


# Main
if __name__ == '__main__':
    with app.app_context():
        from models import EspecialidadeModel, MedicoModel, CirurgiaModel, ResponsavelModel, PlanoModel
        db.create_all()
        print("Banco de dados conectado e tabelas verificadas.")
    
    app.run(debug=True)