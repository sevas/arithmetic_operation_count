import ast

import pytest

from count_ops.lang_py import make_opcount_tree, get_func_named
from count_ops.common import OpCount, count_from_tree
from count_ops.parse import parse


class TestExpressionsAndAssignmentsSpec:
    @staticmethod
    def test_simple_expression():
        code = """
def func():
    a = 12 * 2 + 3 + 2 * (2 * 5)
    return a
        """
        expected = OpCount(mul=3, add=2)
        parsed = ast.parse(code)
        oc_tree = make_opcount_tree(parsed)
        assert count_from_tree(oc_tree) == expected

    @staticmethod
    def test_division_binop_not_implemented():
        code = """
def func():
    a = 12 / 2
    return a
        """
        with pytest.raises(NotImplementedError):
            parsed = parse(code)
            make_opcount_tree(parsed)

    @staticmethod
    def test_augmented_assignment():
        code = """
def func():
    a = 12
    a += 2
    a -= 34
    a *= 5
    return a
    """
        expected = OpCount(add=2, mul=1)
        parsed = parse(code)
        oc_tree = make_opcount_tree(parsed)
        assert expected == count_from_tree(oc_tree)

    def test_division_assignment_is_not_implemented(self):
        code = """
def func():
    a = 0
    a /= 2
    return a
        """
        with pytest.raises(NotImplementedError):
            parsed = parse(code)
            make_opcount_tree(parsed)


def test_simple_ifelse():
    code = """
def func():  
    res = 0
    if res == 0:
        res = res + 2
    else:
        res = res + 3 * 3
    return res
    """
    expected = OpCount(mul=1, add=1)
    parsed = ast.parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert expected == count_from_tree(oc_tree)


def test_ifelifelse():
    code = """
def func():  
    res = 0
    if res == 0:
        res = res + 2
    elif res == 1:
        res = res + 3 * 3
    elif res == 2:
        res = res + 3 * 3 * 5 + 12
    else:
        res = res + res + res *2 
    
    return res
    """
    expected = OpCount(mul=2, add=2)
    parsed = ast.parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert expected == count_from_tree(oc_tree)


class TestForLoopsSpec:
    @staticmethod
    def test_simple_loop():
        code = """
def func(arr):
    for i in range(10):
        arr[i] = i * 2 + 3
        """
        expected = OpCount(add=10, mul=10)
        parsed = ast.parse(code)
        oc_tree = make_opcount_tree(parsed)
        assert count_from_tree(oc_tree) == expected

    @staticmethod
    def test_simple_loop_with_variable():
        code = """
def func(arr):
    for i in range(n):
        arr[i] = i * 2 + 3
        """
        expected = OpCount(add=5, mul=5)
        parsed = ast.parse(code)
        oc_tree = make_opcount_tree(parsed, context={"n": 5})
        assert count_from_tree(oc_tree) == expected

    @staticmethod
    def test_raise_exception_when_context_is_not_defined():
        code = """
def func():
    a = 0
    for i in range(n):
        a += i
    return a
        """
        with pytest.raises(ValueError):
            parsed = parse(code)
            make_opcount_tree(parsed)

    @staticmethod
    def test_nested_loop():
        code = """
def test_nested_loop_with_constant(arr):
    for i in range(10):
        for j in range(20):
            arr[i, j] = i * 20 + j
    """
        expected = OpCount(add=200, mul=200)
        parsed = ast.parse(code)
        oc_tree = make_opcount_tree(parsed)
        assert count_from_tree(oc_tree) == expected

    @staticmethod
    def test_range_with_3_args():
        code = """
def func():
    a = 0
    for i in range(1, 10, 2):
        a += i
    return a
        """
        expected = OpCount(add=4, mul=0)
        parsed = parse(code)
        oc_tree = make_opcount_tree(parsed)
        assert expected == count_from_tree(oc_tree)

    @staticmethod
    def test_for_with_other_generator_raises_exception():
        code = """
def func(arr):
    for i in loop(10):
        arr[i] = i * 2 + 3
        """
        parsed = parse(code)
        with pytest.raises(NotImplementedError):
            make_opcount_tree(parsed)


class Test_get_func_named_Spec:
    @staticmethod
    def test_can_get_function_by_name():
        code = """
def foo(): pass
def bar(): pass
        """
        parsed = parse(code)
        bar_func = get_func_named(parsed, name="bar")
        assert bar_func.name == "bar"

    @staticmethod
    def test_raises_keyerror_when_function_does_not_exist():
        code = """
def foo(): pass
def bar(): pass
        """
        parsed = parse(code)
        with pytest.raises(KeyError):
            get_func_named(parsed, name="baz")


def test_sobel_filter():
    code = """
k_x = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]])

k_y = np.array([
    [-1, -2, -1],
    [ 0, 0, 0],
    [ 1, 2, 1]])

neighbour_idx = np.array([
    [(-1, -1), (-1, 0), (-1, 1)],
    [( 0, -1), ( 0, 0), ( 0, 1)],
    [( 1, -1), ( 1, 0), ( 1, 1)],
])

@njit
def sobel(image_in, image_out):
    for i in range(1, 239):                                         # 238 steps
        for j in range(1, 319):                                     #   318 steps
            idx = i * 320 + j                                       #     1 add, 1 mul
            x_val = 0.0
            y_val = 0.0
            for ki in range(3):                                     #     3 steps
                for kj in range(3):                                 #       3 steps
                    kidx = ki * 3 + kj                              #         1 add, 1 mul
                    idx2 = (i + ki - 1) * 320 + (j + kj - 1)        #         5 add, 1 mul
                    x_val += image_in[idx2] * k_x[kidx]             #         1 add, 1 mul
                    y_val += image_in[idx2] * k_y[kidx]             #         1 add, 1 mul
            image_out[idx] = m.sqrt(x_val * x_val + y_val * y_val)  #    2 add, 1 mul
    
    """
    expected = OpCount(
        # fmt: off
        mul=238 * 318 * (1 + (3 * 3 * (1 + 1 + 1 + 1)) + 2),
        add=238 * 318 * (1 + (3 * 3 * (1 + 5 + 1 + 1)) + 1)
        # fmt: on
    )
    parsed = ast.parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert count_from_tree(oc_tree) == expected
