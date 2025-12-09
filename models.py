from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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