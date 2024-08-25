import ast
from flaskforge.utils.io import StandardIO


class ImportModifier(ast.NodeTransformer):
    """
    AST Node Transformer for modifying import statements in Python code.

    This class can add new import statements to a module, or extend existing import statements with additional imports.

    Args:
        new_imports (str): New import statements to be added. Can be a single line or multiple lines.
        **kwargs: Additional arguments to control behavior.
            - extend (bool): Whether to extend existing imports (default: False).
            - module (str): The module to extend imports for (required if extend=True).

    Example Usage:
        ```python
        import ast

        source_code = '''
        import os
        import sys
        '''

        new_imports = 'from datetime import datetime'

        # Create an instance of ImportModifier
        tree = ast.parse(source_code)
        modifier = ImportModifier(new_imports, extend=False)
        modified_tree = modifier.visit(tree)

        # Convert AST back to source code
        modified_source_code = ast.unparse(modified_tree)
        print(modified_source_code)
        ```

    TODO:
        - Support more complex import scenarios, such as multi-line imports or imports from submodules.
        - Add functionality to handle import statements that span multiple lines.
        - Improve error handling for cases where `new_imports` cannot be parsed or is invalid.
    """

    io = StandardIO()

    def __init__(self, new_imports: str, **kwargs):
        """
        Initializes the ImportModifier with the new import statements and optional parameters.

        Args:
            new_imports (str): The new import statements to be added or extended.
            **kwargs: Additional arguments to control the behavior of the modifier.
                - extend (bool): Whether to extend existing imports.
                - module (str): The module to extend imports for.
        """
        self.new_imports = new_imports
        self.extend = kwargs.get("extend", False)
        self.extend_module = kwargs.get("module")
        self.modified_ = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        Visit and modify the import statements in the module.

        Args:
            node (ast.Module): The module node to be visited and modified.

        Returns:
            ast.Module: The modified module node with updated import statements.
        """
        imports = [
            stmt for stmt in node.body if isinstance(stmt, (ast.Import, ast.ImportFrom))
        ]

        if self.extend and imports and self.extend_module:
            for import_ in imports:
                if not import_.module == self.extend_module:
                    continue
                exist_name = [alias.name for alias in import_.names]
                import_.names += [
                    ast.alias(name=i) for i in self.new_imports if i not in exist_name
                ]
                self.modified_ = True
                break  # Append once and break

        if not self.modified_:
            try:
                self.new_imports = (
                    f"""from {self.extend_module} import {",".join(self.new_imports)}"""
                    if self.extend
                    else self.new_imports
                )
                new_imports_ast = ast.parse(self.new_imports).body
                imports.extend(new_imports_ast)
            except SyntaxError:
                self.io.print(f"Invalid import block: {self.new_imports}")

        other_statements = [
            stmt
            for stmt in node.body
            if not isinstance(stmt, (ast.Import, ast.ImportFrom))
        ]

        node.body = imports + other_statements

        return node
