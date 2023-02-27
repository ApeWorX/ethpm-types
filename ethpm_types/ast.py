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
    def line_numbers(self) -> Tuple[int, int, int, int]:
        """
        The values needed for constructing the line numbers for this node
        in the form ``[lineno, col_offset, end_lineno, end_col_offset]``.
        """

        return self.lineno, self.col_offset, self.end_lineno, self.end_col_offset

    def get_node(self, src: SourceMapItem) -> Optional["ASTNode"]:
        if self.src.start == src.start and self.src.length == src.length:
            return self

        for child in self.children:
            node = child.get_node(src)
            if node:
                return node

        return None

    def get_nodes_at_line(self, line_numbers: Tuple[int, int, int, int]) -> List["ASTNode"]:
        nodes = []
        if self.line_numbers == line_numbers:
            nodes.append(self)

        for child in self.children:
            subs = child.get_nodes_at_line(line_numbers)
            nodes.extend(subs)

        return nodes
