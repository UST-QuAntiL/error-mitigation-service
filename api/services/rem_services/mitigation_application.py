from abc import ABC, abstractmethod

import mthree
import numpy as np
from api.utils.helper_functions import array_to_dict, dict_to_array


class MitigationApplication(ABC):
    @abstractmethod
    def appyl_mitigation(self, mitigator, **kwargs):
        pass


class MatrixMultiplication(MitigationApplication):
    def appyl_mitigation(self, mitigator, **kwargs):
        n_qubits = len(kwargs['qubits'])
        counts = kwargs['counts']
        array_counts = dict_to_array(counts,n_qubits)
        res = list(np.matmul(mitigator, array_counts))
        return array_to_dict(res,n_qubits)


class MthreeApplication(MitigationApplication):
    def appyl_mitigation(self, mitigator, **kwargs):
        mit = mthree.M3Mitigation()
        mit.cals_from_matrices(mitigator)


        # result = mitigator.apply_correction(kwargs['counts'], kwargs['qubits'], distance=10)
        print(kwargs['counts'], kwargs['qubits'])
        counts= kwargs['counts']
        qubits=kwargs['qubits']

        result = mit.apply_correction(counts, qubits)

        newdict = {}
        for key, value in result.nearest_probability_distribution().items():
            newdict[key] = int(value * result.shots)
        mit_counts = newdict

        return mit_counts



