from typing import List, Tuple

from PMF import PMF
from IPPMFProver import InteractivePMFProver
from FSPMFVerifier import PseudoRandomPMFVerifier, Theorem, Proof


def generateTheoremAndProof(poly: PMF) -> Tuple[Theorem, Proof]:
    """
    Generate the theorem (poly itself and the asserted sum) and its proof.
    :param poly: The PMF polynomial
    :return: theorem and proof
    """
    pv = InteractivePMFProver(poly)
    As, s = pv.calculateAllBookKeepingTables()

    v = PseudoRandomPMFVerifier(poly, s)
    pv.attemptProve(As, v)

    theorem = Theorem(poly, s)
    proof = Proof(v.proverMessages)

    return theorem, proof

