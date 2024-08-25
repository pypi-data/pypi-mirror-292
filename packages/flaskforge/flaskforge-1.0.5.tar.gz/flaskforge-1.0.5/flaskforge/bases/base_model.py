from os import environ
from math import ceil

from stringcase import snakecase
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func, create_engine
from sqlalchemy.orm import (
    Query,
    class_mapper,
    sessionmaker,
    scoped_session,
    RelationshipProperty,
    ColumnProperty,
)
from sqlalchemy.exc import SQLAlchemyError

from utils.helper import create_response_schema


class Paginate:
    def __init__(self, page, per_page, total, items) -> None:
        self.page = page
        self.per_page = per_page
        self.total_records = total
        self.total_pages = ceil(total / per_page)
        self.items = items


class BaseQuery(Query):
    def paginate(self, page=None, per_page=None, count=True):
        """get paginate
        param   self        BaseQuery   BaseQuery class
        param   page        Int         page
        param   per_page    Int         per page
        param   count       Int         count
        return  items       List        Lits of pagiaate
        """

        page = page if page else 1

        per_page = per_page if per_page else 10

        items = (
            self.limit(per_page).offset((page - 1) * per_page).all()
            if page > 0
            else self.all()
        )

        total = self.order_by(None).count() if count else None

        return Paginate(page, per_page, total, items) if page != -1 else items


engine = create_engine(
    "postgresql://{db_username}:{db_pwd}@db/{db_name}".format(
        db_username=environ.get("POSTGRES_USER"),
        db_pwd=environ.get("POSTGRES_PASSWORD"),
        db_name=environ.get("POSTGRES_DB"),
    )
)

session = scoped_session(
    sessionmaker(
        bind=engine,
        query_cls=BaseQuery,
        pool_size=environ.get("SQLALCHEMY_POOL_SIZE", 10),
        max_overflow=environ.get("SQLALCHEMY_MAX_OVERFLOW", 10),
        pool_timeout=environ.get("SQLALCHEMY_POOL_TIMEOUT", 30),
    )
)
Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    __temp__ = None

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), index=True)

    def __init__(self, schema: dict = {}):
        self.schema = schema
        self._session = session
        self.mapper = class_mapper(self.__class__)

        for attr in self.mapper.attrs:
            # skip none sqlalchemy attributes
            if not isinstance(attr, (RelationshipProperty, ColumnProperty)):
                continue

            if isinstance(attr, ColumnProperty):
                column = attr.columns[0].name
                if self.schema.get(column):
                    setattr(self, column, self.schema[column])
                continue

            if not self.schema.get(attr.key):
                continue

            if self.id is not None and f"{self.__class__.__tablename__}_id" not in [
                f.key
                for f in attr.mapper.attrs
                if isinstance(f, ColumnProperty) and f.columns[0].foreign_keys
            ]:
                continue

            child_model = attr.mapper.class_

            child = (
                [child_model(c) for c in self.schema[attr.key]]
                if attr.uselist
                else child_model(self.schema[attr.key])
            )

            setattr(self, attr.key, child)

    def get_query(self, expression: dict, **kwargs):
        q = self._session.query(self.__class__)

        for attr in self.mapper.attrs:
            if not isinstance(attr, ColumnProperty):
                continue

            column = attr.columns[0]
            if column.name not in expression.keys():
                continue

            q = (
                q.filter(column.contains(expression.get(column.name)))
                if kwargs.get("search") and issubclass(column.type.python_type, str)
                else q.filter(column == expression.get(column.name))
            )

        for k, m in self.mapper.relationships.items():
            if not expression.get(k):
                continue

            q = (
                q.join(m.mapper.class_)
                if m.secondary is None
                else q.join(m.secondary).join(m.mapper.class_)
            )

            for attr in m.mapper.attrs:
                if not isinstance(attr, ColumnProperty):
                    continue
                column = attr.columns[0]

                if column.name not in (
                    expression[k].keys()
                    if isinstance(expression[k], dict)
                    else expression[k][0].keys()
                ):
                    continue

                parameter = (
                    expression[k][0]
                    if isinstance(expression[k], list)
                    else expression[k]
                )

                q = (
                    q.filter(column.contains(parameter[column.name]))
                    if kwargs.get("search") and isinstance(column.type.python_type, str)
                    else q.filter(column == parameter[column.name])
                )

        return q

    def get(self, expression: dict):
        self.__temp__ = self.get_query(expression).one()

    def get_all(self, expression: dict, pagination: dict) -> list:

        self.__temp__ = self.get_query(expression).paginate(**pagination)

        return self.__temp__

    def search(self, expression: dict, pagination: dict):
        self.__temp__ = self.get_query(expression, search=True).paginate(**pagination)

    def add(self) -> None:

        self._session.add(self)
        self.commit_()

    def update(self):
        model = (
            self._session.query(self.__class__)
            .filter(self.__class__.id == self.schema["id"])
            .one()
        )

        for attr in self.mapper.attrs:
            # skip not SQLAlchemy properties
            if not isinstance(attr, (ColumnProperty, RelationshipProperty)):
                continue

            # update commons fields
            if isinstance(attr, ColumnProperty):
                # skip not
                if getattr(self, attr.key) is None:
                    continue

                setattr(model, attr.key, getattr(self, attr.key))
                continue

            # update relationship
            if hasattr(attr, "uselist") and attr.uselist:
                ids = [m.id for m in getattr(self, attr.key) if m.id is not None]
                setattr(
                    model,
                    attr.key,
                    list(
                        filter(
                            lambda x: x.id in ids or x.id is None,
                            getattr(model, attr.key),
                        )
                    ),
                )

                self._session.flush()

            _ = (
                [self._session.merge(c) for c in getattr(self, attr.key)]
                if hasattr(attr, "uselist") and attr.uselist
                else (self._session.merge(getattr(self, attr.key)))
            )

        self.commit_()

        self.__temp__ = model

    def delete(self):
        if not self.id:
            raise AttributeError(f"Cannot delete NoneType of {self.__class__}")

        self._session.query(self.__class__).filter(
            self.__class__.id == self.id
        ).delete()
        self.commit_()

    def commit_(self):
        self._session.commit()

    def rollback(self):
        try:
            self._session.rollback()
        except SQLAlchemyError():
            ...

    def jsonify(self):
        data = self if self.__temp__ is None else self.__temp__

        Schema = (
            create_response_schema(self.Schema_)
            if not isinstance(data, self.__class__)
            else self.Schema_
        )

        schema = Schema()

        return schema.dump(data)
