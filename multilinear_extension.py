import math
from typing import List, Dict

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

    poly_terms = {i: 0 for i in range(2**l)}

    for b in range(len(data)):
        sub_poly = gen({b: data[b]})
        xi0 = [x[i] for i in range(l) if b >> i & 1 == 0]
        sub_poly *= _product1mx(xi0, 0, len(xi0)-1)
        for t, v in sub_poly.terms.items():
            poly_terms[t] += v

    return gen(poly_terms)


def extend_sparse(data: Dict[int, int], L: int, fieldSize: int) -> MVLinear:
    """
    Convert an sparse map to a polynomial where the argument is the binary form of index.
    :param data: sparse map if index<2^L. If the size of array is not power of 2, out-of-range part will be arbitrary.
    :param L: number of variables
    :param fieldSize: The size of finite field that the array value belongs.
    :return: The result MVLinear P(x1, x2, ..., xl) = Arr[0bxl...x1]
    """
    l: int = L
    p = fieldSize
    gen = makeMVLinearConstructor(l, p)
    x = [gen({1 << i: 1}) for i in range(l)]  # predefine x_1, ..., x_l

    poly_terms = {i: 0 for i in range(2**l)}

    for b, vb in data.items():
        sub_poly = gen({b: vb})
        xi0 = [x[i] for i in range(l) if b >> i & 1 == 0]
        sub_poly *= _product1mx(xi0, 0, len(xi0)-1)
        for t, v in sub_poly.terms.items():
            poly_terms[t] += v

    return gen(poly_terms)

def _product1mx(xs: List[MVLinear], lo: int, hi: int):
    """
    Divide and conquer algorithm for calculating product of (1-xi)
    """
    if lo == hi:
        return 1 - xs[lo]
    if hi > lo:
        L = _product1mx(xs, lo, lo + (hi - lo) // 2)
        R = _product1mx(xs, lo + (hi - lo) // 2 + 1, hi)
        return L * R
    return 1

