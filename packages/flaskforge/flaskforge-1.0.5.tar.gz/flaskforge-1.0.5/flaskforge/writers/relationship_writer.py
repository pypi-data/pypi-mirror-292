import os
import sys
import ast
import astor
import inflect
from abc import ABC, abstractmethod
from stringcase import snakecase, pascalcase

from flaskforge.modifiers import ImportModifier, FieldModifier, MethodModifier
from flaskforge.utils.commons import join_path
from flaskforge.utils.exception import ModelNotFoud, DoneExit

from .base_writer import AbstractWriter
from .schema_writer import SchemaWriter


class AbstractStrategy(ABC):
    """
    Abstract base class for strategy patterns used in relationship writers.

    Provides common methods and attributes for managing model relationships in SQLAlchemy.
    Subclasses should implement specific strategies for different relationship types.

    Attributes:
        model_path (str): Path to the directory containing model files.
        args (object): Arguments object containing model details.
        model (str): Name of the model.
        child (str): Name of the child model.
        child_path (str): Path to the child model file.
        parent_path (str): Path to the parent model file.
    """

    model_path = join_path(os.getcwd(), "models")

    def __init__(self, args: object, kwargs: dict) -> None:
        """
        Initialize the strategy with model-specific details.

        Args:
            args (object): Arguments object containing model details.
            kwargs (dict): Additional keyword arguments including child model details.

        TODO:
            - Validate that `args` and `kwargs` contain necessary attributes.
            - Handle cases where `model_path` might not be accessible or does not exist.
        """
        self.args = args
        self.kwargs = kwargs
        self.relationship = int(kwargs["strategy"])

        # Reverse child and parent model if belongto relationship
        self.model = (
            snakecase(self.kwargs["child_model"]).replace("_model", "")
            if self.relationship >= 4 and self.relationship <= 7
            else self.args.model
        )
        self.child = (
            pascalcase(f"{self.args.model}_model")
            if self.relationship >= 4 and self.relationship <= 7
            else self.kwargs["child_model"]
        )

        self.only_relationship = self.relationship in (1, 3, 5, 7)

        self.append_model()
        self.set_writable()
        self.check_writable()

    @abstractmethod
    def modify_child(self): ...

    @abstractmethod
    def modify_parent(self): ...

    def get_child_source(
        self, unique: bool = False, primary: bool = False, required: bool = False
    ) -> str:
        """
        Generate source code for the child model.

        Args:
            unique (bool): Flag to determine if the field should be unique.

        Returns:
            str: The formatted source code for the child model.

        TODO:
            - Handle cases where `self.child_path` might be missing or inaccessible.
        """
        tree = self.modify_child_import(self.read_tree(self.child_path))
        tree = FieldModifier(
            self.get_foriegn_key_str(unique=unique, required=True)
        ).visit(tree)
        return astor.to_source(tree)

    def get_parent_source(self, field_name: str, unique: bool = False) -> str:
        """
        Generate source code for the parent model.

        Args:
            field_name (str): Name of the field to be used in the parent model.
            unique (bool): Flag to determine if the field should be unique.

        Returns:
            str: The formatted source code for the parent model.

        TODO:
            - Handle cases where `self.parent_path` might be missing or inaccessible.
        """
        tree = self.modify_parent_import(self.read_tree(self.parent_path))

        tree = FieldModifier(self.get_relationship_str(field_name, unique)).visit(tree)

        if self.only_relationship:

            # Define the new method with a variable
            new_method_code = f"""
@validates('{field_name}')
def validate_{field_name}(self, key, {field_name}):
    error_message = "A {self.model} must have at least one {
        snakecase(self.child.replace("Model", ""))}."
    if not {field_name}:
        raise ValueError(error_message)
    return {field_name}
"""
            tree = ImportModifier(
                ["validates"], extend=True, module="sqlalchemy.orm"
            ).visit(tree)
            tree = MethodModifier(
                pascalcase(f"{self.model}_model"), new_method_code
            ).visit(tree)

        return astor.to_source(tree)

    def append_model(self):
        """
        Append the model path to the system path if not already present.

        TODO:
            - Handle potential errors when appending to the system path.
        """
        if self.model_path not in sys.path:
            sys.path.append(self.model_path)

    def get_model_path(self, model: str) -> str:
        """
        Get the file path for a given model.

        Args:
            model (str): Name of the model.

        Returns:
            str: The file path of the model.

        TODO:
            - Validate that the model name is correctly formatted.
        """
        return join_path(self.model_path, f"{snakecase(model)}.py")

    def get_relationship_str(self, field: str, unique: bool = False) -> str:
        """
        Generate the relationship string for the parent model.

        Args:
            field (str): Name of the relationship field.
            unique (bool): Flag to determine if the relationship should be unique.

        Returns:
            str: The relationship string.

        TODO:
            - Validate the relationship string format.
        """
        return f"""{field} = relationship("{
            pascalcase(self.child)}", backref="{
                self.model}", uselist={not unique},cascade="all, delete-orphan")"""

    def get_foriegn_key_str(
        self,
        model: str = None,
        unique: bool = False,
        primary: bool = False,
        required=False,
    ) -> str:
        """
        Generate the foreign key string for a model.

        Args:
            model (str, optional): The model name for the foreign key. Defaults to `self.model`.
            unique (bool): Flag to determine if the foreign key should be unique.
            primary (bool): Flag to determine if the foreign key is a primary key.

        Returns:
            str: The foreign key string.

        TODO:
            - Validate the foreign key string format.
        """
        model_ = model if model else self.model

        return f"""{model_}_id = Column(Integer, ForeignKey("{
            model_}.id"), index=True{", unique=True" if unique else ""}{
                ",primary_key=True" if primary else ""}{
                    ", nullable=False" if required else ""})"""

    def modify_child_import(self, tree: object) -> object:
        """
        Modify import statements in the child model source code.

        Args:
            tree (object): The abstract syntax tree (AST) of the child model.

        Returns:
            object: The modified AST.

        TODO:
            - Handle cases where the import modifications may conflict with existing imports.
        """
        return ImportModifier(
            ["ForeignKey", "Integer"], extend=True, module="sqlalchemy"
        ).visit(tree)

    def modify_parent_import(self, tree: object) -> object:
        """
        Modify import statements in the parent model source code.

        Args:
            tree (object): The abstract syntax tree (AST) of the parent model.

        Returns:
            object: The modified AST.

        TODO:
            - Handle cases where the import modifications may conflict with existing imports.
        """
        return ImportModifier(
            ["relationship"], extend=True, module="sqlalchemy.orm"
        ).visit(tree)

    def read_tree(self, model_path: str) -> ast.AST:
        """
        Read and parse the source code of a model into an AST.

        Args:
            model_path (str): The file path of the model.

        Returns:
            ast.AST: The abstract syntax tree (AST) of the model.

        TODO:
            - Handle cases where the model file might be missing or inaccessible.
        """
        with open(model_path, "r") as reader:
            model_source = reader.read()

        return ast.parse(model_source)

    def set_writable(self):
        """
        Set the paths for the child and parent model files based on the model name.

        TODO:
            - Validate the paths to ensure they are correct and accessible.
        """
        self.child_path = self.get_model_path(self.child)
        self.parent_path = self.get_model_path(f"{self.model}Model")

    def check_writable(self):
        """
        Check if the child and parent model files exist and are valid.

        Raises:
            ModelNotFoud: If either model file is not found.

        TODO:
            - Handle potential exceptions when checking for model files.
        """
        self.is_model(self.child_path)
        self.is_model(self.parent_path)

    def is_model(self, model: str) -> bool:
        """
        Check if a given model file exists.

        Args:
            model (str): The file path of the model.

        Returns:
            bool: True if the model file exists, otherwise raises `ModelNotFoud`.

        Raises:
            ModelNotFoud: If the model file does not exist.

        TODO:
            - Improve error handling to provide more detailed feedback.
        """
        if not os.path.isfile(model):
            raise ModelNotFoud(f"Could not find {self.child} in {self.model_path}")

        return True


