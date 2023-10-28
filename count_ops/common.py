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

    def __lt__(self, other):
        if isinstance(other, OpCount):
            return (self.mul + self.add) < (other.mul + other.add)
        else:
            raise NotImplementedError

@dataclass
class OpCountNode:
    """A simplified tree with only the nodes with arithmetic operations, loops and branches."""
    name: str
    children: list[Self]
    op_count: OpCount
    children_op_mult: int = 1
    is_branch: bool = False


def count_from_tree(node: OpCountNode):
    if node.children:
        if node.is_branch:
            assert node.children_op_mult == 1
            # When there are branches, we only count from the branch that yields the most ops.
            # Later, this can be changed to count from all branches and publish a partial count tree.
            # This means we will not have a single number.
            return node.op_count + max([count_from_tree(child) for child in node.children])
        else:
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
