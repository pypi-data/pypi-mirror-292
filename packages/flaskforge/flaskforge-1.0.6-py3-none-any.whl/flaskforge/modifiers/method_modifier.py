import ast


class MethodModifier(ast.NodeTransformer):
    def __init__(self, class_name: str, source: str, replace=False):
        self.class_name = class_name
        self.new_method_source = source
        self.replace = replace

    def visit_ClassDef(self, node):
        # Check if the class name matches
        if node.name == self.class_name:
            # Parse the new method source to an AST node
            new_method_tree = ast.parse(self.new_method_source).body[0]
            # Check if the new method is a function definition
            if isinstance(new_method_tree, ast.FunctionDef):
                # Replace existing method or add new method
                method_name = new_method_tree.name
                method_exists = False
                for i, item in enumerate(node.body):
                    if isinstance(item, ast.FunctionDef) and item.name == method_name:
                        node.body[i] = new_method_tree
                        method_exists = True
                        break
                if not method_exists:
                    node.body.append(new_method_tree)
        return node
