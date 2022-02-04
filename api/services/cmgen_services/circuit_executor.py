from abc import ABC, abstractmethod

from qiskit import IBMQ, execute
from qiskit_ionq import IonQProvider
from pyquil import get_qc
from qiskit.test.mock import FakeSantiago, FakeMontreal

class CircuitExecutor(ABC):

    @abstractmethod
    def execute_circuits(self, circuits, qpu, token, shots):
        pass

class IBMCircuitExecutor(CircuitExecutor):

    def execute_circuits(self, circuits, qpu, token, shots):
        IBMQ.enable_account(token)
        provider = IBMQ.get_provider()
        backend = provider.get_backend(qpu)
        backend = FakeMontreal()
        results = execute(circuits, backend=backend, shots=shots, optimization_level=0).result()
        IBMQ.disable_account()
        return results


class IonQCircuitExecutor(CircuitExecutor):

    def execute_circuits(self, circuits, qpu, token, shots):
        provider = IonQProvider(token)
        backend = provider.get_backend(qpu)
        return execute(circuits, backend=backend, shots=shots, optimization_level=0).result()


class RigettiCircuitExecutor(CircuitExecutor):

    def execute_circuits(self, circuits, qpu, token, shots):
        qc = get_qc(qpu)
        #TODO how to handle multiple programs/circuits
        executable = qc.compile(circuits)
        result = qc.run(executable)
        bitstrings = result.readout_data.get("ro")
        return bitstrings
