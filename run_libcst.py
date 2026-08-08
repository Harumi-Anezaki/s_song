import os
import libcst as cst
from libcst.metadata import PositionProvider

class TypeAndDocstringAdder(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        changes = {}
        
        # Add return type hint if missing
        if not updated_node.returns and updated_node.name.value != '__init__':
            changes['returns'] = cst.Annotation(annotation=cst.Name("Any"))
            
        # Add docstring if missing
        body = updated_node.body.body
        has_docstring = False
        if body and isinstance(body[0], cst.SimpleStatementLine):
            stmt = body[0].body[0]
            if isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.SimpleString):
                has_docstring = True
                
        if not has_docstring:
            docstring = cst.SimpleStatementLine(
                body=[
                    cst.Expr(
                        value=cst.SimpleString(f'\"\"\"\n    {updated_node.name.value} function.\n    \"\"\"')
                    )
                ]
            )
            new_body = list(updated_node.body.body)
            new_body.insert(0, docstring)
            changes['body'] = updated_node.body.with_changes(body=new_body)
            
        # Add type hints to arguments if missing
        new_params = []
        for param in updated_node.params.params:
            if param.name.value != 'self' and not param.annotation:
                new_params.append(param.with_changes(annotation=cst.Annotation(annotation=cst.Name("Any"))))
            else:
                new_params.append(param)
        
        if new_params != list(updated_node.params.params):
            changes['params'] = updated_node.params.with_changes(params=new_params)
            
        if changes:
            return updated_node.with_changes(**changes)
            
        return updated_node

class ImportAdder(cst.CSTTransformer):
    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        # Check if 'from typing import Any' is present
        has_typing_any = False
        for stmt in updated_node.body:
            if isinstance(stmt, cst.SimpleStatementLine):
                for node in stmt.body:
                    if isinstance(node, cst.ImportFrom) and node.module and node.module.value == 'typing':
                        for name in node.names:
                            if name.name.value == 'Any':
                                has_typing_any = True
        
        if not has_typing_any:
            import_stmt = cst.parse_statement("from typing import Any\n")
            new_body = list(updated_node.body)
            
            # Insert after the first docstring if it exists, otherwise at the top
            insert_idx = 0
            if new_body and isinstance(new_body[0], cst.SimpleStatementLine) and isinstance(new_body[0].body[0], cst.Expr) and isinstance(new_body[0].body[0].value, cst.SimpleString):
                insert_idx = 1
                
            new_body.insert(insert_idx, import_stmt)
            return updated_node.with_changes(body=new_body)
            
        return updated_node

for root, _, files in os.walk('core'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            try:
                module = cst.parse_module(source)
                transformer = TypeAndDocstringAdder()
                modified_module = module.visit(transformer)
                
                # If we modified the module, add the typing import
                if modified_module.code != source:
                    import_transformer = ImportAdder()
                    modified_module = modified_module.visit(import_transformer)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(modified_module.code)
                    print(f"Updated {filepath}")
            except Exception as e:
                print(f"Failed to process {filepath}: {e}")
