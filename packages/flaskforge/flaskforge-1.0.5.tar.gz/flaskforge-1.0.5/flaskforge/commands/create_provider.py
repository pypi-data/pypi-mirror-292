import os
import re
from datetime import datetime

from stringcase import snakecase, pascalcase
from flaskforge.writers.writer_factory import WriterFactory
from flaskforge.builders.builder_factory import BuilderFactory
from flaskforge.utils.commons import join_path, exec_command
from flaskforge.utils.exception import (
    KoExit,
    OkExit,
    DoneExit,
    HintExit,
    UnCommitError,
    CancelExit,
    InvalidAttr,
    BreakAndExit,
)

from .base_cli_provider import AbstractProvider


class CreateProvider(AbstractProvider):
    """
    Provides functionality to interactively create and customize database settings.

    TODO:
        - Add support for multiple data types beyond the currently defined ones.
        - Implement a mechanism for saving and loading settings from a configuration file.
        - Add more comprehensive error handling and validation for user inputs.
    """

    continue_relationship = False

    def enter_setting(self, attr: dict = None, fields: list = None, data: str = None):
        """
        Display a customized database setting prompt and handle user input.

        Args:
            attr (dict, optional): Dictionary of attributes to update. Defaults to an empty dict if not provided.
            fields (list, optional): List of field settings. Defaults to an empty list if not provided.
            data (str, optional): Optional data to pre-fill the field settings. If not provided, prompts user input.

        TODO:
            - Allow users to specify default values for fields.
            - Implement a feature to suggest possible field settings based on existing attributes.
        """
        if attr is None:
            attr = {}
        if fields is None:
            fields = []

        try:
            attr_length = len(attr)
            example = list(self.AVAILABLE_ARGS.keys())[attr_length]
            hint = self.AVAILABLE_ARGS.get(example, {}).get("hint", "")
            factory = BuilderFactory(
                input(
                    f"""\n\tEnter your field setting (use hint arguments) {
                        self.io.color(self.io.CYAN, "~" * 3 + ">>")} """
                )
                if data is None
                else data
            )
            factory_builder = factory.get_builder()
            build_key = factory_builder.build()
            attr.update({build_key: factory_builder})

        except HintExit as err:
            self.io.print(err)

        except OkExit as err:
            self.io.clear()
            self.io.info(
                "Please review your column settings and confirm with <yes>", end="\n"
            )

            # Print the current settings
            temp = fields + [attr]
            for f in temp:
                self.io.print(self.get_field_str(f), color=self.io.GREEN)

            requires = set(
                [k for k, v in self.AVAILABLE_ARGS.items() if v.get("required")]
            )
            current = set(attr.keys())

            # Validate required fields
            if len(current) < len(requires):
                missing_fields = ",".join(list(requires - current))
                raise InvalidAttr(
                    f"Please complete all required fields (required: {self.io.color(self.io.RED, missing_fields)})\n"
                )

            # Confirm field settings
            if self.io.confirm("Please confirm your model field") != "yes":
                raise CancelExit("Operation canceled by user.")

            fields.append(attr)
            self.io.success(f"{str(err)}")

            self.io.clear()

            # Prompt to continue adding fields
            if self.io.confirm("Would you like to continue adding fields?") == "no":
                raise DoneExit

            raise KoExit

    def setup_relationship(self, args):
        self.io.clear()
        model_classname = pascalcase(f"{args.model}_model")
        models = [
            pascalcase(model.replace(".py", ""))
            for model in os.listdir(join_path(self.project_path, "models"))
            if not model.startswith("__")
            and "_to_" not in model
            and model != "base_model.py"
            and model != f"{snakecase(args.model)}_model.py"
        ]

        if not models:
            raise BreakAndExit("No existing model found in the model directory.")

        if (
            not self.continue_relationship
            and self.io.confirm(
                f"Would you like to add relationships for <{model_classname}>?"
            )
            != "yes"
        ):
            raise BreakAndExit("User canceled relationship creation.")

        self.io.clear()
        self.io.info(f"Please pick a relationship for <{model_classname}>")

        self.io.print_choice(models)

        choice = int(self.io.choice(len(models)))

        self.io.clear()

        self.io.info(
            f"Please choose a relation type between {pascalcase(args.model + '_model')} and {models[choice]}"
        )

        choosed_model = models[choice]

        relationships = [
            # A model can have zero or one of the specified related model.
            # This implies an optional one-to-one relationship.
            f"""{model_classname} has zero or one {choosed_model} {
                self.io.color(self.io.CYAN, "(OnetoOne)")}""",
            # A model has exactly one of the specified related model.
            # This implies a required one-to-one relationship.
            f"""{model_classname} has only one {choosed_model} {
                self.io.color(self.io.CYAN, "(OnetoOne)")}""",
            # A model can have zero or many of the specified related model.
            # This implies an optional one-to-many relationship.
            f"""{model_classname} has zero or many {choosed_model} {
                self.io.color(self.io.CYAN, "(OnetoMany)")}""",
            # A model must have at least one of the specified related model.
            # This implies a required one-to-many relationship.
            f"""{model_classname} has at least one {choosed_model} {
                self.io.color(self.io.CYAN, "(OnetoMany)")}""",
            # A model can belong to zero or one of the specified related model.
            # This implies an optional one-to-one relationship.
            f"""{model_classname} belongs to zero or one {choosed_model} {
                self.io.color(self.io.CYAN, "(OneToOne)")}""",
            # A model must belong to exactly one of the specified related model.
            # This implies a required one-to-one relationship.
            f"""{model_classname} belongs to only one {choosed_model} {
                self.io.color(self.io.CYAN, "(OneToOne)")}""",
            # A model can belong to zero or many of the specified related model.
            # This implies an optional one-to-many relationship.
            f"""{model_classname} belongs to zero or many {choosed_model} {
                self.io.color(self.io.CYAN, "(OnetoMany)")}""",
            # A model must belong to at least one of the specified related model. T
            # his implies a required one-to-many relationship.
            f"""{model_classname} belongs to at least one {choosed_model} {
                self.io.color(self.io.CYAN, "(OnetoMany)")}""",
            # Both models can have many of each other.
            # This implies a many-to-many relationship.
            f"""{model_classname} and {choosed_model} has many of each others {
                self.io.color(self.io.CYAN, "(ManytoMany)")}""",
        ]

        self.io.print_choice(relationships)

        relation_choice = self.io.choice(len(relationships))

        writer = WriterFactory(
            "relationship",
            args,
            strategy=relation_choice,
            child_model=models[choice],
        )
        writer.write_source()

    def handler(self, args):
        """
        Handle the entire process of setting up models and relationships.

        Args:
            args (object): Command-line arguments.

        TODO:
            - Add functionality to handle different project structures or configurations.
            - Implement a way to preview the final output before writing to files.
            - Enhance user prompts and messages for better clarity and guidance.
        """
        # Verify runner.py file existence
        self.runner_path = join_path(self.project_path, "runner.py")

        if not os.path.isfile(self.runner_path):
            raise ValueError(
                f"""Could not find runner.py in the current working directory.\n
Please run {self.io.color(self.io.CYAN, "flaskforge initapp")} first"""
            )

        if not args.force and exec_command("git status --porcelain") != "":
            raise UnCommitError("Please commit your code before exec command!")

        fields = []
        attr = {}

        while True:
            try:
                self.enter_setting(attr, fields)
            except InvalidAttr as err:
                self.io.clear()
                self.io.print("\n")
                self.io.error(f"{str(err)}")

            except CancelExit:
                self.io.clear()
                self.io.info(
                    f"Please update your field settings and confirm with {self.io.color(self.io.CYAN, '<yes>')} when done."
                )

            except KoExit:
                self.io.clear()
                attr = {}

            except DoneExit as err:
                # Finalize and write everything
                self.io.clear()

                writers = ["model", "schema", "resource", "route", "swagger"]
                for writer in writers:
                    WriterFactory(writer, args, fields=fields).write_source()

                self.io.success(str(err))
                break

        while True:
            try:
                self.setup_relationship(args)

            except BreakAndExit:
                break  # No action needed, continue

            except DoneExit as err:
                self.io.clear()
                if (
                    self.io.confirm(
                        f"""{str(err)
                    }. Would you to add more relationship?"""
                    )
                    == "yes"
                ):
                    self.continue_relationship = True
                    continue

                break  # exit relationship setup

        try:
            with open(self.runner_path, "r") as reader:
                source_runner = reader.read()

                # Check for blueprint registration
                pattern = r"app\.register_blueprint"
                if not re.search(pattern, source_runner) and not args.model_only:
                    if "yes" == self.io.confirm(
                        "Would you like to register endpoints for blueprints and swaggers?"
                    ):
                        writer = WriterFactory("register", args)
                        writer.write_source()

        except Exception as err:
            self.io.error(str(err))

        confirm_init = False
        now = datetime.now()
        # Format the timestamp as YYYY_MM_DD_HH_MM_SS
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        msg = snakecase(f"{timestamp} create {args.model} table")
        use_docker = os.path.isfile(join_path(self.project_path, "Dockerfile"))

        if (
            not os.path.isfile(join_path(self.project_path, "alembic.ini"))
            and self.io.confirm("Would like to init migration") == "yes"
        ):
            exec_command(
                f"""{"docker exec -it api " if use_docker else ""}alembic init migration"""
            )

            writer = WriterFactory("migration", args)
            writer.args.use_docker = use_docker
            writer.write_source()

            # Run migration once
            exec_command(
                f"""{"docker exec -it api " if use_docker else ""
                }alembic revision --autogenerate --message '{msg}'"""
            )
            exec_command(
                f"""{"docker exec -it api " if use_docker else ""}alembic upgrade head"""
            )
            confirm_init = True

        if (
            not confirm_init
            and self.io.confirm("Would you like to execute alembic migrate?") == "yes"
        ):

            exec_command(
                f"""{"docker exec -it api " if use_docker else ""
                }alembic revision --autogenerate --message '{msg}'"""
            )
            exec_command(
                f"""{"docker exec -it api " if use_docker else ""}alembic upgrade head"""
            )
