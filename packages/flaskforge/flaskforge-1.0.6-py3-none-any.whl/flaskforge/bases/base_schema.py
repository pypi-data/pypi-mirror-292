from flask import request
from stringcase import camelcase, snakecase
from marshmallow import Schema, pre_load, post_dump, fields


class BaseSchema(Schema):
    @pre_load
    def to_snakecase(self, data, **kwargs):
        local_data = {snakecase(k): v for k, v in data.items()}
        if request.method == "GET":
            return {
                f: (
                    (
                        [
                            {
                                nf.replace(f"{f}_", ""): nv
                                for nf, nv in local_data.items()
                                if nf.startswith(f"{f}_")
                            }
                        ]
                        if v.schema.many
                        else {
                            nf.replace(f"{f}_", ""): nv
                            for nf, nv in local_data.items()
                            if nf.startswith(f"{f}_")
                        }
                    )
                    if isinstance(v, fields.Nested)
                    else local_data.get(f)
                )
                for f, v in self.fields.items()
                if local_data.get(f) or isinstance(v, fields.Nested)
            }

        return local_data

    @post_dump
    def to_camelcase(self, data, **kwargs):
        # return only require data
        if request.method == "PATCH":
            return {camelcase(k): v for k, v in data.items() if v is not None}

        return {camelcase(k): v for k, v in data.items()}
