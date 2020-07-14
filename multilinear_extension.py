import math
from typing import List

from polynomial import MVLinear, makeMVLinearConstructor


def extend(data: List[int], fieldSize: int) -> MVLinear:
    """
    Convert an array to a polynomial where the argument is the binary form of index.
    :param data: Array of size 2^l. If the size of array is not power of 2, out-of-range part will be arbitrary.
    :param fieldSize: The size of finite field that the array value belongs.
    :return: The result MVLinear P(x1, x2, ..., xl) = Arr[0bxl...x1]
    """
    l: int = math.ceil(math.log(len(data), 2))
    p = fieldSize
    gen = makeMVLinearConstructor(l, p)
    x = [gen({1 << i: 1}) for i in range(l)]  # predefine x_1, ..., x_l

    poly = gen({0: 0})  # initialize poly = 0

    for b in range(len(data)):
        sub_poly = gen({0: data[b]})
        for i in range(l):
            bi = (b >> i) & 1
            if bi == 1:
                sub_poly *= x[i]
            else:
                sub_poly *= 1 - x[i]
        poly += sub_poly

    return poly
