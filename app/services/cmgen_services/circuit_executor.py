from abc import ABC, abstractmethod

from qiskit import IBMQ, execute, transpile
from qiskit.providers.ibmq import IBMQBackend, IBMQJobManager
from qiskit_ionq import IonQProvider
from pyquil import get_qc
from qiskit.test.mock import FakeMontreal


class CircuitExecutor(ABC):
    @abstractmethod
    def execute_circuits(self, circuits, qpu, credentials, shots):
        pass


class IBMCircuitExecutor(CircuitExecutor):
    def execute_circuits(self, circuits, qpu, credentials, shots):
        try:
            provider = IBMQ.enable_account(**credentials)
            backend = provider.get_backend(qpu)
            # TODO split when too many circuits
            # if type(backend) == IBMQBackend:
            #     jobmanager = IBMQJobManager()  # works only with IBMQBackend typed backend, splits experiments into jobs
            #     bulk_circuits = transpile(circuits, backend=backend)
            #     res = jobmanager.run(bulk_circuits, backend=backend, shots=shots).results()
            #     counts = [res.get_counts(i) for i in range(len(bulk_circuits))]
            results = (
                execute(circuits, backend=backend, shots=shots, optimization_level=0)
                .result()
                .get_counts()
            )
            # TODO check if reverse is necessary
            reversed_result = {}
            # for key, value in results.items():
            #     reversed_result[key.reverse()] = value
        finally:
            IBMQ.disable_account()
        return results


class IonQCircuitExecutor(CircuitExecutor):
    def execute_circuits(self, circuits, qpu, credentials, shots):
        provider = IonQProvider(**credentials)
        backend = provider.get_backend(qpu)
        jobs = [execute(c, backend=backend, shots=shots) for c in circuits]
        counts = [j.result().get_counts() for j in jobs]
        return counts


class RigettiCircuitExecutor(CircuitExecutor):
    def execute_circuits(self, circuits, qpu, credentials, shots):
        qc = get_qc(qpu)
        # TODO how to handle multiple programs/circuits
        executable = qc.compile(circuits)
        result = qc.run(executable)
        bitstrings = result.readout_data.get("ro")
        return bitstrings
