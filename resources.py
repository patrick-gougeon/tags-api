from flask_restful import Resource, reqparse, fields, marshal, abort
from models import *

# --- Resources genérico ---
class DefaultResource(Resource):
    default_fields = None
    model = None
    default_args = None
    
    busca_args = reqparse.RequestParser()
    busca_args.add_argument('page', type=int, default=1, location='args')
    busca_args.add_argument('per_page', type=int, default=10, location='args')

    def get(self):
        paginacao_fields = {
        'pagina_atual': fields.Integer,
        'total_paginas': fields.Integer,
        'total_itens': fields.Integer,
        'itens': fields.List(fields.Nested(self.default_fields)) 
        }
        
        args = self.busca_args.parse_args()
        
        pagination = self.model.query.paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )
        
        data = {
            'pagina_atual': pagination.page,
            'total_paginas': pagination.pages,
            'total_itens': pagination.total,
            'itens': pagination.items
        }
        
        return marshal(data, paginacao_fields)
    
    def post(self):
        args = self.default_args.parse_args()
        nova_instancia = self.model(**args)
        try:
            db.session.add(nova_instancia)
            db.session.commit() 
            return marshal(nova_instancia, self.default_fields), 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Erro ao salvar no banco', 'error': str(e)}, 500
        
class DefaultsResource(Resource):
    default_fields = None
    model = None
    default_args = None
    
    def get(self, id):
        default = self.model.query.get(id) 
        if not default: abort(404, message='Tag não existe.')
        return marshal(default, self.default_fields)
    
    def patch(self, id):
        args = self.default_args.parse_args()
        default = self.model.query.get(id)
        if not default: abort(404, message='Tag não existe.')
        
        for key, value in args.items():
            if value is not None:
                setattr(default, key, value)
        
        try:
            db.session.commit()
            return marshal(default, self.default_fields)
        except Exception as e:
            db.session.rollback()
            return {'erro': f'Erro interno: {str(e)}'}, 500

    def delete(self, id):
        default = self.model.query.get(id)
        if not default: abort(404, message='Tag não existe.')
        
        try:
            db.session.delete(default)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'erro': f'Erro interno: {str(e)}'}, 500

# --- Resources Especialidade ---

# Parser
especialidade_args = reqparse.RequestParser()
especialidade_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
especialidade_args.add_argument('descricao', type=str)

# Fields
especialidade_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'descricao': fields.String
}

class Especialidades(DefaultsResource):
    default_fields = especialidade_fields
    model = EspecialidadeModel
    default_args = especialidade_args
    
class Especialidade(DefaultResource):
    default_fields = especialidade_fields
    model = EspecialidadeModel
    default_args = especialidade_args
    
# --- Resources responsável ---

# Parser
responsavel_args = reqparse.RequestParser()
responsavel_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
responsavel_args.add_argument('email', type=str)
responsavel_args.add_argument('telefone', type=str)

# Fields
responsavel_fields = {
    'id': fields.Integer,
    'nome': fields.String,
    'email': fields.String,
    'telefone': fields.String
}

class Responsaveis(DefaultsResource):
    default_fields = responsavel_fields
    model = ResponsavelModel
    default_args = responsavel_args
    
class Responsavel(DefaultResource):
    default_fields = responsavel_fields
    model = ResponsavelModel
    default_args = responsavel_args