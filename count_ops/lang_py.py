import ast
from typing import Tuple, List

from .common import OpCountNode, OpCount, log_indented, range_to_count


def get_func_named(mod: ast.Module, name: str):
    for node in mod.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == name:
                return node
    raise KeyError(name)


def get_loop_range(range_args: List[ast.Constant]) -> Tuple[int, int, int]:
    if len(range_args) == 1:
        start = 0
        end = range_args[0].value
        step = 1
    elif len(range_args) == 2:
        start = range_args[0].value
        end = range_args[1].value
        step = 1
    elif len(range_args) == 3:
        start = range_args[0].value
        end = range_args[1].value
        step = range_args[2].value
    else:
        raise NotImplementedError("range with more than 3 arguments")
    return start, end, step


def make_opcount_tree(node, level=0) -> OpCountNode:
    if isinstance(node, ast.BinOp):
        log_indented(f"binary op {node.op.__class__.__name__}", level)
        if isinstance(node.op, ast.Mult):
            oc = OpCount(mul=1)
        elif isinstance(node.op, (ast.Add, ast.Sub)):
            oc = OpCount(add=1)
        elif isinstance(node.op, ast.Div):
            raise NotImplementedError(node.op)
        else:
            raise NotImplementedError

        return OpCountNode(
            name=node.op.__class__.__name__,
            op_count=oc,
            children=[make_opcount_tree(node.left, level=level + 1), make_opcount_tree(node.right, level=level + 1)],
        )
    elif isinstance(node, ast.For):
        log_indented("For", level)

        if node.iter.func.id == "range":
            loop_range = get_loop_range(node.iter.args)

            return OpCountNode(
                name="For",
                op_count=OpCount(),
                children=[make_opcount_tree(child, level=level + 1) for child in node.body],
                children_op_mult=range_to_count(loop_range),
            )

        else:
            raise NotImplementedError(node.iter.func.id)
    elif isinstance(node, ast.AugAssign):
        if isinstance(node.op, (ast.Add, ast.Sub)):
            oc = OpCount(add=1)
        elif isinstance(node.op, ast.Mult):
            oc = OpCount(mul=1)
        elif isinstance(node.op, ast.Div):
            raise NotImplementedError(node.op)
        else:
            raise NotImplementedError(node)

        return OpCountNode(
            name=f"AugAssign {node.op}", op_count=oc, children=[make_opcount_tree(node.value, level=level + 1)]
        )

    else:
        log_indented(node.__class__.__name__, level)

        return OpCountNode(
            name=node.__class__.__name__,
            op_count=OpCount(),
            children=[make_opcount_tree(child, level=level + 1) for child in ast.iter_child_nodes(node)],
        )
