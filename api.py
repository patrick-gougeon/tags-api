from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

USUARIO = os.getenv('DB_USUARIO')
SENHA = os.getenv('DB_SENHA')
HOST = os.getenv('DB_HOST')
BANCO = os.getenv('DB_NOME')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}/{BANCO}'

db = SQLAlchemy(app)

class Especialidade(db.Model):
    __tablename__ = 'especialidade'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    medicos = db.relationship('Medico', backref='especialidade')
    cirurgias = db.relationship('Cirurgia', backref='especialidade')

class Cirurgia(db.Model):
    __tablename__ = 'cirurgia'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    
    id_especialidade = db.Column(db.Integer, db.ForeigKey('especialidade.id'))

class Medico(db.Model):
    __tablename__ = 'medico'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100))

    id_especialidade = db.Column(db.Integer, db.ForeigKey('especialidade.id')) 
    
class Responsavel(db.Model):
    __tablename__ = 'responsavel'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Plano(db.Model):
    __tablename__ = 'plano'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

if __name__ == '__main__':
    app.run(debug=True)