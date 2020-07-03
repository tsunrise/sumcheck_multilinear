from copy import copy
from typing import List, Tuple

from polynomial import MVLinear
import pickle
import hashlib
from IPVerifier import InteractiveVerifier


class Theorem:
    """
    A data structure representing offline theorem of multilinear sum.
    """

    def __init__(self, poly: MVLinear, assertedSum: int):
        self.poly: MVLinear = copy(poly)
        self.asserted_sum = assertedSum


class Proof:
    """
    A data structure representing proof of a theorem.
    """

    def __init__(self, proverMessage: List[Tuple[int, int]]):
        self.prover_message = proverMessage


def randomElement(poly: MVLinear, proverMessage: List[Tuple[int, int]]) -> int:
    """
    Sample a random element in the field using hash function which takes the polynomial and prover message as input.
    :param poly: The polynomial
    :param proverMessage: List of Tuple of P(0), P(1)
    :return:
    """
    hash_size = (poly.p.bit_length() + 7) // 8
    byteLength = hash_size
    sha = hashlib.blake2b(pickle.dumps(poly), digest_size=hash_size)

    # append input: polynomial
    sha.update(pickle.dumps(poly))

    for msg_pair in proverMessage:
        p0 = msg_pair[0] % poly.p
        p1 = msg_pair[1] % poly.p

        sha.update(b'N')
        sha.update(p0.to_bytes(byteLength, 'little'))
        sha.update(b'X')
        sha.update(p1.to_bytes(byteLength, 'little'))

    result = int.from_bytes(sha.digest(), 'little')
    while result >= poly.p:
        sha.update(b'\xFF')  # rejection sampling
        result = int.from_bytes(sha.digest(), 'little')

    return result


def verifyProof(theorem: Theorem, proof: Proof) -> bool:
    v = PseudoRandomVerifier(theorem.poly, theorem.asserted_sum)
    for msg_pair in proof.prover_message:
        result, _ = v.talk(msg_pair[0], msg_pair[1])
        if not result:
            return False

    return v.convinced


class PseudoRandomVerifier(InteractiveVerifier):
    def __init__(self,  polynomial: MVLinear, asserted_sum: int):
        super().__init__(0, polynomial, asserted_sum)
        self.proverMessages: List[Tuple[int, int]] = []

    def talk(self, p0: int, p1: int) -> Tuple[bool, int]:
        self.proverMessages.append((p0, p1))
        return super(PseudoRandomVerifier, self).talk(p0, p1)

    def randomR(self) -> int:
        return randomElement(self.poly, self.proverMessages)


# todo: next step
# todo: product of multilinear (start with 2 product)
# todo: case of sparse polynomial (2*n variables -> 2^(2n) monomials) (in this case, 2^n sparse monomials):
#  different algorithm
