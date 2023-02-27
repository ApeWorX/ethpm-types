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

        def find_children(node):
            children = []

            def add_child(data):
                data["children"] = find_children(data)
                child = ASTNode.parse_obj(data)
                children.append(child)

            for value in node.values():
                if isinstance(value, dict) and "ast_type" in value:
                    add_child(value)

                elif isinstance(value, list):
                    for _val in value:
                        if isinstance(_val, dict) and "ast_type" in _val:
                            add_child(_val)

            return children

        return {
            "doc_str": val.get("doc_string"),
            "children": find_children(val),
            **val,
            "src": src,
        }

    @property
    def pcmap(self) -> Tuple[int, int, int, int]:
        """
        The values needed for constructing the PCMap for this node.
        """

        return self.lineno, self.col_offset, self.end_lineno, self.end_col_offset

    def get_statement(self, src: SourceMapItem) -> Optional["ASTNode"]:
        if self.src.start == src.start and self.src.length == src.length:
            return self

        for child in self.children:
            statement = child.get_statement(src)
            if statement:
                return statement

        return None
