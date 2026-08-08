import ast
import os
import sys

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    issues = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check docstring
            if not ast.get_docstring(node):
                issues.append(f"Missing docstring: {node.name}")
            
            # Check return type hint
            if not node.returns:
                if node.name != '__init__':
                    issues.append(f"Missing return type hint: {node.name}")
            
            # Check argument type hints
            for arg in node.args.args:
                if arg.arg != 'self' and not arg.annotation:
                    issues.append(f"Missing type hint for arg '{arg.arg}': {node.name}")
                    
    if issues:
        print(f"\n--- {filepath} ---")
        for i in issues:
            print(i)

for root, _, files in os.walk('core'):
    for file in files:
        if file.endswith('.py'):
            check_file(os.path.join(root, file))
