import ast


class AssignmentModifier(ast.NodeTransformer):
    def __init__(self, target_variable, new_value_str):
        self.target_variable = target_variable
        self.new_value_str = new_value_str
        self.new_value = self._parse_new_value(new_value_str)

    def _parse_new_value(self, value_str):
        """
        Parse the new value string into an AST node.
        """
        try:
            # `ast.parse` with mode='eval' to handle expressions
            node = ast.parse(value_str, mode="eval").body
            if not isinstance(
                node, (ast.Expression, ast.Attribute, ast.Name, ast.Dict, ast.Call)
            ):
                raise ValueError("Invalid new value format")
            return node
        except (SyntaxError, ValueError) as e:
            raise ValueError(f"Invalid new value syntax: {e}")

    def visit_Assign(self, node):
        # Check if the assignment is to the target variable
        if (
            isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == self.target_variable
        ):
            # Replace the value with the new value
            node.value = self.new_value
        return node
