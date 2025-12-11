from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Criando tabelas do DB
class EspecialidadeModel(db.Model):
    __tablename__ = 'especialidade'

    # Primary key que se auto-incrementa.
    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(500))
    ativo = db.Column(db.Boolean, default=True)


class CirurgiaModel(db.Model):
    __tablename__ = 'cirurgia'

    # Primary key que se auto-incrementa.
    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(100), unique=True, nullable=False)
    
    # Foreign key de especialidade
    id_especialidade = db.Column(db.Integer, db.ForeignKey('especialidade.id', ondelete='SET NULL'))
    ativo = db.Column(db.Boolean, default=True)
    
    especialidade = db.relationship('EspecialidadeModel')

class MedicoModel(db.Model):
    __tablename__ = 'medico'
    
    # Primary key que se auto-incrementa.
    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100))

    # Foreign key de especialidade
    id_especialidade = db.Column(db.Integer, db.ForeignKey('especialidade.id', ondelete='SET NULL')) 
    pacientes = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)
    
    especialidade = db.relationship('EspecialidadeModel')
    
class ResponsavelModel(db.Model):
    __tablename__ = 'responsavel'

    # Primary key que se auto-incrementa.
    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200))
    telefone = db.Column(db.String(50))
    pacientes = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)

class PlanoModel(db.Model):
    __tablename__ = 'plano'
    
    # Primary key que se auto-incrementa.
    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(100), unique=True, nullable=False)
    sigla = db.Column(db.String(10))
    pacientes = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)