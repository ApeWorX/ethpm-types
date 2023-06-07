import pytest

from ethpm_types import SourceMapItem
from ethpm_types.ast import ASTNode

VYPER_AST_JSON = {
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
                            "src": "111:0:0",
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
SOLIDITY_AST_JSON = {
    "absolutePath": "Imports.sol",
    "exportedSymbols": {
        "BrownieContract": [10],
        "BrownieStyleDependency": [21],
        "Depend": [68],
        "Depend2": [73],
        "Imports": [91],
        "MissingPragma": [101],
        "MyStruct": [56],
        "Relativecontract": [153],
        "Struct0": [108],
        "Struct1": [113],
        "Struct2": [118],
        "Struct3": [123],
        "Struct4": [128],
        "Struct5": [133],
    },
    "id": 92,
    "license": "MIT",
    "nodeType": "SourceUnit",
    "nodes": [
        {
            "id": 67,
            "literals": ["solidity", "^", "0.8", ".4"],
            "nodeType": "PragmaDirective",
            "src": "33:23:5",
        },
        {
            "absolutePath": ".cache/TestDependency/local/Dependency.sol",
            "file": "@remapping/contracts/Dependency.sol",
            "id": 68,
            "nameLocation": "70:6:5",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 39,
            "src": "58:62:5",
            "symbolAliases": [],
            "unitAlias": "Depend",
        },
        {
            "absolutePath": "MissingPragma.sol",
            "file": "./MissingPragma.sol",
            "id": 69,
            "nameLocation": "-1:-1:-1",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 102,
            "src": "121:101:5",
            "symbolAliases": [],
            "unitAlias": "",
        },
        {
            "absolutePath": "CompilesOnce.sol",
            "file": "CompilesOnce.sol",
            "id": 71,
            "nameLocation": "-1:-1:-1",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 66,
            "src": "223:44:5",
            "symbolAliases": [
                {
                    "foreign": {
                        "id": 70,
                        "name": "MyStruct",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 56,
                        "src": "232:8:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                }
            ],
            "unitAlias": "",
        },
        {
            "absolutePath": "subfolder/Relativecontract.sol",
            "file": "./subfolder/Relativecontract.sol",
            "id": 72,
            "nameLocation": "-1:-1:-1",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 154,
            "src": "268:42:5",
            "symbolAliases": [],
            "unitAlias": "",
        },
        {
            "absolutePath": ".cache/TestDependency/local/Dependency.sol",
            "file": "@remapping_2/Dependency.sol",
            "id": 73,
            "nameLocation": "351:7:5",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 39,
            "src": "311:48:5",
            "symbolAliases": [],
            "unitAlias": "Depend2",
        },
        {
            "absolutePath": ".cache/BrownieDependency/local/BrownieContract.sol",
            "file": "@remapping_2_brownie/BrownieContract.sol",
            "id": 74,
            "nameLocation": "-1:-1:-1",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 11,
            "src": "360:50:5",
            "symbolAliases": [],
            "unitAlias": "",
        },
        {
            "absolutePath": "NumerousDefinitions.sol",
            "file": "./NumerousDefinitions.sol",
            "id": 81,
            "nameLocation": "-1:-1:-1",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 143,
            "src": "411:121:5",
            "symbolAliases": [
                {
                    "foreign": {
                        "id": 75,
                        "name": "Struct0",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 108,
                        "src": "424:7:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                },
                {
                    "foreign": {
                        "id": 76,
                        "name": "Struct1",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 113,
                        "src": "437:7:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                },
                {
                    "foreign": {
                        "id": 77,
                        "name": "Struct2",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 118,
                        "src": "450:7:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                },
                {
                    "foreign": {
                        "id": 78,
                        "name": "Struct3",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 123,
                        "src": "463:7:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                },
                {
                    "foreign": {
                        "id": 79,
                        "name": "Struct4",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 128,
                        "src": "476:7:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                },
                {
                    "foreign": {
                        "id": 80,
                        "name": "Struct5",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 133,
                        "src": "489:7:5",
                        "typeDescriptions": {},
                    },
                    "nameLocation": "-1:-1:-1",
                },
            ],
            "unitAlias": "",
        },
        {
            "absolutePath": ".cache/BrownieStyleDependency/local/BrownieStyleDependency.sol",
            "file": "@styleofbrownie/BrownieStyleDependency.sol",
            "id": 82,
            "nameLocation": "-1:-1:-1",
            "nodeType": "ImportDirective",
            "scope": 92,
            "sourceUnit": 22,
            "src": "533:52:5",
            "symbolAliases": [],
            "unitAlias": "",
        },
        {
            "abstract": False,
            "baseContracts": [],
            "canonicalName": "Imports",
            "contractDependencies": [],
            "contractKind": "contract",
            "fullyImplemented": True,
            "id": 91,
            "linearizedBaseContracts": [91],
            "name": "Imports",
            "nameLocation": "596:7:5",
            "nodeType": "ContractDefinition",
            "nodes": [
                {
                    "body": {
                        "id": 89,
                        "nodeType": "Block",
                        "src": "651:28:5",
                        "statements": [
                            {
                                "expression": {
                                    "hexValue": "74727565",
                                    "id": 87,
                                    "isConstant": False,
                                    "isLValue": False,
                                    "isPure": True,
                                    "kind": "bool",
                                    "lValueRequested": False,
                                    "nodeType": "Literal",
                                    "src": "668:4:5",
                                    "typeDescriptions": {
                                        "typeIdentifier": "t_bool",
                                        "typeString": "bool",
                                    },
                                    "value": "true",
                                },
                                "functionReturnParameters": 86,
                                "id": 88,
                                "nodeType": "Return",
                                "src": "661:11:5",
                            }
                        ],
                    },
                    "functionSelector": "c2985578",
                    "id": 90,
                    "implemented": True,
                    "kind": "function",
                    "modifiers": [],
                    "name": "foo",
                    "nameLocation": "619:3:5",
                    "nodeType": "FunctionDefinition",
                    "parameters": {
                        "id": 83,
                        "nodeType": "ParameterList",
                        "parameters": [],
                        "src": "622:2:5",
                    },
                    "returnParameters": {
                        "id": 86,
                        "nodeType": "ParameterList",
                        "parameters": [
                            {
                                "constant": False,
                                "id": 85,
                                "mutability": "mutable",
                                "name": "",
                                "nameLocation": "-1:-1:-1",
                                "nodeType": "VariableDeclaration",
                                "scope": 90,
                                "src": "645:4:5",
                                "stateVariable": False,
                                "storageLocation": "default",
                                "typeDescriptions": {
                                    "typeIdentifier": "t_bool",
                                    "typeString": "bool",
                                },
                                "typeName": {
                                    "id": 84,
                                    "name": "bool",
                                    "nodeType": "ElementaryTypeName",
                                    "src": "645:4:5",
                                    "typeDescriptions": {
                                        "typeIdentifier": "t_bool",
                                        "typeString": "bool",
                                    },
                                },
                                "visibility": "internal",
                            }
                        ],
                        "src": "644:6:5",
                    },
                    "scope": 91,
                    "src": "610:69:5",
                    "stateMutability": "pure",
                    "virtual": False,
                    "visibility": "public",
                }
            ],
            "scope": 92,
            "src": "587:94:5",
            "usedErrors": [],
            "usedEvents": [],
        },
    ],
    "src": "33:649:5",
}


def test_vy_ast():
    node = ASTNode.parse_obj(VYPER_AST_JSON)
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
    assert funcs[0].name == "setNumber"
    assert node.get_defining_function((7, 11, 7, 14)) == funcs[0]
    assert node.get_defining_function([7, 11, 7, 14]) == funcs[0]
    assert node.get_defining_function((55, 11, 56, 14)) is None


def test_sol_ast():
    node = ASTNode.parse_obj(SOLIDITY_AST_JSON)
    assert node.ast_type == "SourceUnit"
    assert len(node.children) == 10


@pytest.mark.parametrize("length", (0, None))
def test_ast_get_node_no_length(length):
    node = ASTNode.parse_obj(VYPER_AST_JSON)
    idx = SourceMapItem(start=111, length=length, contract_id=None, jump_code="-")
    actual = node.get_node(idx)
    assert actual.ast_type == "Int"
