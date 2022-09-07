from app.database.minio_db import store_matrix_object_in_db, load_matrix_object_from_db
from app.model.cmgen_request import CMGetRequest, CMGenRequest, CMGenFromCountsRequest
from app.model.matrix_types import MatrixType
from app.services.cmgen_services.circuit_executor import (
    IBMCircuitExecutor,
    IonQCircuitExecutor,
    RigettiCircuitExecutor,
)
from app.services.cmgen_services.circuit_generator import (
    StandardCMGenerator,
    CTMPCMGenerator,
    TPNMCMGenerator,
)


def retrieve_executor(provider: str):
    provider = provider.lower()
    if provider == "ibm":
        return IBMCircuitExecutor()
    if provider == "ionq":
        return IonQCircuitExecutor()
    if provider == "rigetti":
        return RigettiCircuitExecutor()


def retrieve_generator(method: str):
    method = method.lower()
    if method == "standard":
        return StandardCMGenerator()
    if method == "tpnm":
        return TPNMCMGenerator()
    if method == "ctmp":
        return CTMPCMGenerator()


def generate_cm(request: CMGenRequest):
    generator = retrieve_generator(request.cm_gen_method)
    circuits = generator.generate_cm_circuits(request.qubits)
    executor = retrieve_executor(request.provider.lower())
    counts = executor.execute_circuits(
        circuits, request.qpu, request.credentials, request.shots, request.noise_model, request.only_measurement_errors
    )
    cm = generator.compute_cm(counts)
    return store_matrix_object_in_db(
        cm,
        request.qpu,
        MatrixType.cm,
        qubits=request.qubits,
        cm_gen_method=request.cm_gen_method,
        noise_model=request.noise_model,
        only_measurement_errors=request.only_measurement_errors
    )


def retrieve_cm(req: CMGetRequest):
    return load_matrix_object_from_db(
        qpu=req.qpu,
        matrix_type=MatrixType.cm,
        qubits=req.qubits,
        cm_gen_method=req.cm_gen_method,
        max_age=req.max_age,
        noise_model=req.noise_model,
        only_measurement_errors=req.only_measurement_errors
    )


def generate_cm_from_counts(request: CMGenFromCountsRequest):
    generator = retrieve_generator(request.cm_gen_method)
    counts = request.counts
    cm = generator.compute_cm(counts)
    return store_matrix_object_in_db(
        cm,
        request.qpu,
        MatrixType.cm,
        qubits=request.qubits,
        cm_gen_method=request.cm_gen_method,
    )


if __name__ == "__main__":
    from credentials import Credentials as credentials

    json = {
        "cm_gen_method": "tpnm",
        "qpu": "ibmq_lima",
        "provider": "ibm",
        "shots": 1000,
        "credentials": credentials.CREDENTIALS_US,
        "qubits": [1, 2, 4],
    }
    req = CMGenRequest(**json)
    res = generate_cm(req)
