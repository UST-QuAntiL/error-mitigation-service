from abc import ABC, abstractmethod
import numpy as np



class MitigationGenerator(ABC):
    @abstractmethod
    def generate_mitigator(self, cm, *kwargs):
        pass


class MatrixInversion(MitigationGenerator):
    def generate_mitigator(self, cm, **kwargs):

        return np.linalg.inv(cm)

