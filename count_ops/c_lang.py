import ast
from typing import Tuple

import pycparser

from .common import OpCount, range_to_count


def print_indent(msg, level):
    print("  " * level + msg)


def get_loop_range(for_node: pycparser.c_ast.For) -> Tuple[int, int, int]:
    """Extract start, end and step from a for loop"""
    assert isinstance(for_node, pycparser.c_ast.For)
    if isinstance(for_node.init, pycparser.c_ast.DeclList):
        # simplification: only one variable, one Decl in decllist
        if len(for_node.init.decls) == 1:
            if isinstance(for_node.init.decls[0].init, pycparser.c_ast.Constant):
                start = ast.literal_eval(for_node.init.decls[0].init.value)
            else:
                # only constants. Variables to be added
                raise NotImplementedError(for_node.init.decls[0].init.__class__.__name__)
        else:
            raise NotImplementedError(for_node.init.decls.__class__.__name__)
    else:
        raise NotImplementedError(for_node.init.__class__.__name__)

    if isinstance(for_node.cond, pycparser.c_ast.BinaryOp):
        if isinstance(for_node.cond.left, pycparser.c_ast.ID):
            end = ast.literal_eval(for_node.cond.right.value)
        else:
            raise NotImplementedError(for_node.cond.left.__class__.__name__)
    else:
        raise NotImplementedError(for_node.cond.__class__.__name__)

    if isinstance(for_node.next, pycparser.c_ast.UnaryOp):
        if isinstance(for_node.next.expr, pycparser.c_ast.ID):
            step = 1
        else:
            raise NotImplementedError(for_node.next.expr.__class__.__name__)
    else:
        raise NotImplementedError(for_node.next.__class__.__name__)

    return start, end, step


def count_ops(node, level=0) -> OpCount:
    if isinstance(node, pycparser.c_ast.BinaryOp):
        print_indent("binary op", level)
        if node.op == "*":
            oc = OpCount(mul=1)
        elif node.op == "+":
            oc = OpCount(add=1)
        else:
            raise NotImplementedError(node.op)
        return oc + count_ops(node.left, level=level + 1) + count_ops(node.right, level=level + 1)
    elif isinstance(node, pycparser.c_ast.UnaryOp):
        print_indent("unary op", level)
        return OpCount(add=1) + count_ops(node.expr, level=level + 1)
    elif isinstance(node, pycparser.c_ast.Assignment):
        if node.op == "=":
            print_indent("assignment", level)
            return count_ops(node.rvalue, level=level + 1)
        else:
            print_indent(f"!!! assignment with op {node.op}", level)
            return OpCount()
    elif isinstance(node, pycparser.c_ast.Constant):
        print_indent("constant", level)
        return OpCount()
    elif isinstance(node, pycparser.c_ast.ID):
        print_indent(f"ID: {node.name}", level)
        return OpCount()
    elif isinstance(node, pycparser.c_ast.FuncDef):
        print_indent("Func Body", level)
        print_indent(f"recurse in {node.body.__class__.__name__}", level)
        return count_ops(node.body, level=level + 1)
    elif isinstance(node, pycparser.c_ast.For):
        print_indent("For", level)
        loop_range = get_loop_range(node)
        loop_steps = range_to_count(loop_range)
        return count_ops(node.stmt, level=level + 1) * loop_steps
    elif isinstance(node, pycparser.c_ast.Decl):
        print_indent(f"recurse in {node.init.__class__.__name__}", level)
        return count_ops(node.init, level=level + 1)
    elif isinstance(node, pycparser.c_ast.Compound):
        print_indent("Compound", level)
        return sum((count_ops(each, level=level + 1) for each in node.block_items), start=OpCount())
    elif isinstance(node, pycparser.c_ast.FileAST):
        for each in node.children():
            print_indent(f"recurse in {each[1].__class__.__name__}", level)
            return count_ops(each[1], level=level + 1)

    else:
        # raise NotImplementedError(node.__class__.__name__)
        print_indent(f"!!! {node.__class__.__name__}", level)
        for each in node.children():
            print_indent(f"recurse in {each[1].__class__.__name__}", level)
            return count_ops(each[1], level=level + 1)
