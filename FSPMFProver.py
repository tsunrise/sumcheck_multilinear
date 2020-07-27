from typing import Tuple

from IPPMFVerifier import InteractivePMFVerifier
from PMF import PMF
from IPPMFProver import InteractivePMFProver
from FSPMFVerifier import Theorem, Proof
from FSPMFVerifier import PseudoRandomGen
MAX_SOUNDNESS_ERROR_ALLOWED = 2e-64


def generateTheoremAndProof(poly: PMF, maxAllowedSoundnessError=MAX_SOUNDNESS_ERROR_ALLOWED)\
        -> Tuple[Theorem, Proof, InteractivePMFVerifier]:
    """
    Generate the theorem (poly itself and the asserted sum) and its proof.
    :param maxAllowedSoundnessError:
    :param poly: The PMF polynomial
    :return: theorem, proof, and the (hopefully) convinced pseudorandom verifier
    """
    pv = InteractivePMFProver(poly)
    As, s = pv.calculateAllBookKeepingTables()

    gen = PseudoRandomGen(poly)
    v = InteractivePMFVerifier(poly, s, maxAllowedSoundnessError=maxAllowedSoundnessError, randomGen=gen)
    msgs = pv.attemptProve(As, v, gen=gen)

    theorem = Theorem(poly, s)
    proof = Proof(msgs)

    return theorem, proof, v