class OneToOneWriter(AbstractStrategy):
    """
    Strategy for writing one-to-one relationships.

    Inherits from `AbstractStrategy` and provides methods to modify child and parent models
    for one-to-one relationships.
    """

    def modify_child(self) -> str:
        """
        Modify the child model for a one-to-one relationship.

        Returns:
            str: The modified source code for the child model.
        """

        return self.get_child_source(unique=True, required=True)

    def modify_parent(self) -> str:
        """
        Modify the parent model for a one-to-one relationship.

        Returns:
            str: The modified source code for the parent model.
        """
        field_name = snakecase(self.child.replace("Model", ""))
        return self.get_parent_source(field_name, True)


class OnetoManyWriter(AbstractStrategy):
    """
    Strategy for writing one-to-many relationships.

    Inherits from `AbstractStrategy` and provides methods to modify child and parent models
    for one-to-many relationships.
    """

    def modify_child(self) -> str:
        """
        Modify the child model for a one-to-many relationship.

        Returns:
            str: The modified source code for the child model.
        """
        return self.get_child_source()

    def modify_parent(self) -> str:
        """
        Modify the parent model for a one-to-many relationship.

        Returns:
            str: The modified source code for the parent model.
        """
        p = inflect.engine()
        field_name = p.plural(snakecase(self.child.replace("Model", "")))
        return self.get_parent_source(field_name)


