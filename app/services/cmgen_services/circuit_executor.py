from abc import ABC, abstractmethod
from time import sleep

from qiskit import IBMQ, execute, transpile
from qiskit.providers import QiskitBackendNotFoundError
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.ibmq import IBMQAccountCredentialsNotFound
from qiskit.providers.ibmq.api.exceptions import RequestsApiError
from qiskit_ionq import IonQProvider
import requests
import json


class CircuitExecutor(ABC):
    @abstractmethod
    def execute_circuits(
        self, circuits, qpu, credentials, shots, noise_model, only_measurement_errors
    ):
        pass


class IBMCircuitExecutor(CircuitExecutor):
    def execute_circuits(
        self, circuits, qpu, credentials, shots, noise_model, only_measurement_errors
    ):
        if noise_model:
            noisy_qpu = get_qpu(credentials, noise_model)
            noise_model = NoiseModel.from_backend(noisy_qpu)
            configuration = noisy_qpu.configuration()
            coupling_map = configuration.coupling_map
            basis_gates = noise_model.basis_gates
            transpiled_circuit = transpile(circuits, noisy_qpu, optimization_level=0)

            if only_measurement_errors:
                ro_noise_model = NoiseModel()
                for k, v in noise_model._local_readout_errors.items():
                    ro_noise_model.add_readout_error(v, k)
                noise_model = ro_noise_model

            backend = AerSimulator()
            job = execute(
                transpiled_circuit,
                backend=backend,
                coupling_map=coupling_map,
                basis_gates=basis_gates,
                noise_model=noise_model,
                shots=shots,
                optimization_level=0,
            )
            result_counts = job.result().get_counts()
            return result_counts
        else:
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
    def execute_circuits(
        self, circuits, qpu, credentials, shots, noise_model, only_measurement_errors
    ):
        if noise_model:
            raise NotImplementedError(
                "No noisy simulation implemented for IonQ devices yet"
            )
        provider = IonQProvider(**credentials)
        backend = provider.get_backend(qpu)
        jobs = [execute(c, backend=backend, shots=shots) for c in circuits]
        counts = [j.result().get_counts() for j in jobs]
        return counts


class RigettiCircuitExecutor(CircuitExecutor):
    def execute_circuits(
        self, circuits, qpu, credentials, shots, noise_model, only_measurement_errors
    ):
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


def get_qpu(credentials, qpu):
    """Load account from token. Get backend."""
    try:
        try:
            IBMQ.disable_account()
        except IBMQAccountCredentialsNotFound:
            pass
        finally:
            provider = IBMQ.enable_account(**credentials)
            backend = provider.get_backend(qpu)
            return backend
    except (QiskitBackendNotFoundError, RequestsApiError):
        print(
            'Backend could not be retrieved. Backend name or credentials are invalid. Be sure to use the schema credentials: {"token": "YOUR_TOKEN", "hub": "YOUR_HUB", "group": "YOUR GROUP", "project": "YOUR_PROJECT"). Note that "ibm-q/open/main" are assumed as default values for "hub", "group", "project".'
        )
        return None
