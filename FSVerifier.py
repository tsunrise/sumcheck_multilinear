import random
from copy import copy
from typing import List, Tuple

from polynomial import MVLinear
import pickle
import hashlib
from IPVerifier import InteractiveVerifier


class Proof:
    """
    A data structure representing offline proof of multilinear sum.
    """

    def __init__(self, poly: MVLinear, assertedSum: int, proverMessage: List[Tuple[int, int]]):
        self.prover_message: List[Tuple[int, int]] = copy(proverMessage)
        self.poly: MVLinear = copy(poly)  # todo: remove: change to be in theorem
        self.asserted_sum = assertedSum   # todo: remove: same


def randomElement(poly: MVLinear, proverMessage: List[Tuple[int, int]], byteLength: int = 512):
    sha = hashlib.sha512()  # todo: can change to blake (configurable)

    # append input: polynomial
    sha.update(pickle.dumps(poly))

    for msg_pair in proverMessage:
        p0 = msg_pair[0] % poly.p
        p1 = msg_pair[1] % poly.p

        sha.update(b'N')
        sha.update(p0.to_bytes(byteLength, 'little'))
        sha.update(b'X')
        sha.update(p1.to_bytes(byteLength, 'little'))

    result = int.from_bytes(sha.digest(), 'little') % poly.p  # approx correct
    # pick something small / rejection sampling (by pick the next power of 2)
    return result


def verifyProof(proof: Proof, byteLength: int = 512) -> bool:
    v = PseudoRandomVerifier(proof.poly, proof.asserted_sum, byteLength)
    for msg_pair in proof.prover_message:
        result, _ = v.talk(msg_pair[0], msg_pair[1])
        if not result:
            return False

    return v.convinced


class PseudoRandomVerifier(InteractiveVerifier):
    def __init__(self,  polynomial: MVLinear, asserted_sum: int, byteLength: int = 512):
        super().__init__(0, polynomial, asserted_sum)
        self.proverMessages: List[Tuple[int, int]] = []
        self.byteLength = byteLength

    def talk(self, p0: int, p1: int) -> Tuple[bool, int]:
        self.proverMessages.append((p0, p1))
        return super(PseudoRandomVerifier, self).talk(p0, p1)

    def randomR(self) -> int:
        return randomElement(self.poly, self.proverMessages, byteLength=self.byteLength)


# todo: next step
# todo: product of multilinear (start with 2 product)
# todo: case of sparse polynomial (2*n variables -> 2^(2n) monomials) (in this case, 2^n sparse monomials):
#  different algorithm
