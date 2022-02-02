from abc import ABC, abstractmethod
import numpy as np



class MitigationApplication(ABC):
    @abstractmethod
    def appyl_mitigation(self, mitigator, **kwargs):
        pass


class MatrixMultiplication(MitigationApplication):
    def appyl_mitigation(self, mitigator, **kwargs):
        return list(np.matmul(mitigator, kwargs['counts']))




