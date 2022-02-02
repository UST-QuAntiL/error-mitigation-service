from abc import ABC, abstractmethod
from qiskit.ignis.mitigation import complete_meas_cal, CompleteMeasFitter
import qiskit.ignis.mitigation as mit

# from api.services.cmgen_services.sparse_fitter import SparseExpvalMeasMitigatorFitter


class CircuitGenerator(ABC):
    @abstractmethod
    def generate_cm_circuits(self, qubits):
        pass

    def compute_cm(self, results, labels):
        pass

class StandardCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits
        circuits, state_labels = complete_meas_cal(qr=len(qubits), circlabel='mcal')
        return circuits, state_labels

    def compute_cm(self, results, labels):
        meas_fitter = CompleteMeasFitter(results, labels, circlabel='mcal')
        return meas_fitter.cal_matrix


class TPNMCMGenerator(CircuitGenerator):

    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits
        circuits, state_labels = mit.expval_meas_mitigator_circuits(qubits.size, method='tensored')
        return circuits, state_labels

    def compute_cm(self, results, labels, sparsity = 1e-5):
        mitigator_tensored = SparseExpvalMeasMitigatorFitter(results, labels).fit()
        return mitigator_tensored.mitigation_matrix(sparsity_factor=sparsity)


class CTMPCMGenerator(CircuitGenerator):

    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits
        circuits, state_labels = mit.expval_meas_mitigator_circuits(qubits.size, method='CTMP')
        return circuits, state_labels

    def compute_cm(self, results, labels):
        mitigator_ctmp = mit.ExpvalMeasMitigatorFitter(results, labels).fit()
        return mitigator_ctmp.assignment_matrix()


class MthreeCMGenerator(CircuitGenerator):

    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits, TODO check setup
        mit = mthree.M3Mitigation(backend)
        mit.cals_from_system(qubits, shots)
        return mit

    def compute_cm(self, results, labels):
        meas_fitter = CompleteMeasFitter(results, labels, circlabel='mcal')
        return meas_fitter.cal_matrix
