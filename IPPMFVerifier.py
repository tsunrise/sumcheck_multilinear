from typing import List, Tuple


def modInverse(a: int, m: int):
    """
    modular inverse (https://www.geeksforgeeks.org/multiplicative-inverse-under-modulo-m/)
    :param a: a
    :param m: prime
    :return: a^-1 mod p
    """

    m0 = m
    y = 0
    x = 1

    if m == 1:
        return 0

    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0:
        x += m0
    return x


def interpolate(points: List[int], r: int, p: int):
    """
    Interpolate and evaluate a PMF.
    Adapted from https://www.geeksforgeeks.org/lagranges-interpolation/
    :param points: P_0, P_1, P_2, ..., P_m where P is the product of m multilinear polynomials
    :param r: The point we want to evaluate at. In this scenario, the verifier wants to evaluate p_r.
    :param p: Field size.
    :return: P_r
    """

    result = 0
    for i in range(len(points)):

        term = points[i]
        for j in range(len(points)):
            if j != i:
                term = (term * ((r - j) % p) * modInverse((i - j) % p, p)) % p

        result = (result + term) % p

    return result
