import ast
import logging
from pathlib import Path

from count_ops.common import count_from_tree
from count_ops.lang_py import make_opcount_tree, get_func_named
from count_ops.parse import parse

SRC_FILE = Path(__file__).parent / "main_numba.py"


def func_names(mod: ast.Module):
    for node in mod.body:
        if isinstance(node, ast.FunctionDef):
            yield node.name


def print_tree(node: ast.AST, level=0):
    print("  " * level + f"{node.__class__.__name__}")
    for child in ast.iter_child_nodes(node):
        print_tree(child, level=level + 1)


def main():
    logger = logging.getLogger("count_ops")
    logger.setLevel(logging.DEBUG)

    parsed = parse(SRC_FILE.read_text())
    print(list(func_names(parsed)))
    f = get_func_named(parsed, "sobel")
    # print_tree(f)

    op_tree = make_opcount_tree(f)
    oc = count_from_tree(op_tree)
    print(oc)


if __name__ == "__main__":
    main()