class ManyToManyWriter(AbstractStrategy):
    """
    Strategy for writing many-to-many relationships.

    Inherits from `AbstractStrategy` and provides methods to modify child and parent models
    for many-to-many relationships.
    """

    def modify_child(self) -> str:
        """
        Modify the child model for a many-to-many relationship.

        Returns:
            str: The modified source code for the child model.

        TODO:
            - Validate the secondary model class name and table name.
        """
        chid_field = snakecase(self.child.replace("Model", ""))

        parent_id = self.get_foriegn_key_str(primary=True)
        child_id = self.get_foriegn_key_str(chid_field, primary=True)

        classname = pascalcase(f"{self.model}_to_{chid_field}")
        self.secondary_name = snakecase(classname)

        secondary_source = f"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from .base_model import Base

class {classname}(Base):
    __tablename__ = "{self.secondary_name}"
    {parent_id}
    {child_id}
    UniqueConstraint("{self.model}_id", "{
        chid_field}_id", name="{self.model}_id_{chid_field}_id")
"""
        self.child_path = join_path(self.model_path, f"{self.secondary_name}.py")

        return secondary_source

    def modify_parent(self) -> str:
        """
        Modify the parent model for a many-to-many relationship.

        Returns:
            str: The modified source code for the parent model.

        TODO:
            - Ensure that the relationship field is correctly named and associated with the secondary table.
        """
        p = inflect.engine()
        field_name = p.plural(snakecase(self.child.replace("Model", "")))

        field_source = f"""{field_name} = relationship("{self.child}", secondary="{
            self.secondary_name}",backref="{p.plural(self.model)}")"""

        tree = ast.parse(self.get_parent_source(field_name))
        tree = FieldModifier(field_source).visit(tree)

        return astor.to_source(tree)


class RelationShipFactory:
    """
    Factory class for creating relationship writers based on strategy.

    Attributes:
        factorys (tuple): Tuple of strategy classes for different relationship types.
    """

    factorys = (OneToOneWriter, OnetoManyWriter, ManyToManyWriter)
    factory_pairs = [(0, 1, 4, 5), (2, 3, 6, 7), (8,)]

    def __new__(cls, factory: int) -> AbstractStrategy:
        """
        Create a new instance of the appropriate strategy class based on the given factory index.

        Args:
            factory (int): Index of the strategy class to be instantiated.

        Returns:
            AbstractStrategy: An instance of the selected strategy class.

        TODO:
            - Validate the factory index to ensure it is within range.
            - Handle cases where the strategy class might not be found.
        """
        strategy = next(
            (i for i, tpl in enumerate(cls.factory_pairs) if int(factory) in tpl), None
        )
        writer = cls.factorys[strategy]
        return writer


class RelationshipWriter(AbstractWriter):
    """
    Writer for managing model relationships using various strategies.

    Inherits from `AbstractWriter` and uses strategy patterns to generate relationship code
    and update model files accordingly.

    Attributes:
        type (str): The type of writer, set to "relationship".
        _strategy (AbstractStrategy): The strategy instance for managing relationships.
    """

    type = "relationship"
    _strategy = None

    def __init__(self, args: object, **kwargs):
        """
        Initialize the RelationshipWriter with model details and strategy.

        Args:
            args (object): Arguments object containing model details.
            **kwargs: Additional keyword arguments including strategy and child model details.

        TODO:
            - Validate the `args` and `kwargs` to ensure they contain necessary attributes.
            - Handle cases where strategy initialization might fail.
        """
        self.args = args
        self.kwargs = kwargs
        self.schema_writer = SchemaWriter(args, **kwargs)

        self._strategy = RelationShipFactory(kwargs["strategy"])(args, kwargs)

    def write_source(self):
        """
        Write the generated relationship code to the appropriate model files.

        Also writes schema information for nested relationships.

        TODO:
            - Implement error handling for file write operations.
            - Add logging to track the writing process and any potential issues.
        """
        self.get_source()
        self.write(self._strategy.child_path, self.child_source)
        self.write(self._strategy.parent_path, self.parent_source)

        self.schema_writer.write_nested()

        raise DoneExit("Relationship setup successfully")

    def get_source(self):
        """
        Generate and format the source code for child and parent models.

        Sets `self.child_source` and `self.parent_source` with the formatted source code
        generated by the strategy.

        TODO:
            - Handle cases where the generated source code might not be valid or complete.
        """
        self.child_source = self.format(self._strategy.modify_child())
        self.parent_source = self.format(self._strategy.modify_parent())
