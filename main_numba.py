import numpy as np
from numba import njit
import math as m
# from count_ops.numba_lang import count_ops


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
    for i in range(1, 239):
        for j in range(1, 319):
            idx = i * 320 + j
            x_val = 0.
            y_val = 0.
            for ki in range(3):
                for kj in range(3):
                    kidx = ki * 3 + kj
                    idx2 = (i + ki - 1) * 320 + (j + kj - 1)
                    x_val += image_in[idx2] * k_x[kidx]
                    y_val += image_in[idx2] * k_y[kidx]
            image_out[idx] = m.sqrt(x_val * x_val + y_val * y_val)


def main():
    a = simple_expression(1, 2, 3)
    print(a)
    print(simple_expression.get_annotation_info())
    # arr = np.ones(10, dtype=np.int32)
    # loop_with_constant(arr)
    # print(arr)
    # arr2d = np.ones((10, 20), dtype=np.int32)
    # nested_loop_with_constant(arr2d)
    # print(arr2d)

if __name__ == '__main__':
    main()
