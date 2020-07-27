"""
Trivial Fiat Shemir GKR Protocol.
"""
import hashlib
import pickle
from copy import copy
from typing import List, Tuple

from GKR import GKR
from GKRProver import GKRProver
from GKRVerifier import GKRVerifier, GKRVerifierState
from IPPMFVerifier import RandomGen



class Theorem:
    def __init__(self, gkr: GKR, g: List[int], assertedSum: int):
        self.gkr: GKR = copy(gkr)
        self.g: List[int] = g
        assert len(self.g) == self.gkr.L
        self.assertedSum = assertedSum


class Proof:
    def __init__(self, phase1Msg:  List[List[int]], phase2Msg: List[List[int]]):
        self.phase1Msg = phase1Msg.copy()
        self.phase2Msg = phase2Msg.copy()

def getGKRHash(gkr: GKR) -> bytes:
    hash_size = 64
    sha = hashlib.blake2b(pickle.dumps(gkr), digest_size=hash_size)
    return sha.digest()

def randomElement(gkrHash: bytes, phase1Msg: List[List[int]], phase2Msg: List[List[int]], p: int):
    hash_size = (p.bit_length() + 7) // 8
    byteLength = hash_size
    sha = hashlib.blake2b(gkrHash, digest_size=hash_size)

    for msg in phase1Msg:
        for point in msg:
            sha.update(b'N')
            sha.update(point.to_bytes(byteLength, 'little'))
        sha.update(b'X')

    for msg in phase2Msg:
        for point in msg:
            sha.update(b'N')
            sha.update(point.to_bytes(byteLength, 'little'))
        sha.update(b'X')

    result = int.from_bytes(sha.digest(), 'little')
    while result >= p:
        sha.update(b'\xFF')  # rejection sampling
        result = int.from_bytes(sha.digest(), 'little')

    return result


class PseudoRandomGen(RandomGen):
    def __init__(self, gkrHash: bytes, p: int):
        self.gkrHash: bytes = gkrHash
        self.phase1MsgRecorder: List[List[int]] = []  # mutable on fly
        self.phase2MsgRecorder: List[List[int]] = []  # mutable on fly
        self.p = p

    def getRandomElement(self):
        return randomElement(self.gkrHash, self.phase1MsgRecorder, self.phase2MsgRecorder, self.p)

def verifyProof(thm: Theorem, pf: Proof)->bool:
    gen = PseudoRandomGen(getGKRHash(thm.gkr), thm.gkr.p)
    v = GKRVerifier(thm.gkr, thm.g, thm.assertedSum, gen)
    for msg in pf.phase1Msg:
        gen.phase1MsgRecorder.append(msg)
        v.talk_phase1(msg)
        if v.state == GKRVerifierState.REJECT:
            return False
    for msg in pf.phase2Msg:
        gen.phase2MsgRecorder.append(msg)
        v.talk_phase2(msg)
        if v.state == GKRVerifierState.REJECT:
            return False
    return v.state == GKRVerifierState.ACCEPT

def generateTheoremAndProof(gkr: GKR, g: List[int]) -> Tuple[Theorem, Proof]:
    pv = GKRProver(gkr)
    A_hg, G, s = pv.initializeAndGetSum(g)

    thm = Theorem(gkr, g, s)
    gen = PseudoRandomGen(getGKRHash(gkr), gkr.p)
    v = GKRVerifier(gkr, g, s, gen)
    pv.proveToVerifier(A_hg, G, s, v, gen.phase1MsgRecorder, gen.phase2MsgRecorder)

    assert v.state == GKRVerifierState.ACCEPT
    pf = Proof(gen.phase1MsgRecorder, gen.phase2MsgRecorder)

    return thm, pf



