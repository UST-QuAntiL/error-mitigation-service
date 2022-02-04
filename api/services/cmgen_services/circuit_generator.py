from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.tools.visualization import circuit_drawer
from qiskit.ignis.mitigation import complete_meas_cal, CompleteMeasFitter, tensored_meas_cal
import qiskit.ignis.mitigation as mit
# import mthree
# from api.services.cmgen_services.sparse_fitter import SparseExpvalMeasMitigatorFitter
from api.services.cmgen_services.sparse_fitter import SparseExpvalMeasMitigatorFitter


class CircuitGenerator(ABC):
    @abstractmethod
    def generate_cm_circuits(self, qubits):
        pass

    def compute_cm(self, results, labels):
        pass

class StandardCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits
        state_labels = [bin(j)[2:].zfill(len(qubits)) for j in range(2 ** len(qubits))]
        circuits, _ = tensored_meas_cal([qubits], circlabel='mcal')
        return circuits, state_labels

    def compute_cm(self, results, labels):
        meas_fitter = CompleteMeasFitter(results, labels, circlabel='mcal')
        return meas_fitter.cal_matrix


class TPNMCMGenerator(CircuitGenerator):

    def generate_cm_circuits(self, qubits):
        circuit_size = max(qubits)
        qr = QuantumRegister(circuit_size+ 1)
        cr = ClassicalRegister(len(qubits))
        qc0 = QuantumCircuit(qr, cr)
        qc1 = QuantumCircuit(qr, cr)
        for e,i in enumerate(qubits):
            qc1.x(i)
            qc0.measure(qr[i],cr[e])
            qc1.measure(qr[i],cr[e])

        circuits = [qc0, qc1]
        state_labels = [{'experiment': 'meas_mit', 'cal': '0'*len(qubits), 'method': 'tensored'}, {'experiment': 'meas_mit', 'cal': '1'*len(qubits), 'method': 'tensored'}]
        return circuits, state_labels

    def compute_cm(self, results, labels):
        mitigator_tensored = mit.ExpvalMeasMitigatorFitter(results, labels).fit()
        return mitigator_tensored.assignment_matrix()

    def compute_sparse_mm(self, results, labels, sparsity = 1e-5):
        mitigator_tensored = SparseExpvalMeasMitigatorFitter(results, labels).fit()
        # return mitigator_tensored.mitigation_matrix(sparsity_factor=sparsity)
        return mitigator_tensored.mitigation_matrix(sparsity_factor=1e-4)


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

if __name__ == "__main__":
    generator = TPNMCMGenerator()
    generator.generate_cm_circuits([1,4,5,8])