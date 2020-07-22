from enum import Enum
import random
from typing import List, Optional, Tuple

from GKR import GKR
from IPPMFVerifier import InteractivePMFVerifier
from PMF import PMF, MVLinear
from multilinear_extension import evaluate, evaluate_sparse

class GKRVerifierState(Enum):
    PHASE_ONE_LISTENING = 1   # verify on x (L variables)
    PHASE_TWO_LISTENING = 2   # verify on y (L variables)
    ACCEPT = 3
    REJECT = 0


class GKRVerifier:
    """
    An interactive verifier verifying the sum of GKR protocol.
    """
    def __init__(self, gkr: GKR, g: List[int], asserted_sum: int):
        self.state: GKRVerifierState = GKRVerifierState.PHASE_ONE_LISTENING
        assert len(g) == gkr.L, "g should have same size as number of variables in f2 or f3"
        self.f1 = gkr.f1
        self.f2 = gkr.f2
        self.f3 = gkr.f3
        self.g = g
        self.p = gkr.p
        L = self.f2.num_variables
        self.L = L
        self.asserted_sum = asserted_sum
        # Phase 1 verifier: product of h_g (no need for verifier to multiply) and f2 (no need to access)
        # we put dummy polynomial here because the subroutine verifier does not evaluate h_g and f2: it just check the
        # sum.
        self.phase1_verifier: InteractivePMFVerifier = InteractivePMFVerifier(random.randint(1, 0xFFFFFFFFFFFFFFFF),
                                                      PMF([MVLinear(2*L, {0: 0}, self.p), MVLinear(L, {0: 0}, self.p)]),
                                                      asserted_sum=asserted_sum, checksum_only=True)
        # phase 1 verifier generate sub claim u and its evaluation of product of h_g and f2 on x = u

        # phase 2 verifier: product of f1 at x = u and f3 times f2(u)
        # In phased two, it checks sum for y, and the asserted_sum is the sub-claim outputted by the previous verifier.
        # In current state, it is None, because the verifier not yet to know the sub claim.
        self.phase2_verifier: Optional[InteractivePMFVerifier] = None

    def talk_phase1(self, msgs: List[int]) -> Tuple[bool, int]:
        if self.state != GKRVerifierState.PHASE_ONE_LISTENING:
            raise RuntimeError("Verifier is not in phase 1.")
        _, r = self.phase1_verifier.talk(msgs)

        if self.phase1_verifier.convinced:
            L = self.L
            self.phase2_verifier = InteractivePMFVerifier(random.randint(1, 0xFFFFFFFFFFFFFFFF),
                                                          PMF([MVLinear(L, {0: 0}, self.p),
                                                               MVLinear(L, {0: 0}, self.p)]),  # dummy
                                                          asserted_sum=self.phase1_verifier.sub_claim()[1],
                                                          checksum_only=True)
            self.state = GKRVerifierState.PHASE_TWO_LISTENING
            return True, r
        if (not self.phase1_verifier.active) and (not self.phase1_verifier.convinced):
            self.state = GKRVerifierState.REJECT
            return False, r
        return True, r

    def talk_phase2(self, msgs: List[int]) -> Tuple[bool, int]:
        if self.state != GKRVerifierState.PHASE_TWO_LISTENING:
            raise RuntimeError("Verifier is not in phase 2.")
        _, r = self.phase2_verifier.talk(msgs)
        if self.phase2_verifier.convinced:
            return self._verdict(), r
        if (not self.phase2_verifier.active) and (not self.phase2_verifier.convinced):
            self.state = GKRVerifierState.REJECT
            return False, r
        return True, r

    def _verdict(self) -> bool:
        """
        Verify the sub claim of verifier 2, using the u from sub claim 1 and v from sub claim 2.
        This requires three polynomial evaluation.
        :return:
        """
        if self.state != GKRVerifierState.PHASE_TWO_LISTENING:
            raise RuntimeError("Verifier is not in phase 2.")
        if not self.phase2_verifier.convinced:
            raise RuntimeError("Phase 2 verifier is not convinced.")
        u = self.phase1_verifier.sub_claim()[0]     # x
        v = self.phase2_verifier.sub_claim()[0]     # y

        # verify phase 2 verifier's claim
        m1 = evaluate_sparse(self.f1, self.g+u+v, self.p)       # self.f1.eval(u+v)
        m2 = evaluate(self.f3, v, self.p) * evaluate(self.f2, u, self.p) % self.p
        # self.f3.eval(v) * self.f2.eval(u) % self.p

        expected = m1*m2 % self.p

        if (self.phase2_verifier.sub_claim()[1] - expected) % self.p != 0:
            self.state = GKRVerifierState.REJECT
            return False
        self.state = GKRVerifierState.ACCEPT
        return True


