from flask import make_response, g
from flask_restful import Api, Resource


class Api(Api):
    def handle_error(self, err):

        # Rollback session on error
        model = g.__resource__.model()
        model.rollback()
        return make_response({"message": ""}, 500)


class BaseResource(Resource):
    nit_every_request = True

    def dispatch_request(self, *args, **kwargs):
        g.__resource__ = self
        return super().dispatch_request(*args, **kwargs)
