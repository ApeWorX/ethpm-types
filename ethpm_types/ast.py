from typing import List, Optional, Tuple

from pydantic import root_validator

from ethpm_types.base import BaseModel
from ethpm_types.sourcemap import SourceMapItem


class ASTNode(BaseModel):
    ast_type: str
    """
    The type of AST node this is, such as ``FunctionDef``.
    """

    doc_str: Optional[str] = None
    """
    Documentation for the node.
    """

    src: SourceMapItem
    """
    The source offset item.
    """

    lineno: int
    """
    The start line number in the source.
    """

    end_lineno: int
    """
    The line number where the AST node ends.
    """

    col_offset: int
    """
    The offset of the column start.
    """

    end_col_offset: int
    """
    The offset when the column ends.
    """

    children: List["ASTNode"] = []
    """
    All sub-AST nodes within this one.
    """

    @root_validator(pre=True)
    def validate_src(cls, val):
        src = val.get("src")
        if src and isinstance(src, str):
            src = SourceMapItem.parse_str(src)

        children = []
        for value in val.values():
            if isinstance(value, dict) and "ast_type" in value:
                child = ASTNode.parse_obj(value)
                children.append(child)
            elif isinstance(value, list):
                for _val in value:
                    if isinstance(_val, dict) and "ast_type" in _val:
                        child = ASTNode.parse_obj(_val)
                        children.append(child)

        return {
            "doc_str": val.get("doc_string"),
            "children": children,
            **val,
            "src": src,
        }

    @property
    def pcmap(self) -> Tuple[int, int, int, int]:
        """
        The values needed for constructing the PCMap for this node.
        """

        return self.lineno, self.col_offset, self.end_lineno, self.end_col_offset

    @property
    def statements(self):
        """
        All children nodes, flattened to a list.
        """

        stmts: List["ASTNode"] = [self]
        for child in self.children:
            stmts.extend(child.statements)

        return stmts

    def get_statement(self, src: SourceMapItem) -> "ASTNode":
        matches = [
            s for s in self.statements if src.start == s.src.start and src.length == s.src.length
        ]
        if len(matches) == 1:
            return matches[0]

        raise IndexError("Unable to find exact statement.")
