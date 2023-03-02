from typing import List, Optional, Tuple, Union

from pydantic import root_validator

from ethpm_types.base import BaseModel
from ethpm_types.sourcemap import SourceMapItem

SourceLocation = Tuple[int, int, int, int]


class ASTNode(BaseModel):
    ast_type: str
    """
    The type of AST node this is, such as ``FunctionDef``.
    """

    doc_str: Optional[Union[str, "ASTNode"]] = None
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
    def line_numbers(self) -> SourceLocation:
        """
        The values needed for constructing the line numbers for this node
        in the form ``[lineno, col_offset, end_lineno, end_col_offset]``.
        """

        return self.lineno, self.col_offset, self.end_lineno, self.end_col_offset

    @property
    def functions(self) -> List["ASTNode"]:
        """
        All function nodes defined at this level.

        **NOTE**: This is only populated on a ``Module`` AST node.
        """

        return [n for n in self.children if n.ast_type == "FunctionDef"]

    def get_node(self, src: SourceMapItem) -> Optional["ASTNode"]:
        """
        Get a node by source.

        Args:
            src (:class:`~ethpm_types.sourcemap.SourceMapItem`): The source map
              item to seek in the AST.

        Returns:
            Optional[``ASTNode``]: The matching node, if found, else ``None``.
        """

        if self.src.start == src.start and self.src.length == src.length:
            return self

        for child in self.children:
            node = child.get_node(src)
            if node:
                return node

        return None

    def get_nodes_at_line(self, line_numbers: SourceLocation) -> List["ASTNode"]:
        """
        Get the AST nodes for the given line number combination

        Args:
            line_numbers (``SourceLocation``): A tuple in the form of
              [lineno, col_offset, end_lineno, end_col_offset].

        Returns:
            List[``ASTNode``]: All matching nodes.
        """

        nodes = []
        if len(line_numbers) != 4:
            raise ValueError(
                "Line numbers should be given in form of "
                "`(lineno, col_offset, end_lineno, end_coloffset)`"
            )

        if all(x == y for x, y in zip(self.line_numbers, line_numbers)):
            nodes.append(self)

        for child in self.children:
            subs = child.get_nodes_at_line(line_numbers)
            nodes.extend(subs)

        return nodes

    def get_defining_function(self, line_numbers: SourceLocation) -> Optional["ASTNode"]:
        """
        Get the function that defines the given line numbers.

        Args:
            line_numbers (``SourceLocation``): A tuple in the form of
              [lineno, col_offset, end_lineno, end_col_offset].

        Returns:
            Optional[``ASTNode``]: The function definition AST node if found,
              else ``None``.
        """

        for function in self.functions:
            if function.get_nodes_at_line(line_numbers):
                return function

        return None
