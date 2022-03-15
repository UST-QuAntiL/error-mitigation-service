from abc import ABC, abstractmethod

import mthree
import numpy as np
from scipy.optimize import minimize

from api.utils.helper_functions import array_to_dict, dict_to_array
from api.model.matrix_types import MatrixType


class MitigationApplication(ABC):
    @property
    def requires(self):
        raise NotImplementedError


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

    requires = MatrixType.mm


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

    requires = MatrixType.mm

class IterativeBayesApplication(MitigationApplication):
    def appyl_mitigation(self, cm, **kwargs):
        n_qubits= len( kwargs['qubits'])
        counts = kwargs['counts']
        counts = np.array(dict_to_array(counts, n_qubits))
        tn_new = np.sum(counts)/len(counts)*np.ones(counts.shape)
        tn = np.zeros(counts.shape)
        n =0
        while(np.linalg.norm(tn_new-tn)>np.linalg.norm(counts)/300):
            tn = tn_new
            multiplicator = counts/(np.matmul(cm, tn))
            multiplicator[np.matmul(cm, tn) == 0]=0
            tn_new = np.matmul(cm.T, multiplicator) * tn
            n=n+1
        #print(n)
        return array_to_dict(tn_new, n_qubits)

    requires = MatrixType.cm

class IgnisUnfoldingApplication(MitigationApplication):

    def fun(self, x, y, R):
        mat_dot_x = np.ravel(np.matmul(R, x))
        return sum((y - mat_dot_x) ** 2)

    def appyl_mitigation(self, cm, **kwargs):
        n_qubits = len(kwargs['qubits'])
        counts = kwargs['counts']
        counts = np.array(dict_to_array(counts, n_qubits))

        x0 = np.random.rand(len(counts))
        x0 = x0 / sum(x0)
        nshots = sum(counts)
        cons = ({'type': 'eq', 'fun': lambda x: nshots - sum(x)})
        bnds = tuple((0, nshots) for x in x0)
        res = minimize(self.fun, x0, method='SLSQP', constraints=cons, bounds=bnds, tol=1e-5, args=(counts, cm))
        return array_to_dict(res.x, n_qubits)

    requires = MatrixType.cm





