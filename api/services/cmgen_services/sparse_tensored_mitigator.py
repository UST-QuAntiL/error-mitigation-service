from typing import List
import numpy as np
from scipy import sparse
import psutil

from qiskit.ignis.mitigation import TensoredExpvalMeasMitigator

"""
Extend qiskit method to obtain a sparse, exponentially more memmory efficient tensored mitigation matrix
"""
class SparseTensoredExpvalMeasMitigator(TensoredExpvalMeasMitigator):
    def mitigation_matrix(self, qubits: List[int] = None, sparsity_factor = 1e-3) -> np.ndarray:
        """Return the SPARSE measurement mitigation matrix for the specified qubits.

        The mitigation matrix :math:`A^{-1}` is defined as the inverse of the
        :meth:`assignment_matrix` :math:`A`.

        Args:
            qubits: Optional, qubits being measured for operator expval.

        Returns:
            np.ndarray: the measurement error mitigation matrix :math:`A^{-1}`.
        """
        if qubits is None:
            qubits = list(range(self._num_qubits))
        if isinstance(qubits, int):
            qubits = [qubits]
        mat = self._mitigation_mats[qubits[0]]
        for i in qubits[1:]:
            if i > 3:
                mask = np.abs(mat.data)<= sparsity_factor
                mat.data[mask]=0
                mat.eliminate_zeros()
            # print(mat.shape)
            # print(mat.data.nbytes)
            if(psutil.virtual_memory().total < mat.data.nbytes * np.count_nonzero(self._mitigation_mats[qubits[i]])):
                print("Calculating the full calibration matrix would require {} available memory; The system memory size is: {}".format(2**(self._mitigation_mats[qubits[i]]),psutil.virtual_memory().total))
                raise Exception("Memory exceeded")
            mat = sparse.kron(self._mitigation_mats[qubits[i]], mat, "csr")

        mask = np.abs(mat.data) <= sparsity_factor
        mat.data[mask]=0
        mat.eliminate_zeros()
        return mat