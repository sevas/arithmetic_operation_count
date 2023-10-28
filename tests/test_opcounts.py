import pytest

from count_ops.common import range_to_count, OpCount



@pytest.mark.parametrize("loop_range, expected_steps", [
    ((0, 10, 1), 10),
    ((0, 10, 2), 5),
    ((2, 10, 2), 4),
])
def test_loop_range_to_step_count(loop_range, expected_steps):
    assert range_to_count(loop_range) == expected_steps



class TestOpCountSpec:
    @staticmethod
    def test_add():
        oc1 = OpCount(mul=1, add=2)
        oc2 = OpCount(mul=3, add=4)
        assert oc1 + oc2 == OpCount(mul=4, add=6)

    @staticmethod
    def test_cant_add_with_scalar():
        oc1 = OpCount(mul=1, add=2)
        with pytest.raises(NotImplementedError):
            oc1 + 2

    @staticmethod
    def test_mul_with_scalar():
        oc1 = OpCount(mul=1, add=2)
        assert oc1 * 2 == OpCount(mul=2, add=4)

    @staticmethod
    def test_rmul_with_scalar():
        oc1 = OpCount(mul=1, add=2)
        assert 2 * oc1 == OpCount(mul=2, add=4)