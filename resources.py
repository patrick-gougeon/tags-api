from flask_restful import Resource, reqparse, fields, marshal_with, abort
from models import *

# --- Parsers ---
especialidade_args = reqparse.RequestParser()
especialidade_args.add_argument('nome', type=str, required=True, help="Nome é obrigatório")
especialidade_args.add_argument('descricao', type=str)

busca_args = reqparse.RequestParser()
busca_args.add_argument('page', type=int, default=1, location='args')
busca_args.add_argument('per_page', type=int, default=10, location='args')

# --- Fields ---
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

# --- Resources ---
class Especialidades(Resource):
    @marshal_with(paginacao_fields)
    def get(self):
        args = busca_args.parse_args()
        pagination = EspecialidadeModel.query.paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
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
        especialidade = EspecialidadeModel.query.get(id) 
        if not especialidade: abort(404, message='Especialidade não existe.')
        return especialidade
    
    @marshal_with(especialidade_fields)
    def put(self, id):
        args = especialidade_args.parse_args()
        especialidade = EspecialidadeModel.query.get(id)
        if not especialidade: abort(404, message='Especialidade não existe.')
        especialidade.nome = args['nome']
        especialidade.descricao = args['descricao']
        db.session.commit()
        return especialidade 

    def delete(self, id):
        especialidade = EspecialidadeModel.query.get(id)
        if not especialidade: abort(404, message='Especialidade não existe.')
        db.session.delete(especialidade)
        db.session.commit()
        return '', 204
