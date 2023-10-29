import ast
from count_ops.lang_py import make_opcount_tree
from count_ops.common import OpCount, count_from_tree


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


def test_nested_loop():
    code = """
def nested_loop_with_constant(arr):
    for i in range(10):
        for j in range(20):
            arr[i, j] = i * 20 + j
"""
    expected = OpCount(add=200, mul=200)
    parsed = ast.parse(code)
    oc_tree = make_opcount_tree(parsed)
    assert count_from_tree(oc_tree) == expected


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
