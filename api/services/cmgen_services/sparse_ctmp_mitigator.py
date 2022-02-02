from typing import List
import numpy as np
from qiskit.ignis.mitigation import CTMPExpvalMeasMitigator
import scipy.sparse as sps

# TODO This is currently inefficient and does not actually save memory
class SparseCTMPExpvalMeasMitigator(CTMPExpvalMeasMitigator):

    def mitigation_matrix(self, qubits: List[int] = None) -> np.ndarray:
        r"""Return the SPARSE measurement mitigation matrix for the specified qubits.

        The mitigation matrix :math:`A^{-1}` is defined as the inverse of the
        :meth:`assignment_matrix` :math:`A`.

        Args:
            qubits: Optional, qubits being measured for operator expval.

        Returns:
            np.ndarray: the measurement error mitigation matrix :math:`A^{-1}`.
        """
        # NOTE: the matrix definition of G is somehow flipped in both row and
        # columns compared to the canonical ordering for the A-matrix used
        # in the Complete and Tensored methods
        gmat = self.generator_matrix(qubits)
        gmat = sps.csr_matrix(gmat)
        sl = slice(None, None, -1)
        gmat = gmat[tuple([sl]*gmat.ndim)]
        return sps.linalg.expm(gmat)
        # gmat = np.flip(gmat.todense())
        # return la.expm(-gmat)