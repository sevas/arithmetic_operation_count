from dataclasses import dataclass


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


def range_to_count(loop_range):
    start, end, step = loop_range
    return int((end - start) / step)
