import ast
from typing import Tuple

import pycparser

from .common import OpCount, range_to_count, OpCountNode, print_indent


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


def make_opcount_tree(node, level=0) -> OpCountNode:
    if isinstance(node, pycparser.c_ast.BinaryOp):
        print_indent(f"binary op {node.op}", level)
        if node.op == "*":
            oc = OpCount(mul=1)
        elif node.op in ["+", "-"]:
            oc = OpCount(add=1)
        elif node.op == "==":
            oc = OpCount()
        else:
            raise NotImplementedError(node.op)
        return OpCountNode(name=node.op, op_count=oc, children=[make_opcount_tree(node.left, level=level + 1),
                                                                make_opcount_tree(node.right, level=level + 1)])

    elif isinstance(node, pycparser.c_ast.UnaryOp):
        print_indent("unary op", level)
        return OpCountNode(name=node.op, op_count=OpCount(add=1),
                           children=[make_opcount_tree(node.expr, level=level + 1)])

    elif isinstance(node, pycparser.c_ast.Assignment):
        if node.op == "=":
            print_indent("assignment", level)
            return make_opcount_tree(node.rvalue, level=level + 1)
        elif node.op in ["+=", "-="]:
            print_indent("assignment with op", level)
            return OpCountNode(name=node.op, op_count=OpCount(add=1),
                               children=[make_opcount_tree(node.rvalue, level=level + 1)])
        elif node.op == "*=":
            print_indent("assignment with op", level)
            return OpCountNode(name=node.op, op_count=OpCount(mul=1),
                               children=[make_opcount_tree(node.rvalue, level=level + 1)])
        elif node.op == "/=":
            raise NotImplementedError(node.op)
        else:
            print_indent(f"!!! assignment with op {node.op}", level)
            return OpCountNode(name=node.op, op_count=OpCount(), children=[])

    elif isinstance(node, pycparser.c_ast.Constant):
        print_indent("constant", level)
        return OpCountNode(name="constant", op_count=OpCount(), children=[])

    elif isinstance(node, pycparser.c_ast.ID):
        print_indent(f"ID: {node.name}", level)
        return OpCountNode(name="ID", op_count=OpCount(), children=[])

    elif isinstance(node, pycparser.c_ast.FuncDef):
        print_indent("Func Body", level)
        print_indent(f"recurse in {node.body.__class__.__name__}", level)
        return make_opcount_tree(node.body, level=level + 1)

    elif isinstance(node, pycparser.c_ast.For):
        print_indent("For", level)
        loop_range = get_loop_range(node)
        loop_steps = range_to_count(loop_range)
        # TODO: add ops from loop increment in self opcount
        return OpCountNode(name="forloop", op_count=OpCount(), children_op_mult=loop_steps,
                           children=[make_opcount_tree(node.stmt, level=level + 1)])

    elif isinstance(node, pycparser.c_ast.If):
        print_indent("If", level)
        return OpCountNode(name="if", op_count=OpCount(), is_branch=True,
                           children=[make_opcount_tree(node.iftrue, level=level + 1),
                                     make_opcount_tree(node.iffalse, level=level + 1)])

    elif isinstance(node, pycparser.c_ast.Decl):
        print_indent(f"recurse in {node.init.__class__.__name__}", level)
        if node.init:
            return make_opcount_tree(node.init, level=level + 1)
        else:
            return OpCountNode(name="Decl", op_count=OpCount(), children=[])

    elif isinstance(node, pycparser.c_ast.Compound):
        print_indent("Compound", level)
        if node.block_items:
            return OpCountNode(name="Compound", op_count=OpCount(),
                               children=[make_opcount_tree(each, level=level + 1) for each in node.block_items])
        else:
            # empty block means no mul/add operations in this block
            return OpCountNode(name="Compound", op_count=OpCount(), children=[])
    elif isinstance(node, pycparser.c_ast.FuncCall):
        print_indent("FuncCall", level)
        if node.args:
            return OpCountNode(name="FuncCall", op_count=OpCount(),
                               children=[make_opcount_tree(each, level=level + 1) for each in node.args.exprs])

    elif isinstance(node, pycparser.c_ast.FileAST):
        for each in node.children():
            print_indent(f"recurse in {each[1].__class__.__name__}", level)
            return make_opcount_tree(each[1], level=level + 1)

    else:
        # all other case, we forward to child AST nodes
        # raise NotImplementedError(node.__class__.__name__)
        print_indent(f"!!! {node.__class__.__name__}", level)
        for each in node.children():
            print_indent(f"recurse in {each[1].__class__.__name__}", level)
            return make_opcount_tree(each[1], level=level + 1)
