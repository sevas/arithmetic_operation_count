import numpy as np
from numba import njit

from count_ops.c_lang import count_ops


@njit
def simple_expression(a, b, c):
    a = a + b + 2 * (c * 3)
    return a

@njit
def loop_with_constant(arr):
    for i in range(10):
        arr[i] = i * 2 + 3


@njit
def nested_loop_with_constant(arr):
    for i in range(10):
        for j in range(20):
            arr[i, j] = i * 20 + j


def main():
    a = simple_expression(1, 2, 3)
    print(a)
    arr = np.ones(10, dtype=np.int32)
    loop_with_constant(arr)
    print(arr)
    arr2d = np.ones((10, 20), dtype=np.int32)
    nested_loop_with_constant(arr2d)
    print(arr2d)

if __name__ == '__main__':
    main()
