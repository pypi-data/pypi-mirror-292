import re
import ast
import astor
from os import getenv, path

from yaml import load, Loader
from dotenv import load_dotenv
from flaskforge.utils.commons import join_path
from flaskforge.modifiers import ImportModifier, AssignmentModifier

from .base_writer import AbstractWriter


class MigrationWriter(AbstractWriter):
    type = "migration"

    def __init__(self, args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

        self.migration_path = join_path(self.project_root, "migration")
        self.env_py_path = join_path(self.migration_path, "env.py")
        self.alembic_ini_path = join_path(self.project_root, "alembic.ini")

    def read_source(self, path: str):
        with open(path, "r") as reader:
            return reader.read()

    def write_env(self):
        self.write(self.env_py_path, self.env_py)

    def write_alembic_ini(self):
        self.write(join_path(self.project_root, "alembic.ini"), self.alembic_ini)

    def write_source(self):
        self.get_source()

        self.write_env()

        self.write_alembic_ini()

    def get_source(self):

        load_dotenv(join_path(self.project_root, ".env"))

        env_py = self.read_source(join_path(self.migration_path, "env.py"))

        tree = ast.parse(env_py)
        tree = ImportModifier("from models import *").visit(tree)
        tree = ImportModifier("from models.base_model import Base").visit(tree)

        tree = AssignmentModifier("target_metadata", "Base.metadata").visit(tree)

        self.env_py = self.format(astor.to_source(tree))

        if (
            hasattr(self.args, "use_docker")
            and self.args.use_docker
            and path.isfile(join_path(self.package_root, "bases", "docker-compose.yml"))
        ):
            docker_compose = self.read(
                join_path(self.package_root, "bases", "docker-compose.yml")
            )
            environments = load(docker_compose, Loader=Loader)["services"]["db"][
                "environment"
            ]

            database_url = f"""postgresql://{environments["POSTGRES_USER"]}:{
                environments["POSTGRES_PASSWORD"]}@db/{environments["POSTGRES_DB"]}"""
        else:

            database_url = getenv("DATABASE_URL")

        alembic_ini = self.read_source(join_path(self.project_root, "alembic.ini"))

        # Define a regex pattern to find the sqlalchemy.url line
        pattern = r"^sqlalchemy.url\s*=\s*.*$"

        # Create a replacement line with the new URL
        replacement = f"sqlalchemy.url = {database_url}"

        # Replace the existing sqlalchemy.url line with the new one
        self.alembic_ini = re.sub(pattern, replacement, alembic_ini, flags=re.MULTILINE)
