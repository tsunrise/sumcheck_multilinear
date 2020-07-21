import random
from typing import Dict
from unittest import TestCase

from multilinear_extension import extend_sparse
from GKRProver import binaryToList, initialize_PhaseOne, calculateBookKeepingTable
from polynomial import randomPrime, randomMVLinear
from IPPMFProver import PMF, InteractivePMFProver


def generateRandomF1(L: int, p: int) -> Dict[int, int]:
    n = round(((1 << (3*L))**0.5))
    ans = dict()
    for _ in range(n):
        term = random.randint(0, (1 << (3*L)) - 1)
        ev = random.randint(0, p-1)
        ans[term] = ev
    return ans


class Test(TestCase):
    def test_initialize_phase_one(self):
        L = 5
        p = randomPrime(64)
        # generate random sparse f1, random f3, g
        D_f1 = generateRandomF1(L, p)
        f3 = randomMVLinear(L, prime=p)
        g = [random.randint(0, p-1) for _ in range(L)]
        # get bookkeeping table for f3
        A_f3, _ = calculateBookKeepingTable(f3)
        # get poly form for f1 (only for test checking)
        A_f1 = [0] * (1 << (3 * L))
        for k, v in D_f1.items():
            A_f1[k] = v
        f1 = extend_sparse(D_f1, 3*L, p)

        f1_fix_g = f1.eval_part(g)
        self.assertEqual(f1_fix_g.num_variables, 2*L)

        A_hg_expected = [0] * (1 << L)
        for i in range(1 << (2*L)):
            x = i & ((1 << L) - 1)
            y = (i & (((1 << L) - 1) << L)) >> L
            A_hg_expected[x] = (A_hg_expected[x] + f1_fix_g.eval_bin(i) * A_f3[y]) % p

        A_hg_actual = initialize_PhaseOne(D_f1, L, p, A_f3, g)
        for i in range(1 << L):
            self.assertEqual(A_hg_expected[i] % p, A_hg_actual[i] % p)


