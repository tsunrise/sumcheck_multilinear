from typing import List, Tuple, Dict

from polynomial import MVLinear


def binaryToList(b: int, numVariables: int) -> List[int]:
    """
    Change binary form to list of arguments.

    :param b: The binary form in little endian encoding. For example: 0b1011 means g(x0=1, x1 = 1, x2 = 0, x3 = 1)
    :param numVariables: The number of variables
    :return:
    """
    lst: List[int] = [0] * numVariables
    i = 0
    while b != 0:
        lst[i] = b & 1
        b >>= 1
        i += 1
    return lst


def precompute(g: List[int], p: int)->List[int]:
    L = len(g)
    G = [0] * (1 << L)
    # handle first case
    G[0] = (1-g[0])
    G[1] = g[0]
    for i in range(1, L):
        oldG = G[:]
        for b in range(1 << i):
            G[b] = oldG[b] * (1 - g[i]) % p
            G[b + (1 << i)] = oldG[b]*g[i] % p
    return G

def _three_split(arg: int, L: int) -> Tuple[int, int, int]:
    """
    :param arg: argument of length 3L
    :param L: L
    :return: z (first L bits), x (second L bits), y (last L bits) little endian
    """
    z = arg & ((1 << L) - 1)  # get first L argument: this is z
    x = (arg & (((1 << L) - 1) << L)) >> L
    y = (arg & (((1 << L) - 1) << (2 * L))) >> (2 * L)
    return z, x, y

def initialize_PhaseOne(f1: Dict[int, int], L: int, p: int, A_f3: List[int], g: List[int])-> Tuple[List[int], List[int]]:
    """
    (Paper P16) phase one

    :param f1: f1(z,x,y) Sparse MVLinear represented by Dict[argument in little endian binary form, evaluation]
    :param L: number of variables of f3
    :param p: field size
    :param A_f3: Bookkeeping table of f3  (where f3 is the multilinear extension of that)
    :param g: fixed parameter g of f1
    :return: Bookkeeping table of h_g = sum over y: f1(g,x,y)*f3(y). It has size 2**L. It also returns G,
    which is precompute(g,p), that is useful for phase two.
    """
    # sanity check        z = term & ((1 << L) - 1)   # get first L argument: this is z
    #         x = (term & (((1 << L) - 1) << L)) >> L
    #         y = (term & (((1 << L) - 1) << (2 * L))) >> (2 * L)
    assert len(A_f3) == 2**L
    assert len(g) == L

    A_hg = [0] * (1 << L)

    G = precompute(g, p)

    # rely on sparsity
    for arg, ev in f1.items():
        # assert (arg < 1 << (3*L))  # make sure f1 has no more than 3*L variables # should be checked in GKR
        z, x, y = _three_split(arg, L)

        A_hg[x] = (A_hg[x] + G[z]*ev*A_f3[y]) % p
    return A_hg, G


def initialize_PhaseTwo(f1: Dict[int, int], G: List[int], u: List[int], p: int) -> List[int]:
    """
    (paper p16) phase two

    :param f1: f1(z,x,y) Sparse MVLinear represented by Dict[argument in little endian binary form, evaluation]
    :param G: precompute(g, p), which is outputted in phase one. It has size 2**L.
    :param u: randomness of previous phase sum check protocol. It has size L (#variables in f2, f3).
    :param p: field size
    :return: A_f1: the bookkeeping table f1(g, u, y) over y. It has size 2**L.
    """

    L = len(u)
    U = precompute(u, p)
    assert len(U) == len(G), "len(U) != len(G)"
    A_f1: List[int] = [0] * (1 << L)
    for arg, ev in f1.items():
        z, x, y = _three_split(arg, L)
        A_f1[y] = (A_f1[y] + G[z]*U[x]*ev) % p
    return A_f1








