from flask_restful import Resource, reqparse, fields, marshal, abort
from models import *

# --- Resources genéricos ---
# Essa parte do código define classes genéricas pai, que serão
# posteriormente herdadas pelas classes Medico, Especialidade, Plano etc...

# Resource que representa o endpoint que retorna todas as tags do tipo selecionado
class DefaultsResource(Resource):
    
    # Atributos genéricos (serão alterados nas classes específicas)
    default_fields = None
    model = None
    default_args = None
    
    # Argumentos de paginação
    busca_args = reqparse.RequestParser()
    busca_args.add_argument('page', type=int, default=1, location='args')
    busca_args.add_argument('per_page', type=int, default=10, location='args')
    busca_args.add_argument('search', type=str, location='args')

    # GET
    def get(self):
        
        # Fields de paginação
        paginacao_fields = {
        'pagina_atual': fields.Integer,
        'total_paginas': fields.Integer,
        'total_itens': fields.Integer,
        'itens': fields.List(fields.Nested(self.default_fields)) 
        }
        
        # Processa os parâmetros do request.
        args = self.busca_args.parse_args()
         
        # Sistema de pesquisa no DB
        prompt = args['search']
        if prompt is not None:
            model_query = self.model.query.filter(self.model.nome.like(f'%{prompt}%'))
        else:
            model_query = self.model.query
        
         # Recebe e utiliza os valores de paginação na query
        # (paginate() é um método padrão do flask que facilita este processo).    
        pagination = model_query.paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )
        
        # Estabelece as informações que serão retornadas ao usuário.
        data = {
            'pagina_atual': pagination.page,
            'total_paginas': pagination.pages,
            'total_itens': pagination.total,
            'itens': pagination.items
        }
        
        # Usa os fields como molde pra formatação da resposta.
        return marshal(data, paginacao_fields)
    
    # POST
    def post(self):
        # Processa os parâmetros do usuário.
        args = self.default_args.parse_args()
        
        # Utiliza os argumentos processados pra criar uma nova tag.
        nova_instancia = self.model(**args)
        
        # Tenta armazenar a tag no DB.
        try:
            db.session.add(nova_instancia)
            db.session.commit() 
            
            # Usa os fields como molde pra formatação da resposta.
            return marshal(nova_instancia, self.default_fields), 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Erro ao salvar no banco', 'error': str(e)}, 500

# Resource que representa o endpoint que retorna uma tag em específico, selecionada por ID
class DefaultResource(Resource):
    
    # Atributos genéricos (serão alterados nas classes específicas)
    default_fields = None
    model = None
    default_args = None
    
    # GET
    def get(self, id):
        
        # Busca pela tag com o id passado nos argumentos do request.
        default = self.model.query.get(id)
        
        # Tratamento caso a tag não exista no DB
        if not default: abort(404, message='Tag não existe.')
        
        # Usa os fields como molde pra formatação da resposta.
        return marshal(default, self.default_fields)
    
    # PATCH (Update total ou parcial)
    def patch(self, id):
        
        # Processa os parâmetros do usuário.
        args = self.default_args.parse_args()
        
        # Busca pela tag com o id passado nos argumentos do request.
        default = self.model.query.get(id)
        
        # Tratamento caso a tag não exista no DB
        if not default: abort(404, message='Tag não existe.')
        
        # Itera sobre os argumentos do request, atualizando a tag no processo.
        for key, value in args.items():
            if value is not None:
                setattr(default, key, value)
        
        # Tenta atualizar o DB.
        try:
            db.session.commit()
            
            # Usa os fields como molde pra formatação da resposta.
            return marshal(default, self.default_fields)
        except Exception as e:
            db.session.rollback()
            return {'erro': f'Erro interno: {str(e)}'}, 500

    def delete(self, id):
        
        # Busca pela tag com o id passado nos argumentos do request.
        default = self.model.query.get(id)
        
        # Tratamento caso a tag não exista no DB
        if not default: abort(404, message='Tag não existe.')
        
        # Tenta deletar a tag no DB.
        try:
            db.session.delete(default)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'erro': f'Erro interno: {str(e)}'}, 500

# --- Resources específicos ---
# Essa parte do código define de fato os resources concretos 
# da API, com suas características e especificidades.

# Resources especialidade

# Parser
especialidade_args = reqparse.RequestParser()
especialidade_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
especialidade_args.add_argument('descricao', type=str)
especialidade_args.add_argument('ativo', type=bool)

# Fields
especialidade_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'descricao': fields.String,
    'ativo': fields.Boolean
}

class Especialidades(DefaultsResource):
    default_fields = especialidade_fields
    model = EspecialidadeModel
    default_args = especialidade_args
    
class Especialidade(DefaultResource):
    default_fields = especialidade_fields
    model = EspecialidadeModel
    default_args = especialidade_args
    
# Resources responsável

# Parser
responsavel_args = reqparse.RequestParser()
responsavel_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
responsavel_args.add_argument('email', type=str)
responsavel_args.add_argument('telefone', type=str)
responsavel_args.add_argument('pacientes', type=int)
responsavel_args.add_argument('ativo', type=bool)

# Fields
responsavel_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'email': fields.String,
    'telefone': fields.String,
    'pacientes': fields.Integer,
    'ativo': fields.Boolean
}

class Responsaveis(DefaultsResource):
    default_fields = responsavel_fields
    model = ResponsavelModel
    default_args = responsavel_args
    
class Responsavel(DefaultResource):
    default_fields = responsavel_fields
    model = ResponsavelModel
    default_args = responsavel_args
    
# Resources médico

# Parser
medico_args = reqparse.RequestParser()
medico_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
medico_args.add_argument('tipo', type=str, required=True, help="Tipo é obrigatório")
medico_args.add_argument('id_especialidade', type=int)
medico_args.add_argument('pacientes', type=int)
medico_args.add_argument('ativo', type=bool)

# Fields
medico_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'tipo': fields.String,
    'especialidade': fields.String(attribute='especialidade.nome'),
    'pacientes': fields.Integer,
    'ativo': fields.Boolean
}

class Medicos(DefaultsResource):
    default_fields = medico_fields
    model = MedicoModel
    default_args = medico_args
    
class Medico(DefaultResource):
    default_fields = medico_fields
    model = MedicoModel
    default_args = medico_args
    
# Resources cirurgia

# Parser
cirurgia_args = reqparse.RequestParser()
cirurgia_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
cirurgia_args.add_argument('id_especialidade', type=int)
cirurgia_args.add_argument('ativo', type=bool)

# Fields
cirurgia_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'especialidade': fields.String(attribute='especialidade.nome'),
    'ativo': fields.Boolean
}

class Cirurgias(DefaultsResource):
    default_fields = cirurgia_fields
    model = CirurgiaModel
    default_args = cirurgia_args
    
class Cirurgia(DefaultResource):
    default_fields = cirurgia_fields
    model = CirurgiaModel
    default_args = cirurgia_args
    
# Resources plano

# Parser
plano_args = reqparse.RequestParser()
plano_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
plano_args.add_argument('sigla', type=str)
plano_args.add_argument('pacientes', type=int)
plano_args.add_argument('ativo', type=bool)

# Fields
plano_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'sigla': fields.String,
    'pacientes': fields.Integer,
    'ativo': fields.Boolean
}

class Planos(DefaultsResource):
    default_fields = plano_fields
    model = PlanoModel
    default_args = plano_args
    
class Plano(DefaultResource):
    default_fields = plano_fields
    model = PlanoModel
    default_args = plano_args