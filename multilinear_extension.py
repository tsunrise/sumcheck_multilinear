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


def extend_sparse(data: Dict[int, int], num_var: int, fieldSize: int) -> MVLinear:
    """
    Convert an sparse map to a polynomial where the argument is the binary form of index.
    :param data: sparse map if index<2^L. If the size of array is not power of 2, out-of-range part will be arbitrary.
    :param num_var: number of variables
    :param fieldSize: The size of finite field that the array value belongs.
    :return: The result MVLinear P(x1, x2, ..., xl) = Arr[0bxl...x1]
    """
    l: int = num_var
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


def evaluate(data: List[int], arguments: List[int],  fieldSize: int) -> int:
    """
    Directly evaluate a polynomial based on multilinear extension. The function takes linear time to the size of data.
    :param data: The bookkeeping table (where the multilinear extension is based on)
    :param arguments: Input argument
    :param fieldSize:
    :return:
    """

    L = len(arguments)
    p = fieldSize
    assert len(data) <= (1 << L), "Insufficient data"

    A: List[int] = data.copy()
    if len(A) < (1 << L):
        A += [0] * (1 << L - len(A))
    for i in range(1, L + 1):
        r = arguments[i-1]
        for b in range(2**(L-i)):
            A[b] = (A[b << 1] * (1 - r) + A[(b << 1) + 1] * r) % p
    return A[0]


def evaluate_sparse(data: Dict[int, int], arguments: List[int], fieldSize: int) -> int:
    """
    Sparse version of the function evaluate. The function also takes linear time to the size of data.
    :param data: dictionary indicating a map between binary argument and its value (sparse bookkeeping table)
    :param arguments: Input argument
    :param fieldSize:
    :return:
    """
    L = len(arguments)
    p = fieldSize

    dp0 = data.copy()
    dp1: Dict[int, int] = dict()
    for i in range(L):
        r = arguments[i]
        for k, v in dp0.items():
            if k >> 1 not in dp1:
                dp1[k >> 1] = 0
            if k & 1 == 0:
                dp1[k >> 1] = (dp1[k >> 1] + dp0[k] * (1 - r)) % p
            else:
                dp1[k >> 1] = (dp1[k >> 1] + dp0[k] * r) % p
        dp0 = dp1
        dp1 = dict()
    if 0 not in dp0:
        return 0
    return dp0[0]