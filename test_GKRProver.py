import random
from typing import Dict, Tuple, List
from unittest import TestCase

from GKR import GKR
from multilinear_extension import extend_sparse, evaluate
from GKRProver import binaryToList, initialize_PhaseOne, initialize_PhaseTwo, sumOfGKR, talkToVerifierPhase1, \
    talk_to_verifier_phase2
from polynomial import randomPrime, randomMVLinear, MVLinear
from GKRVerifier import GKRVerifier, GKRVerifierState

def generateRandomF1(L: int, p: int) -> Dict[int, int]:
    n = round(((1 << (3*L))**0.5))
    ans = dict()
    for _ in range(n):
        term = random.randint(0, (1 << (3*L)) - 1)
        ev = random.randint(0, p-1)
        ans[term] = ev
    return ans

def randomGKR(L: int, p: int) -> GKR:
    f1 = generateRandomF1(L, p)
    f2 = [random.randint(0, p-1) for _ in range(1 << L)]
    f3 = [random.randint(0, p-1) for _ in range(1 << L)]

    return GKR(f1, f2, f3, p, L)

class Test(TestCase):
    def test_initialize_phase_one_two(self):
        L = 5
        p = randomPrime(64)
        print(f"Testing GKR Prover Bookkeeping table generator functions... Use L = {L}, p = {p}")
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

        A_hg_actual, G = initialize_PhaseOne(D_f1, L, p, A_f3, g)
        for i in range(1 << L):
            self.assertEqual(A_hg_expected[i] % p, A_hg_actual[i] % p)
        print("PASS: initialize_PhaseOne")
        # phase 2
        u = [random.randint(0, p-1) for _ in range(L)]
        f1_fix_gu = f1_fix_g.eval_part(u)
        self.assertEqual(f1_fix_gu.num_variables, L)

        A_f1_expected = [0] * (1 << L)
        for i in range(1 << L):
            y = i & ((1 << L) - 1)
            A_f1_expected[y] = f1_fix_gu.eval_bin(y)

        A_f1_actual = initialize_PhaseTwo(D_f1, G, u, p)
        for i in range(1 << L):
            self.assertEqual(A_f1_expected[i] % p, A_f1_actual[i] % p)
        print("PASS: initialize_PhaseTwo")

    def test_completeness_sanity(self):
        print(f"Test Completeness of GKR protocol (test individual functions)")
        L = 7
        p = randomPrime(256)
        gkr = randomGKR(L, p)
        g = [random.randint(0, p-1) for _ in range(L)]

        A_hg, G = initialize_PhaseOne(gkr.f1, L, p, gkr.f3, g)
        s = sumOfGKR(A_hg, gkr.f2, p)
        v = GKRVerifier(gkr, g, s)
        self.assertEqual(v.state, GKRVerifierState.PHASE_ONE_LISTENING, "wrong verifier state")

        u, f2u = talkToVerifierPhase1(A_hg, gkr, v)
        self.assertEqual(len(u), L, "wrong randomness size")
        self.assertEqual(v.state, GKRVerifierState.PHASE_TWO_LISTENING, "verifier should be in phase two")
        self.assertEqual(f2u % p, evaluate(gkr.f2, u, p) % p, "f2(u) returned by talkToVerifierPhase1 is incorrect")

        print(f"initialize_PhaseOne, sumOfGKR, talkToVerifierPhase1 looks good. ")
        A_f1 = initialize_PhaseTwo(gkr.f1, G, u, p)
        talk_to_verifier_phase2(A_f1, gkr, f2u, v)
        self.assertEqual(v.state, GKRVerifierState.ACCEPT, "Verifier does not accept this proof. ")
        print(f"initialize_PhaseTwo, talk_to_verifier_phase2 looks good. ")
        print(f"Completeness test PASS!")

def calculateBookKeepingTable(poly: MVLinear) -> Tuple[List[int], int]:
    """
    :return: A bookkeeping table where the index is the binary form of argument of polynomial and value is the
    evaluated value; the sum
    """
    P = poly.p
    A: List[int] = [0] * (2 ** poly.num_variables)
    s = 0
    for p in range(2 ** poly.num_variables):
        A[p] = poly.eval(binaryToList(p, poly.num_variables))
        s = (s + A[p]) % P

    return A, s