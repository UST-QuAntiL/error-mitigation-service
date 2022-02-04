from abc import ABC, abstractmethod
from qiskit.ignis.mitigation import complete_meas_cal, CompleteMeasFitter
import qiskit.ignis.mitigation as mit
import numpy as np
# from api.services.cmgen_services.sparse_fitter import SparseExpvalMeasMitigatorFitter


class MitigationGenerator(ABC):
    @abstractmethod
    def generate_mitigator(self, cm, *kwargs):
        pass


class MatrixInversion(MitigationGenerator):
    def generate_mitigator(self, cm, **kwargs):

        return np.linalg.inv(cm)




