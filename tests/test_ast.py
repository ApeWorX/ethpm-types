from ethpm_types import SourceMapItem
from ethpm_types.ast import ASTNode

AST_JSON = {
    "ast_type": "Module",
    "body": [
        {
            "args": {
                "args": [],
                "ast_type": "arguments",
                "col_offset": 0,
                "default": None,
                "defaults": [],
                "end_col_offset": 3,
                "end_lineno": 3,
                "lineno": 3,
                "node_id": 2,
                "src": "16:3:0",
            },
            "ast_type": "FunctionDef",
            "body": [
                {
                    "ast_type": "Return",
                    "col_offset": 4,
                    "end_col_offset": 14,
                    "end_lineno": 4,
                    "lineno": 4,
                    "node_id": 3,
                    "src": "51:10:0",
                    "value": {
                        "ast_type": "Int",
                        "col_offset": 11,
                        "end_col_offset": 14,
                        "end_lineno": 4,
                        "lineno": 4,
                        "node_id": 4,
                        "src": "58:3:0",
                        "value": 123,
                    },
                }
            ],
            "col_offset": 0,
            "decorator_list": [
                {
                    "ast_type": "Name",
                    "col_offset": 1,
                    "end_col_offset": 5,
                    "end_lineno": 1,
                    "id": "view",
                    "lineno": 1,
                    "node_id": 5,
                    "src": "1:4:0",
                },
                {
                    "ast_type": "Name",
                    "col_offset": 1,
                    "end_col_offset": 9,
                    "end_lineno": 2,
                    "id": "external",
                    "lineno": 2,
                    "node_id": 7,
                    "src": "7:8:0",
                },
            ],
            "doc_string": None,
            "end_col_offset": 14,
            "end_lineno": 4,
            "lineno": 3,
            "name": "read_stuff_2",
            "node_id": 1,
            "pos": None,
            "returns": {
                "ast_type": "Name",
                "col_offset": 22,
                "end_col_offset": 29,
                "end_lineno": 3,
                "id": "uint256",
                "lineno": 3,
                "node_id": 9,
                "src": "38:7:0",
            },
            "src": "16:45:0",
        }
    ],
    "col_offset": 0,
    "doc_string": None,
    "end_col_offset": 14,
    "end_lineno": 4,
    "lineno": 1,
    "name": "Dependency.vy",
    "node_id": 0,
    "src": "0:61:0",
}


def test_ast():
    node = ASTNode.parse_obj(AST_JSON)
    assert len(node.statements) == 8

    idx = SourceMapItem.parse_str("16:45:0")
    stmt = node.get_statement(idx)
    assert stmt.ast_type == "FunctionDef"
    assert stmt.pcmap == (3, 0, 4, 14)
