from typing import List, Tuple

from PMF import PMF
from IPPMFProver import InteractivePMFProver
from FSPMFVerifier import PseudoRandomPMFVerifier, Theorem, Proof

MAX_SOUNDNESS_ERROR_ALLOWED = 2e-64


def generateTheoremAndProof(poly: PMF, maxAllowedSoundnessError=MAX_SOUNDNESS_ERROR_ALLOWED)\
        -> Tuple[Theorem, Proof, PseudoRandomPMFVerifier]:
    """
    Generate the theorem (poly itself and the asserted sum) and its proof.
    :param maxAllowedSoundnessError:
    :param poly: The PMF polynomial
    :return: theorem, proof, and the (hopefully) convinced pseudorandom verifier
    """
    pv = InteractivePMFProver(poly)
    As, s = pv.calculateAllBookKeepingTables()

    v = PseudoRandomPMFVerifier(poly, s, maxAllowedSoundnessError=maxAllowedSoundnessError)
    pv.attemptProve(As, v)

    theorem = Theorem(poly, s)
    proof = Proof(v.proverMessages)

    return theorem, proof, v

