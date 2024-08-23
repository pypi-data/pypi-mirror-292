import ast
from .constants import ATTRIBUTES_MESSAGE_TEMPLATE_KEY as ATTRIBUTES_MESSAGE_TEMPLATE_KEY, ATTRIBUTES_SAMPLE_RATE_KEY as ATTRIBUTES_SAMPLE_RATE_KEY, ATTRIBUTES_TAGS_KEY as ATTRIBUTES_TAGS_KEY
from .stack_info import StackInfo as StackInfo, get_filepath_attribute as get_filepath_attribute
from .utils import uniquify_sequence as uniquify_sequence
from dataclasses import dataclass
from opentelemetry.util import types as otel_types

@dataclass(frozen=True)
class LogfireArgs:
    """Values passed to `logfire.instrument` and/or values stored in a logfire instance as basic configuration.

    These determine the arguments passed to the method calls added by the AST transformer.
    """
    tags: tuple[str, ...]
    sample_rate: float | None
    msg_template: str | None = ...
    span_name: str | None = ...
    extract_args: bool = ...

@dataclass
class BaseTransformer(ast.NodeTransformer):
    """Helper for rewriting ASTs to wrap function bodies in `with {logfire_method_name}(...):`."""
    logfire_args: LogfireArgs
    logfire_method_name: str
    filename: str
    module_name: str
    qualname_stack = ...
    def __post_init__(self) -> None: ...
    def visit_ClassDef(self, node: ast.ClassDef): ...
    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef): ...
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef): ...
    def rewrite_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, qualname: str) -> ast.AST: ...
    def logfire_method_call_node(self, node: ast.FunctionDef | ast.AsyncFunctionDef, qualname: str) -> ast.Call: ...
    def logfire_method_arg_values(self, qualname: str, lineno: int) -> tuple[str, dict[str, otel_types.AttributeValue]]: ...
