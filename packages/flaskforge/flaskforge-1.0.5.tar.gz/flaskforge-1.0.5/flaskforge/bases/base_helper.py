from logging import Logger
from functools import wraps

from inflect import engine
from flask import request, abort
from stringcase import camelcase, snakecase
from flask_jwt_extended import verify_jwt_in_request
from marshmallow import fields, Schema, ValidationError


def get_query_class(schema_cls: type) -> type:
    """
    Generates a new Schema class for query parameters based on the provided Marshmallow schema class.

    This function creates a new Schema class with fields derived from the given `schema_cls`.
    It converts field names to camelCase, excludes nested fields, and sets all fields to be
    non-required. If a field is a nested schema, it flattens the nested fields and also sets
    those fields to be non-required.

    Args:
        schema_cls (type): A Marshmallow schema class.

    Returns:
        type: A new Schema class for query parameters.
    """
    # Instantiate the schema class to access its fields
    instance = schema_cls()

    # Extract fields and convert their names to camelCase, excluding nested fields
    fields_ = {
        camelcase(k): v
        for k, v in instance.fields.items()
        if not isinstance(v, fields.Nested)
    }

    # Extract and flatten fields from nested schemas, converting field names to camelCase
    fields_.update(
        {
            camelcase(f"{attr}_{f}"): v
            for attr, nf in instance.fields.items()
            if isinstance(nf, fields.Nested)
            for f, v in nf.schema.fields.items()
            if not isinstance(v, fields.Nested)
        }
    )

    # Create a dictionary of modified fields where all fields are set to be non-required
    modified_field = {
        k: (lambda v: (setattr(v, "required", False), v)[1])(v)
        for k, v in fields_.items()
    }

    # Dynamically create and return a new Schema class with the modified fields
    return type(
        f"{instance.__class__.__name__.replace('Schema', '')}Query",
        (Schema,),
        {
            **modified_field,
            "page": fields.Int(default=1, allow_none=False),
            "perPage": fields.Int(default=10, allow_none=False),
        },
    )


def create_response_schema(schema_cls: type):
    p = engine()
    return type(
        "ResponseSchema",
        (Schema,),
        {
            f"""{
                p.plural(snakecase(schema_cls.__name__.replace("Schema", "")))
                }""": fields.Nested(
                schema_cls, many=True, attribute="items"
            ),
            "page": fields.Int(),
            "perPerage": fields.Int(attribute="per_page"),
            "totalRecords": fields.Int(attribute="total_records"),
        },
    )


def logger(name="IAM", filename="errors.log"):
    """instantiate new log class
    param   name        String  string log name
    param   filename    String  log filename
    return  Logger      Logger  Logger class
    """
    return Logger(name).get_logger(filename)


def validator(Schema, *ma_args, **ma_kwargs):

    def decorator(func):

        data = request.json if func.__name__ != "get" else request.args.to_dict()

        schema = Schema(*ma_args, **ma_kwargs)

        try:

            data_dict = schema.load(data)

        except ValidationError as err:
            print(err)
            abort(400)

        except Exception:
            abort(500)

            return {"message": "415 Unsupported Media Type"}
            """
                TODO:
                    1) should implment login so we track error on production
                    2) we should error to communication channel so we easier to debug
                    3) ....
            """

        @wraps(func)
        def inner(*args, **kwargs):
            pagination = {
                snakecase(k): int(v)
                for k, v in request.args.to_dict().items()
                if k in ["page", "perPage"]
            }

            return (
                func(data_dict, *args, **kwargs)
                if request.method != "GET"
                else func(data_dict, pagination, *args, **kwargs)
            )

        return inner

    return decorator


def authenticate(*auth_args, **auth_kwargs):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        return wrapper

    if len(auth_args) == 1 and callable(auth_args[0]):
        fn = auth_args[0]
        return decorator(fn)
    return decorator
