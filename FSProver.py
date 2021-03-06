from typing import Tuple

from FSVerifier import Theorem, PseudoRandomVerifier, Proof
from IPProverLinear import InteractiveLinearProver
from polynomial import MVLinear


def generateTheoremAndProof(poly: MVLinear, maximumAllowedSoundnessError: float = 2**(-32)) -> Tuple[Theorem, Proof]:
    """
    Generate an offline proof of the multilinear polynomial sum.
    :param poly: The multilinear poly to be looked at.
    :param maximumAllowedSoundnessError: maximum soundness error
    :return: The offline proof.
    """
    prover = InteractiveLinearProver(poly)  # run verifier by itself
    A, s = prover.calculateTable()
    v = PseudoRandomVerifier(poly, s, maximumAllowedSoundnessError)
    prover.attemptProve(A, v)

    assert v.convinced

    msgs = v.proverMessages
    return Theorem(poly, s), Proof(msgs)

