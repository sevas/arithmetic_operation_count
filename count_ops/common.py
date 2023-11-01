import logging
from dataclasses import dataclass, field
from typing import Self, Dict

logger = logging.getLogger("count_ops")


@dataclass
class OpCount:
    mul: int = 0
    add: int = 0
    div: int = 0
    functions: Dict[str, int] = field(default_factory=dict)

    def __add__(self, other):
        if isinstance(other, OpCount):
            return OpCount(self.mul + other.mul, self.add + other.add, self.div + other.div)
        else:
            raise NotImplementedError

    def __mul__(self, rhs):
        if isinstance(rhs, int):
            return OpCount(self.mul * rhs, self.add * rhs, self.div * rhs)
        else:
            raise NotImplementedError(rhs.__class__.__name__)

    def __rmul__(self, lhs):
        return self * lhs

    def __lt__(self, other):
        if isinstance(other, OpCount):
            return self._count_all() < other._count_all()
        else:
            raise NotImplementedError

    def _count_all(self):
        return self.mul + self.add + self.div + sum(self.functions.values())


@dataclass
class OpCountNode:
    """A simplified tree with only the nodes with arithmetic operations, loops and branches."""

    name: str
    children: list[Self]
    op_count: OpCount
    children_op_mult: int = 1
    is_branch: bool = False
    metadata: dict = field(default_factory=dict)


def count_from_tree(node: OpCountNode):
    if node.children:
        if node.is_branch:
            assert node.children_op_mult == 1
            # When there are branches, we only count from the branch that yields the most ops.
            # Later, this can be changed to count from all branches and publish a partial count tree.
            # This means we will not have a single number.
            return node.op_count + max([count_from_tree(child) for child in node.children])
        else:
            return (
                node.op_count
                + sum([count_from_tree(child) for child in node.children], start=OpCount()) * node.children_op_mult
            )
    else:
        return node.op_count


def print_tree(node: OpCountNode, level=0):
    msg = "  " * level + f"{node.name}"
    if node.op_count.add > 0 or node.op_count.mul > 0:
        msg += f"{node.op_count}"
    if node.children_op_mult > 1:
        msg += f" * {node.children_op_mult}"
    if node.is_branch:
        msg += " (branch)"
    print(msg)
    for child in node.children:
        print_tree(child, level=level + 1)


def range_to_count(loop_range):
    start, end, step = loop_range
    return int((end - start) / step)


def log_indented(msg, level):
    logger.info("  " * level + msg)
