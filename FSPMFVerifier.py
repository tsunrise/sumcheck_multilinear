import hashlib
import pickle
import time
from copy import copy
from typing import List

from IPPMFVerifier import InteractivePMFVerifier, RandomGen
from PMF import PMF

MAX_SOUNDNESS_ERROR_ALLOWED = 2e-64


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
        self.prover_messge = proverMessage.copy()


class PseudoRandomGen(RandomGen):
    def __init__(self, poly: PMF):
        self.poly = poly
        self.message: List[List[int]] = []

    def getRandomElement(self) -> int:
        return randomElement(self.poly, self.message)


def verifyProof(theorem: Theorem, proof: Proof, maxAllowedSoundnessError: float = MAX_SOUNDNESS_ERROR_ALLOWED) -> bool:
    gen = PseudoRandomGen(theorem.poly)
    v = InteractivePMFVerifier(theorem.poly, theorem.asserted_sum, maxAllowedSoundnessError=maxAllowedSoundnessError,
                               randomGen=gen)
    for msg in proof.prover_messge:
        gen.message.append(msg)
        v.talk(msg)
    return v.convinced
