from abc import ABC, abstractmethod

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.ignis.mitigation import CompleteMeasFitter, tensored_meas_cal
import qiskit.ignis.mitigation as mit
from sympy.physics.units import bits

from app.services.cmgen_services.sparse_fitter import SparseExpvalMeasMitigatorFitter
from app.utils.helper_functions import ResultsMock


class CircuitGenerator(ABC):
    @abstractmethod
    def generate_cm_circuits(self, qubits):
        pass

    def compute_cm(self, counts):
        pass


class StandardCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        state_labels = [bin(j)[2:].zfill(len(qubits)) for j in range(2 ** len(qubits))]
        circuits, _ = tensored_meas_cal([qubits], circlabel="mcal")
        return circuits

    def compute_cm(self, counts):
        num_qubits = len(list(counts[0].keys())[0])
        matrix = np.zeros((2 ** num_qubits, 2 ** num_qubits))
        shots = np.sum(list(counts[0].values()))
        state_labels = [bin(j)[2:].zfill(num_qubits) for j in range(2 ** num_qubits)]
        for i, column in enumerate(counts):
            for j, bitstring in enumerate(state_labels):
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
        return circuits

    def compute_cm(self, counts):
        qubits = len(list(counts[0].keys())[0])
        state_labels = [
            {"experiment": "meas_mit", "cal": "0" * qubits, "method": "tensored"},
            {"experiment": "meas_mit", "cal": "1" * qubits, "method": "tensored"},
        ]
        counts = ResultsMock(counts)
        mitigator_tensored = mit.ExpvalMeasMitigatorFitter(counts, state_labels).fit()
        return mitigator_tensored.assignment_matrix()

    def compute_sparse_mm(self, counts, labels, sparsity=1e-5):
        counts = ResultsMock(counts)
        mitigator_tensored = SparseExpvalMeasMitigatorFitter(counts, labels).fit()
        return mitigator_tensored.mitigation_matrix(sparsity_factor=sparsity)


class CTMPCMGenerator(CircuitGenerator):
    def generate_cm_circuits(self, qubits):
        # TODO choose correct qubits
        circuits, state_labels = mit.expval_meas_mitigator_circuits(
            qubits.size, method="CTMP"
        )
        return circuits, state_labels

    def compute_cm(self, counts):
        qubits = len(list(counts[0].keys())[0])
        state_labels = [
            {"experiment": "meas_mit", "cal": "0" * qubits, "method": "tensored"},
            {"experiment": "meas_mit", "cal": "1" * qubits, "method": "tensored"},
        ]
        mitigator_ctmp = mit.ExpvalMeasMitigatorFitter(counts, state_labels).fit()
        return mitigator_ctmp.assignment_matrix()


if __name__ == "__main__":
    generator = TPNMCMGenerator()
    generator = StandardCMGenerator()
    generator.generate_cm_circuits([3, 1, 4, 5, 8])
