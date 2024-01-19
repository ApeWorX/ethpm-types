from enum import Enum
from functools import cached_property
from typing import Any, Iterator, List, Optional, Tuple, Union

from pydantic import RootModel, ValidationError, model_validator

from ethpm_types.sourcemap import SourceMapItem
from ethpm_types.utils import SourceLocation


class ASTClassification(Enum):
    UNCLASSIFIED = 0
    """Unclassified AST type (default)."""

    FUNCTION = 1
    """ASTTypes related to defining a function."""


class ASTNode(RootModel[dict]):
    """
    A model representing the AST (abstract-syntax tree) of a compiled contract.
    """

    _classification: ASTClassification = ASTClassification.UNCLASSIFIED
    _lazy_children: List["ASTNode"] = []
    _function_node_types: Tuple[str, ...]
    _ast_type_keys: Tuple[str, ...]

    @model_validator(mode="before")
    @classmethod
    def validate_ast(cls, values):
        fn_node_types = values.pop("function_node_types", ("FunctionDef",))
        ast_type_keys = values.pop("ast_type_keys", ("ast_type", "nodeType"))

        cls._function_node_types = fn_node_types
        cls._ast_type_keys = ast_type_keys

        for key in ast_type_keys:
            if ast_type := values.get(key):
                # Is a node!
                if ast_type in fn_node_types:
                    cls._classification = ASTClassification.FUNCTION

                return values

        raise ValidationError("Not a valid ASTNode.")

    @cached_property
    def ast_type(self) -> str:
        """
        The compiler-given AST node type, such as ``FunctionDef``.
        """
        for key in self._ast_type_keys:
            if itm := self.root.get(key):
                return itm

        # Shouldn't happen.
        raise ValueError("Missing AST type.")

    @property
    def children(self) -> Iterator["ASTNode"]:
        """
        All sub-AST nodes within this one.
        """
        if self._lazy_children:
            yield from self._lazy_children

        else:
            for val in self.root.values():
                yield from self.find_children(val)

    @property
    def classification(self) -> ASTClassification:
        """
        A generic classification of what type of AST this is.
        """
        return self._classification

    @property
    def col_offset(self) -> int:
        """
        The offset of the column start.
        """
        return self.root.get("col_offset", -1)

    @property
    def doc_str(self) -> Optional[Union[str, "ASTNode"]]:
        """
        Documentation for the node.
        """
        return self.root.get("doc_str", self.root.get("doc_string"))

    @property
    def end_col_offset(self) -> int:
        """
        The offset when the column ends.
        """
        return self.root.get("end_col_offset", -1)

    @property
    def end_lineno(self) -> int:
        """
        The line number where the AST node ends.
        """
        return self.root.get("end_lineno", -1)

    @property
    def lineno(self) -> int:
        """
        The start line number in the source.
        """
        return self.root.get("lineno", -1)

    @property
    def name(self) -> Optional[str]:
        """
        The node's name if it has one, such as a function name.
        """
        return self.root.get("name")

    @cached_property
    def src(self) -> SourceMapItem:
        """
        The source offset item.
        """
        raw_src = self.root["src"]
        return self._validate_src(raw_src)

    @classmethod
    def _validate_src(cls, val: str) -> SourceMapItem:
        if val and isinstance(val, str):
            return SourceMapItem.parse_str(val)

        elif isinstance(val, dict):
            return SourceMapItem.model_validate(val)

        elif not isinstance(val, SourceMapItem):
            raise TypeError(type(val))

        # Already validated.
        return val

    @classmethod
    def find_children(cls, node: Any) -> Iterator["ASTNode"]:
        def is_ast_node(data: Any) -> bool:
            return isinstance(data, dict) and any(x in data for x in ("ast_type", "nodeType"))

        if isinstance(node, dict):
            if is_ast_node(node):
                child = ASTNode.model_validate(node)
                yield child
                yield from child.children

            else:
                # Not a node but may have child nodes.
                yield from cls.find_children(list(node.values()))

        elif isinstance(node, (list, tuple)):
            for val in node:
                yield from cls.find_children(val)

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

    def __repr__(self) -> str:
        try:
            return str(self)
        except Exception:
            # Don't allow repr to fail.
            return "<ASTNode>"

    def __str__(self):
        num_children = len(list(self.children))
        stats = "leaf" if num_children == 0 else f"children={num_children}"
        return f"<{self.ast_type}Node {stats}>"

    def __setattr__(self, key, value):
        if key == "classification":
            self._classification = value
        else:
            return super().__setattr__(key, value)

    def iter_nodes(self) -> Iterator["ASTNode"]:
        """
        Yield through all nodes in the tree, including this one.
        """

        yield self
        for node in self.children:
            yield from node.iter_nodes()

    def get_node(self, src: SourceMapItem) -> Optional["ASTNode"]:
        """
        Get a node by source.

        Args:
            src (:class:`~ethpm_types.sourcemap.SourceMapItem`): The source map
              item to seek in the AST.

        Returns:
            Optional[``ASTNode``]: The matching node, if found, else ``None``.
        """

        if self.src.start == src.start and (self.src.length or 0) == (src.length or 0):
            return self

        for child in self.children:
            if node := child.get_node(src):
                return node

        return None

    def get_nodes_at_line(self, line_numbers: SourceLocation) -> Iterator["ASTNode"]:
        """
        Get the AST nodes for the given line number combination

        Args:
            line_numbers (``SourceLocation``): A tuple in the form of
              [lineno, col_offset, end_lineno, end_col_offset].

        Returns:
            Iterator[``ASTNode``]: All matching nodes.
        """

        if len(line_numbers) != 4:
            raise ValueError(
                "Line numbers should be given in form of "
                "`(lineno, col_offset, end_lineno, end_coloffset)`"
            )

        if all(x == y for x, y in zip(self.line_numbers, line_numbers)):
            yield self

        for child in self.children:
            yield from child.get_nodes_at_line(line_numbers)

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
            gen = function.get_nodes_at_line(line_numbers)
            if next(gen, None):
                return function

        return None
