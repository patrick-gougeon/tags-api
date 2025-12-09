from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
import os

from models import db
from resources import Especialidades, Especialidade

load_dotenv()

app = Flask(__name__)

# Configuração
USUARIO = os.getenv('DB_USUARIO')
SENHA = os.getenv('DB_SENHA')
HOST = os.getenv('DB_HOST')
BANCO = os.getenv('DB_NOME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}/{BANCO}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do Banco
db.init_app(app) 

api = Api(app)

# Rotas
api.add_resource(Especialidades, '/api/especialidades/') 
api.add_resource(Especialidade, '/api/especialidades/<int:id>')

@app.route('/')
def home():
    return '<h1>Upload de Tags API</h1>'

if __name__ == '__main__':
    with app.app_context():
        from models import EspecialidadeModel, MedicoModel, CirurgiaModel, ResponsavelModel, PlanoModel
        db.create_all()
        print("Banco de dados conectado e tabelas verificadas.")
    
    app.run(debug=True)