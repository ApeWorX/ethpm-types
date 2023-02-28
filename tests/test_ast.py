from ethpm_types import SourceMapItem
from ethpm_types.ast import ASTNode

AST_JSON = {
    "ast_type": "Module",
    "body": [
        {
            "alias": None,
            "ast_type": "ImportFrom",
            "col_offset": 0,
            "end_col_offset": 34,
            "end_lineno": 3,
            "level": 0,
            "lineno": 3,
            "module": "vyper.interfaces",
            "name": "ERC20",
            "node_id": 1,
            "src": "18:34:0",
        },
        {
            "args": {
                "args": [
                    {
                        "annotation": {
                            "ast_type": "Name",
                            "col_offset": 19,
                            "end_col_offset": 26,
                            "end_lineno": 6,
                            "id": "uint256",
                            "lineno": 6,
                            "node_id": 6,
                            "src": "83:7:0",
                        },
                        "arg": "num",
                        "ast_type": "arg",
                        "col_offset": 14,
                        "end_col_offset": 26,
                        "end_lineno": 6,
                        "lineno": 6,
                        "node_id": 5,
                        "src": "78:12:0",
                    }
                ],
                "ast_type": "arguments",
                "col_offset": 14,
                "default": None,
                "defaults": [],
                "end_col_offset": 26,
                "end_lineno": 6,
                "lineno": 6,
                "node_id": 4,
                "src": "78:12:0",
            },
            "ast_type": "FunctionDef",
            "body": [
                {
                    "ast_type": "Assert",
                    "col_offset": 4,
                    "end_col_offset": 19,
                    "end_lineno": 7,
                    "lineno": 7,
                    "msg": None,
                    "node_id": 8,
                    "src": "97:15:0",
                    "test": {
                        "ast_type": "Compare",
                        "col_offset": 11,
                        "end_col_offset": 19,
                        "end_lineno": 7,
                        "left": {
                            "ast_type": "Name",
                            "col_offset": 11,
                            "end_col_offset": 14,
                            "end_lineno": 7,
                            "id": "num",
                            "lineno": 7,
                            "node_id": 10,
                            "src": "104:3:0",
                        },
                        "lineno": 7,
                        "node_id": 9,
                        "op": {
                            "ast_type": "NotEq",
                            "col_offset": 11,
                            "end_col_offset": 19,
                            "end_lineno": 7,
                            "lineno": 7,
                            "node_id": 12,
                            "src": "104:8:0",
                        },
                        "right": {
                            "ast_type": "Int",
                            "col_offset": 18,
                            "end_col_offset": 19,
                            "end_lineno": 7,
                            "lineno": 7,
                            "node_id": 13,
                            "src": "111:1:0",
                            "value": 5,
                        },
                        "src": "104:8:0",
                    },
                }
            ],
            "col_offset": 0,
            "decorator_list": [
                {
                    "ast_type": "Name",
                    "col_offset": 1,
                    "end_col_offset": 9,
                    "end_lineno": 5,
                    "id": "external",
                    "lineno": 5,
                    "node_id": 14,
                    "src": "55:8:0",
                }
            ],
            "doc_string": None,
            "end_col_offset": 19,
            "end_lineno": 7,
            "lineno": 6,
            "name": "setNumber",
            "node_id": 3,
            "pos": None,
            "returns": None,
            "src": "64:48:0",
        },
    ],
    "col_offset": 0,
    "doc_string": None,
    "end_col_offset": 19,
    "end_lineno": 7,
    "lineno": 1,
    "name": "contract.vy",
    "node_id": 0,
    "src": "0:112:0",
}


def test_ast():
    node = ASTNode.parse_obj(AST_JSON)
    idx = SourceMapItem.parse_str("104:8:0")
    stmt = node.get_node(idx)
    stmts = node.get_nodes_at_line((6, 14, 6, 26))
    funcs = node.functions
    assert stmt.ast_type == "Compare"
    assert stmt.line_numbers == (7, 11, 7, 19)
    assert len(stmts) == 2
    assert stmts[0].ast_type == "arguments"
    assert stmts[1].ast_type == "arg"
    assert len(funcs) == 1
    assert node.get_defining_function((7, 11, 7, 14)) == funcs[0]
    assert node.get_defining_function([7, 11, 7, 14]) == funcs[0]
    assert node.get_defining_function((55, 11, 56, 14)) is None
