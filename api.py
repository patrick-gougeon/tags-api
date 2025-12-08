from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
import os
from dotenv import load_dotenv

# Importando chaves etc
load_dotenv()

USUARIO = os.getenv('DB_USUARIO')
SENHA = os.getenv('DB_SENHA')
HOST = os.getenv('DB_HOST')
BANCO = os.getenv('DB_NOME')

# Configurações do flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}/{BANCO}'

db = SQLAlchemy(app)

api = Api(app)

# Criando tabelas do DB
class EspecialidadeModel(db.Model):
    __tablename__ = 'especialidade'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(500))
    
    medicos = db.relationship('MedicoModel', backref='especialidade')
    cirurgias = db.relationship('CirurgiaModel', backref='especialidade')

class CirurgiaModel(db.Model):
    __tablename__ = 'cirurgia'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    
    id_especialidade = db.Column(db.Integer, db.ForeignKey('especialidade.id', ondelete='SET NULL'))

class MedicoModel(db.Model):
    __tablename__ = 'medico'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100))

    id_especialidade = db.Column(db.Integer, db.ForeignKey('especialidade.id', ondelete='SET NULL')) 
    
class ResponsavelModel(db.Model):
    __tablename__ = 'responsavel'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200))
    telefone = db.Column(db.String(50))

class PlanoModel(db.Model):
    __tablename__ = 'plano'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    sigla = db.Column(db.String(10))

# Configurações da API

especialidade_args = reqparse.RequestParser()
especialidade_args.add_argument('nome', type=str, required=True, help="Nome é um campo obrigatório")
especialidade_args.add_argument('descricao', type=str)

busca_args = reqparse.RequestParser()
busca_args.add_argument('page', type=int, default=1, location='args', help="Página atual")
busca_args.add_argument('per_page', type=int, default=10, location='args', help="Itens por página")

especialidade_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'descricao': fields.String
}

paginacao_fields = {
    'pagina_atual': fields.Integer,
    'total_paginas': fields.Integer,
    'total_itens': fields.Integer,
    'itens': fields.List(fields.Nested(especialidade_fields)) 
}


class Especialidades(Resource):
    @marshal_with(paginacao_fields)
    def get(self):
        args = busca_args.parse_args()

        pagination = EspecialidadeModel.query.paginate(
            page=args['page'], 
            per_page=args['per_page'], 
            error_out=False
        )
        
        return {
            'pagina_atual': pagination.page,
            'total_paginas': pagination.pages,
            'total_itens': pagination.total,
            'itens': pagination.items
        }
    
    @marshal_with(especialidade_fields)
    def post(self):
        args = especialidade_args.parse_args()
        especialidade = EspecialidadeModel(nome=args['nome'], descricao=args['descricao'])
        db.session.add(especialidade)
        db.session.commit() 
        return especialidade, 201

class Especialidade(Resource):
    @marshal_with(especialidade_fields)
    def get(self, id):
        especialidade = EspecialidadeModel.query.filter_by(id=id).first() 
        if not especialidade:
           abort(404, 'Especialidade não existe.')
        return especialidade
    
    @marshal_with(especialidade_fields)
    def put(self, id):
        args = especialidade_args.parse_args()
        especialidade = EspecialidadeModel.query.filter_by(id=id).first()
        if not especialidade:
            abort(404, 'Especialidade não existe.') 
        especialidade.nome = args['nome']
        especialidade.descricao = args['descricao']
        db.session.commit()
        return especialidade 

    def delete(self, id):
        especialidade = EspecialidadeModel.query.filter_by(id=id).first()
        if not especialidade:
            abort(404, 'Especialidade não existe.')
        db.session.delete(especialidade)
        db.session.commit()
        especialidades = EspecialidadeModel.query.all()
        return '', 204 
        
api.add_resource(Especialidades, '/api/especialidades/') 
api.add_resource(Especialidade, '/api/especialidades/<int:id>')

# Endpoint da Home
@app.route('/')
def home():
    return '<h1>Tag upload API</h1>'

# Main
if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas se não existirem
        db.create_all()
        print("Banco de dados atualizado com sucesso!")
    
    app.run(debug=True)