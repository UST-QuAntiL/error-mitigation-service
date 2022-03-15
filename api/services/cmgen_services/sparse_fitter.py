from typing import List, Optional, Generator, Union
from qiskit import QiskitError
from qiskit.ignis.mitigation.expval.ctmp_fitter import fit_ctmp_meas_mitigator
from qiskit.ignis.mitigation.expval.utils import assignment_matrix

from qiskit.ignis.mitigation import ExpvalMeasMitigatorFitter, CompleteExpvalMeasMitigator, CTMPExpvalMeasMitigator

from api.services.cmgen_services.sparse_tensored_mitigator import SparseTensoredExpvalMeasMitigator


class SparseExpvalMeasMitigatorFitter(ExpvalMeasMitigatorFitter):
    def fit(self, method: Optional[str] = None,
            generators: Optional[List[Generator]] = None) -> Union[
        CompleteExpvalMeasMitigator,
        SparseTensoredExpvalMeasMitigator,
        CTMPExpvalMeasMitigator]:
        """Fit and return the Mitigator object from the calibration data."""

        if method is None:
            method = self._method

        if method == 'complete':
            # Construct A-matrix from calibration data
            amat = assignment_matrix(self._cal_data, self._num_qubits)
            self._mitigator = CompleteExpvalMeasMitigator(amat)

        elif method == 'tensored':
            # Construct single-qubit A-matrices from calibration data
            amats = []
            for qubit in range(self._num_qubits):
                amat = assignment_matrix(self._cal_data, self._num_qubits, [qubit])
                amats.append(amat)
            self._mitigator = SparseTensoredExpvalMeasMitigator(amats)

        elif method in ['CTMP', 'ctmp']:
            self._mitigator = fit_ctmp_meas_mitigator(
                self._cal_data, self._num_qubits, generators)
        else:
            raise QiskitError(
                "Invalid expval measurement error mitigation method {}".format(method))
        return self._mitigator
