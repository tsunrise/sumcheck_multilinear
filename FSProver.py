from FSVerifier import Proof, PseudoRandomVerifier
from IPProverLinear import InteractiveLinearProver
from polynomial import MVLinear


def generateProof(poly: MVLinear) -> Proof:
    """
    Generate an offline proof of the multilinear polynomial sum.
    :param poly: The multilinear poly to be looked at.
    :return: The offline proof.
    """
    prover = InteractiveLinearProver(poly)  # run verifier by itself
    A, s = prover.calculateTable()
    v = PseudoRandomVerifier(poly, s)
    prover.attemptProve(A, v)

    assert v.convinced

    msgs = v.proverMessages
    return Proof(poly, s, msgs)

