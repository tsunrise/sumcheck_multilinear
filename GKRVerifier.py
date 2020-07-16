from enum import Enum
import random
from typing import List, Optional, Tuple

from GKR import GKR
from IPPMFVerifier import InteractivePMFVerifier
from PMF import PMF, MVLinear


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
        assert len(g) == gkr.f2.num_variables
        self.f1 = gkr.f1.eval_part(g)   # f1(x,y) = gkr.f1(g, x, y)
        self.f2 = gkr.f2
        self.f3 = gkr.f3
        self.p = self.f1.p
        L = self.f2.num_variables
        self.L = L
        # we put dummy polynomial here because the subroutine verifier does not evaluate h_g and f2: it just check the
        # sum.
        self.phase1_verifier: InteractivePMFVerifier = InteractivePMFVerifier(random.randint(1, 0xFFFFFFFFFFFFFFFF),
                                                      PMF([MVLinear(2*L, {0:0}, self.p), MVLinear(L, {0:0}, self.p)]),
                                                      asserted_sum=asserted_sum, checksum_only=True)

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
                                                          PMF([MVLinear(L, {0:0}, self.p),
                                                               MVLinear(L, {0:0}, self.p)]),
                                                          asserted_sum=self.phase1_verifier.sub_claim()[1],
                                                          checksum_only=True)
            self.state = GKRVerifierState.PHASE_TWO_LISTENING
            return True, r
        if (not self.phase1_verifier.active) and (not self.phase1_verifier.convinced):
            self.state = GKRVerifierState.REJECT
            return False, r
        return True, r

    def talk_phase2(self, msgs: List[int]) -> Tuple[bool, int]:
        # todo
        ...

        if self.phase2_verifier.convinced:
            self.verdict()
            ...

    def verdict(self) -> bool:
        """
        Verify the sub claim of verifier 2, using the u from sub claim 1 and v from sub claim 2.
        This requires one polynomial evaluation.
        :return:
        """
        # todo
        ...
