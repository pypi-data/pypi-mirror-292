import ast
from copy import copy

import astor
from stringcase import pascalcase
from flaskforge.writers.writer_factory import WriterFactory
from flaskforge.modifiers import MethodModifier, ImportModifier, AssignmentModifier

from .base_cli_provider import AbstractProvider


class CreateAuthentication(AbstractProvider):
    def handler(self, args: object):
        self.args = copy(args)
        self.args.model_only = False
        self.args.only = [self.args.username_field, self.args.password_field]
        self.args.endpoints = ["get", "post", "delete"]

        self.args.name = "authentication"
        classname = pascalcase(f"{self.args.name}_resource")
        writer = WriterFactory("resource", self.args)
        writer.set_writable("authentication")

        signin = """
def post(self, schema: dict):
        model = self.model(schema)
        model.signin()
        user = model.jsonify()
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        response = make_response(
            {"access_token": access_token, "refresh_token": refresh_token,}, 200,
        )

        set_access_cookies(response, access_token)

        return response
"""

        signout = """
def delete(self, schema: dict = dict()):

    respone = make_response({"message": "Signout success"}, 200)

    unset_access_cookies(respone)

    return respone
"""

        verify = """
def get(self):

    user=get_jwt_identity()
    
    model = self.model()
    
    model.get(user)
    
    return make_response(model.jsonify(), 200)  
"""
        method_decorators = f"""{{"post": [validator(UserSchema, only=("{
            self.args.username_field}", "{self.args.password_field
            }"))],"delete": [authenticate], "get": [authenticate,]}}"""
        source = writer.get_source()

        tree = ast.parse(source)
        tree = MethodModifier(classname, verify, True).visit(tree)
        tree = MethodModifier(classname, signin, True).visit(tree)
        tree = MethodModifier(classname, signout, True).visit(tree)
        tree = AssignmentModifier("method_decorators", method_decorators).visit(tree)
        tree = ImportModifier(
            ["authenticate"], module="utils.helper", extend=True
        ).visit(tree)
        tree = ImportModifier(
            [
                "get_jwt_identity",
                "set_access_cookies",
                "create_access_token",
                "create_refresh_token",
                "unset_access_cookies",
            ],
            module="flask_jwt_extended",
            extend=True,
        ).visit(tree)

        writer.set_source(astor.to_source(tree))
        writer.write_source()

        writer = WriterFactory("model", args)
        source = writer.read()

        getter_method = f"""
def __setattr__(self, key, value):
    is_hashed = isinstance(value, str) and len(value) == 60 and value.startswith(('$2b$', '$2a$', '$2y$'))
    if key == "{args.password_field}" and not is_hashed:
        value = hashpw(value.encode("utf-8"), gensalt()).decode("utf-8")

    super({pascalcase(f"{args.model}_model")}, self).__setattr__(key, value)
"""

        verify_method = f"""
def verify(self):
    if not checkpw(self.schema["{args.password_field}"].encode("utf-8"), self.__temp__.{args.password_field}.encode("utf-8")):
        raise Forbidden(f"{{self.username}}:{{self.{args.password_field}}} - Invalid credentials")

"""

        signin_method = f"""
def signin(self):
    self.get({{{f"'{self.args.username_field}': getattr(self, '{self.args.username_field}')"}}})
    self.verify()
"""

        tree = ast.parse(source)
        tree = ImportModifier(
            ["hashpw", "gensalt", "checkpw"], module="bcrypt", extend=True
        ).visit(tree)
        tree = ImportModifier(
            ["Forbidden"], module="werkzeug.exceptions", extend=True
        ).visit(tree)
        tree = MethodModifier(f"{writer.classname}", getter_method).visit(tree)
        tree = MethodModifier(f"{writer.classname}", verify_method).visit(tree)
        tree = MethodModifier(f"{writer.classname}", signin_method).visit(tree)
        writer.set_source(astor.to_source(tree))
        writer.write_source()

        for type in ["route", "swagger"]:
            writer = WriterFactory(type, self.args)
            writer.set_writable("authentication")
            writer.write_source()
