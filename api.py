from flask import Blueprint
from flask_restful import Resource, Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class Medico(Resource):
    def get(self):
        return {'mensagem': 'testeaaaaaaaaaa'}

api.add_resource(Medico, '/medico')