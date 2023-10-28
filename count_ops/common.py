from dataclasses import dataclass
from typing import Self


@dataclass
class OpCount:
    mul: int = 0
    add: int = 0

    def __add__(self, other):
        if isinstance(other, OpCount):
            return OpCount(self.mul + other.mul, self.add + other.add)
        else:
            raise NotImplementedError

    def __mul__(self, rhs):
        if isinstance(rhs, int):
            return OpCount(self.mul * rhs, self.add * rhs)
        else:
            raise NotImplementedError(rhs.__class__.__name__)

    def __rmul__(self, lhs):
        return self * lhs


@dataclass
class OpCountNode:
    name: str
    children: list[Self]
    op_count: OpCount
    children_op_mult: int = 1


def count_from_tree(node: OpCountNode):
    if node.children:
        return node.op_count + sum([count_from_tree(child) for child in node.children],
                                   start=OpCount()) * node.children_op_mult
    else:
        return node.op_count


def print_tree(node: OpCountNode, level=0):
    print("  " * level + f"{node.name}: {node.op_count}")
    for child in node.children:
        print_tree(child, level=level + 1)


def range_to_count(loop_range):
    start, end, step = loop_range
    return int((end - start) / step)
