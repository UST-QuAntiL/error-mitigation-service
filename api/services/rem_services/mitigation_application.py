from abc import ABC, abstractmethod
import numpy as np
# from mthree import M3Mitigation


class MitigationApplication(ABC):
    @abstractmethod
    def appyl_mitigation(self, mitigator, **kwargs):
        pass


class MatrixMultiplication(MitigationApplication):
    def appyl_mitigation(self, mitigator, **kwargs):
        return list(np.matmul(mitigator, kwargs['counts']))

class Mthree(MitigationApplication):
    def appyl_mitigation(self, mitigator, **kwargs):
        result = mitigator.apply_correction(kwargs['counts'], kwargs['qubits'], distance=10)
        n_qubits = len(kwargs['qubits'])
        prob_dist_dict = result.nearest_probability_distribution()
        y = np.zeros(2 ** n_qubits, dtype=int)
        for i in range(2 ** n_qubits):
            number = "0" * (n_qubits - 1 - int(np.log2(i)) if i > 0 else n_qubits - 1) + bin(i)[2:]
            if prob_dist_dict.__contains__(
                    "0" * (n_qubits - 1 - int(np.log2(i)) if i > 0 else n_qubits - 1) + bin(i)[2:]):
                y[i] = prob_dist_dict["0" * (n_qubits - 1 - int(np.log2(i)) if i > 0 else n_qubits - 1) + bin(i)[
                                                                                                          2:]] * result.shots
        return y



