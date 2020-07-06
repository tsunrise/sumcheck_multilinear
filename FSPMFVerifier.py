import hashlib
import pickle
from copy import copy
from typing import List

from IPPMFVerifier import InteractivePMFVerifier
from PMF import PMF


def randomElement(poly: PMF, proverMessage: List[List[int]]) -> int:
    """
    Sample a random element in the field using hash function which takes the polynomial and prover message as input.
    :param poly: The polynomial
    :param proverMessage: List of messages [P(0), P(1), P(2), ..., P(m)]
    :return:
    """
    hash_size = (poly.p.bit_length() + 7) // 8
    byteLength = hash_size
    sha = hashlib.blake2b(pickle.dumps(poly), digest_size=hash_size)

    # append input: polynomial
    sha.update(pickle.dumps(poly))

    for msg in proverMessage:
        for point in msg:
            sha.update(b'N')
            sha.update(point.to_bytes(byteLength, 'little'))
        sha.update(b'X')

    result = int.from_bytes(sha.digest(), 'little')
    while result >= poly.p:
        sha.update(b'\xFF')  # rejection sampling
        result = int.from_bytes(sha.digest(), 'little')

    return result


class Theorem:
    """
    A data structure representing offline theorem of PMF sum.
    """

    def __init__(self, poly: PMF, assertedSum: int):
        self.poly = copy(poly)
        self.asserted_sum = assertedSum


class Proof:
    """
    A data structure representing proof of a theorem.
    """

    def __init__(self, proverMessage: List[List[int]]):
        self.prover_messge = proverMessage


def verifyProof(theorem: Theorem, proof: Proof) -> bool:
    v = PseudoRandomPMFVerifier(theorem.poly, theorem.asserted_sum)
    for msg in proof.prover_messge:
        v.talk(msg)
    return v.convinced


class PseudoRandomPMFVerifier(InteractivePMFVerifier):
    def __init__(self, polynomial: PMF, asserted_sum: int):
        super().__init__(0, polynomial, asserted_sum)
        self.proverMessages: List[List[int]] = []

    def talk(self, msgs: List[int]):
        self.proverMessages.append(copy(msgs))
        return super(PseudoRandomPMFVerifier, self).talk(msgs)

    def randomR(self) -> int:
        return randomElement(self.poly, self.proverMessages)


