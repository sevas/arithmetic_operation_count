import numpy as np
from numba import njit, prange
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


def simple_branch(x, order):
    if order == 2:
        return x * x + 2 * x
    elif order == 3:
        return 3 * x * x * x + 2 * x * x + 1
    else:
        return 2 * x


@njit
def nested_loop_with_constant(arr):
    for i in range(10):
        for j in range(20):
            arr[i, j] = i * 20 + j


k_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])


k_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

neighbour_idx = np.array(
    [
        [(-1, -1), (-1, 0), (-1, 1)],
        [(0, -1), (0, 0), (0, 1)],
        [(1, -1), (1, 0), (1, 1)],
    ]
)


@njit
def sobel(image_in, image_out):
    for i in range(1, 239):
        for j in range(1, 319):
            idx = i * 320 + j
            x_val = 0.0
            y_val = 0.0
            for ki in range(3):
                for kj in range(3):
                    kidx = ki * 3 + kj
                    idx2 = (i + ki - 1) * 320 + (j + kj - 1)
                    x_val += image_in[idx2] * k_x[kidx]
                    y_val += image_in[idx2] * k_y[kidx]
            image_out[idx] = m.sqrt(x_val * x_val + y_val * y_val)


@njit
def clip(image_in, image_out, width, height, lo, hi):
    for i in prange(height):
        for j in range(width):
            val = image_in[i, j]
            if val < lo:
                image_out[i, j] = lo
            elif val > hi:
                image_out[i, j] = hi
            else:
                image_out[i, j] = val


@njit
def compute_bbox(xyz, count):
    xmin = np.inf
    ymin = np.inf
    zmin = np.inf
    xmax = -np.inf
    ymax = -np.inf
    zmax = -np.inf

    for i in range(count):
        xmin = min(xmin, xyz[i, 0])
        ymin = min(ymin, xyz[i, 1])
        zmin = min(zmin, xyz[i, 2])
        xmax = max(xmax, xyz[i, 0])
        ymax = max(ymax, xyz[i, 1])
        zmax = max(zmax, xyz[i, 2])
    return xmin, ymin, zmin, xmax, ymax, zmax


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


if __name__ == "__main__":
    main()
