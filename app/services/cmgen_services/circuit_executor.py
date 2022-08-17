from abc import ABC, abstractmethod
from time import sleep

from qiskit import IBMQ, execute
from qiskit_ionq import IonQProvider
import requests
import json


class CircuitExecutor(ABC):
    @abstractmethod
    def execute_circuits(self, circuits, qpu, credentials, shots):
        pass


class IBMCircuitExecutor(CircuitExecutor):
    def execute_circuits(self, circuits, qpu, credentials, shots):
        qasm_list = [circuit.qasm() for circuit in circuits]
        prepared_credentials = dict(
            (
                (key, {"rawValue": value, "type": "Unknown"})
                for key, value in credentials.items()
            )
        )
        request = {
            "transpiled-qasm": qasm_list,
            "qpu-name": qpu,
            "input-params": prepared_credentials,
        }
        print(request)
        url_prefix = "http://qiskit-service:5013/"  # http://localhost:5013/
        response = requests.post(
            url_prefix + "qiskit-service/api/v1.0/execute", json=request
        )
        if response.status_code == 202:
            while True:
                get_response = requests.get(
                    url_prefix + response.json()["Location"]
                ).json()
                complete = get_response["complete"]
                if complete:
                    return get_response["result"]
                else:
                    print(
                        "checking result availability for result "
                        + url_prefix
                        + response.json()["Location"]
                    )
                    sleep(5)

        # alternative local execution without qiskit-service
        # try:
        # provider = IBMQ.enable_account(**credentials)
        # backend = provider.get_backend(qpu)
        # results = (
        #     execute(circuits, backend=backend, shots=shots, optimization_level=0)
        #     .result()
        #     .get_counts()
        # )
        # finally:
        #     IBMQ.disable_account()
        # return results


class IonQCircuitExecutor(CircuitExecutor):
    def execute_circuits(self, circuits, qpu, credentials, shots):
        provider = IonQProvider(**credentials)
        backend = provider.get_backend(qpu)
        jobs = [execute(c, backend=backend, shots=shots) for c in circuits]
        counts = [j.result().get_counts() for j in jobs]
        return counts


class RigettiCircuitExecutor(CircuitExecutor):
    def execute_circuits(self, circuits, qpu, credentials, shots):
        #################################################################
        #                                                               #
        #   Rigetti does not support API circuit execution yet          #
        #   Generate & Execute circuits via Rigetti Jupyter Lab and     #
        #   import counts into REM Service via the /cm/fromCounts API   #
        #                                                               #
        #################################################################
        # qc = get_qc(qpu)
        # executable = qc.compile(circuits)
        # result = qc.run(executable)
        # bitstrings = result.readout_data.get("ro")
        # return bitstrings
        raise NotImplementedError("Rigetti circuits can not be executed via API yet")
