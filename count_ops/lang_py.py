import ast
from typing import Tuple, List, Union

from .common import OpCountNode, OpCount, log_indented, range_to_count


def get_func_named(mod: ast.Module, name: str):
    for node in mod.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == name:
                return node
    raise KeyError(name)


def get_loop_range(range_args: List[Union[ast.Constant, ast.Name]], context=None) -> Tuple[int, int, int]:
    def get_value(arg):
        if isinstance(arg, ast.Constant):
            return arg.value
        elif isinstance(arg, ast.Name):
            if context is None:
                raise ValueError("context is None")
            return context[arg.id]
        else:
            raise NotImplementedError(arg.__class__.__name__)

    if len(range_args) == 1:
        start = 0
        end = get_value(range_args[0])
        step = 1
    elif len(range_args) == 2:
        start = get_value(range_args[0])
        end = get_value(range_args[1])
        step = 1
    elif len(range_args) == 3:
        start = get_value(range_args[0])
        end = get_value(range_args[1])
        step = get_value(range_args[2])
    else:
        raise NotImplementedError("range with more than 3 arguments")
    return start, end, step


def make_opcount_tree(node, context=None, level=0) -> OpCountNode:
    if isinstance(node, ast.BinOp):
        log_indented(f"binary op {node.op.__class__.__name__}", level)
        if isinstance(node.op, ast.Mult):
            oc = OpCount(mul=1)
        elif isinstance(node.op, (ast.Add, ast.Sub)):
            oc = OpCount(add=1)
        elif isinstance(node.op, ast.Div):
            oc = OpCount(div=1)
        else:
            raise NotImplementedError

        return OpCountNode(
            name=node.op.__class__.__name__,
            op_count=oc,
            children=[
                make_opcount_tree(node.left, context=context, level=level + 1),
                make_opcount_tree(node.right, context=context, level=level + 1),
            ],
        )
    elif isinstance(node, ast.For):
        log_indented("For", level)

        if node.iter.func.id in ("range", "prange"):
            loop_range = get_loop_range(node.iter.args, context=context)

            return OpCountNode(
                name=f"For range{loop_range}",
                op_count=OpCount(),
                children=[make_opcount_tree(child, context=context, level=level + 1) for child in node.body],
                children_op_mult=range_to_count(loop_range),
            )

        else:
            raise NotImplementedError(node.iter.func.id)

    elif isinstance(node, ast.If):
        log_indented("If", level)

        return OpCountNode(
            name="If",
            op_count=OpCount(),
            children=[make_opcount_tree(child, context=context, level=level + 1) for child in node.body + node.orelse],
            is_branch=True,
        )

    elif isinstance(node, ast.AugAssign):
        if isinstance(node.op, (ast.Add, ast.Sub)):
            oc = OpCount(add=1)
        elif isinstance(node.op, ast.Mult):
            oc = OpCount(mul=1)
        elif isinstance(node.op, ast.Div):
            oc = OpCount(div=1)
        else:
            raise NotImplementedError(node)

        return OpCountNode(
            name=f"AugAssign {node.op}",
            op_count=oc,
            children=[make_opcount_tree(node.value, context=context, level=level + 1)],
        )

    else:
        log_indented(node.__class__.__name__, level)

        return OpCountNode(
            name=node.__class__.__name__,
            op_count=OpCount(),
            children=[
                make_opcount_tree(child, context=context, level=level + 1) for child in ast.iter_child_nodes(node)
            ],
        )
