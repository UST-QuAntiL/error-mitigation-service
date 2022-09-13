from abc import ABC, abstractmethod
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.ignis.mitigation import tensored_meas_cal
import qiskit.ignis.mitigation as mit

from app.services.cmgen_services.sparse_fitter import SparseExpvalMeasMitigatorFitter
from app.utils.helper_functions import ResultsMock


class CircuitGenerator(ABC):
    def __init__(self):
        self.labels = None

    @abstractmethod
    def generate_cm_circuits(self, qubits):
        pass

    def compute_cm(self, counts):
        pass


class StandardCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        self.labels = [bin(j)[2:].zfill(len(qubits)) for j in range(2 ** len(qubits))]
        circuits, _ = tensored_meas_cal([qubits], circlabel="mcal")
        return circuits

    def compute_cm(self, counts):
        num_qubits = len(list(counts[0].keys())[0])
        matrix = np.zeros((2 ** num_qubits, 2 ** num_qubits))
        shots = np.sum(list(counts[0].values()))
        if self.labels is None:
            self.labels = [bin(j)[2:].zfill(num_qubits) for j in range(2 ** num_qubits)]
        for i, column in enumerate(counts):
            for j, bitstring in enumerate(self.labels):
                if bitstring in column:
                    matrix[j, i] = column[bitstring] / shots
        return matrix


class TPNMCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        circuit_size = max(qubits)
        qr = QuantumRegister(circuit_size + 1)
        cr = ClassicalRegister(len(qubits))
        qc0 = QuantumCircuit(qr, cr)
        qc1 = QuantumCircuit(qr, cr)
        for e, i in enumerate(qubits):
            qc1.x(i)
            qc0.measure(qr[i], cr[e])
            qc1.measure(qr[i], cr[e])

        circuits = [qc0, qc1]
        self.labels = [
            {"experiment": "meas_mit", "cal": "0" * len(qubits), "method": "tensored"},
            {"experiment": "meas_mit", "cal": "1" * len(qubits), "method": "tensored"},
        ]
        return circuits

    def compute_cm(self, counts):
        if self.labels is None:
            num_qubits = len(list(counts[0].keys())[0])
            self.labels = [
                {
                    "experiment": "meas_mit",
                    "cal": "0" * num_qubits,
                    "method": "tensored",
                },
                {
                    "experiment": "meas_mit",
                    "cal": "1" * num_qubits,
                    "method": "tensored",
                },
            ]
        counts = ResultsMock(counts)
        mitigator_tensored = mit.ExpvalMeasMitigatorFitter(counts, self.labels).fit()
        return mitigator_tensored.assignment_matrix()

    def compute_mm(self, counts, sparsity=1e-5):
        counts = ResultsMock(counts)
        mitigator_tensored = SparseExpvalMeasMitigatorFitter(counts, self.labels).fit()
        return mitigator_tensored.mitigation_matrix(sparsity_factor=sparsity)


class CTMPCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits
        circuits, state_labels = mit.expval_meas_mitigator_circuits(
            qubits.size, method="CTMP"
        )
        self.labels = state_labels
        return circuits

    def compute_cm(self, counts):
        counts = ResultsMock(counts)
        mitigator_ctmp = mit.ExpvalMeasMitigatorFitter(counts, self.labels).fit()
        return mitigator_ctmp.assignment_matrix()

    def compute_mm(self, counts):
        counts = ResultsMock(counts)
        mitigator_ctmp = SparseExpvalMeasMitigatorFitter(counts, self.labels).fit()
        return mitigator_ctmp.mitigation_matrix()
