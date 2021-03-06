import mthree
from qiskit import IBMQ
from qiskit_ionq import IonQProvider

from app.database.minio_db import store_matrix_object_in_db, load_matrix_object_from_db
from app.model.matrix_types import MatrixType
from app.model.mmgen_request import MMGetRequest
from app.services.cmgen_services.cmgen_service import generate_cm
from app.services.mitigator_gen_services.mitigation_generator import MatrixInversion
from app.services.cmgen_services.cmgen_service import (
    retrieve_generator,
    retrieve_executor,
)
from app.model.mmgen_request import MMGenRequest
from app.model.cmgen_request import CMGenRequest
from datetime import datetime


def mitigation_generator(method):
    if method == "inversion":
        return MatrixInversion()


def generate_mm(request: MMGenRequest):
    mitigation_method = request.mitigation_method
    if mitigation_method == "tpnm":
        return generate_mm_from_skratch(request)
    elif mitigation_method == "mthree":
        return generate_mthree_mitigator(request)
    else:
        return generate_mm_from_cm(request)


def generate_mthree_mitigator(request: MMGenRequest):
    try:
        if request.provider == "ibm":
            provider = IBMQ.enable_account(**credentials)
            backend = provider.get_backend(request.qpu)
            # For testing on a fake backend uncomment below
            # from qiskit.test.mock import FakeMontreal
            # backend = FakeMontreal()
        elif request.provider == "ionq":
            backend = IonQProvider(request.credentials).get_backend(request.qpu)
        mit = mthree.M3Mitigation(backend)
        mit.cals_from_system(request.qubits, shots=request.shots)
        calstmp = mit.cals_to_matrices()

        filename = store_matrix_object_in_db(
            matrix=calstmp,
            qpu=request.qpu,
            matrix_type=MatrixType.mm,
            qubits=request.qubits,
            cm_gen_method=request.mitigation_method,
            mitigation_method=request.mitigation_method,
            cm_gen_date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )
    finally:
        if request.provider == "ibm":
            IBMQ.disable_account()
    return filename


def generate_mm_from_skratch(request: MMGenRequest):
    generator = retrieve_generator(request.mitigation_method)
    circuits, labels = generator.generate_cm_circuits(request.qubits)
    executor = retrieve_executor(request.provider)
    results = executor.execute_circuits(
        circuits, request.qpu, request.credentials, request.shots
    )
    cm = generator.compute_sparse_mm(results, labels)
    return store_matrix_object_in_db(
        cm,
        request.qpu,
        MatrixType.mm,
        qubits=request.qubits,
        cm_gen_method=request.mitigation_method,
        mitigation_method=request.mitigation_method,
        cm_gen_date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
    )


def generate_mm_from_cm(request: MMGenRequest):

    try:
        cm, metadata = load_matrix_object_from_db(
            qpu=request.qpu,
            qubits=request.qubits,
            matrix_type=MatrixType.cm,
            cm_gen_method=request.cm_gen_method,
            max_age=request.max_age,
        )
    except:
        raise ConnectionError("Could not access DB")

    if cm is None:
        cmgenrequest = CMGenRequest(
            cm_gen_method=request.cm_gen_method,
            qubits=request.qubits,
            qpu=request.qpu,
            shots=request.shots,
            credentials=request.credentials,
            provider=request.provider,
        )
        generate_cm(cmgenrequest)
        cm, metadata = load_matrix_object_from_db(
            qpu=request.qpu,
            qubits=request.qubits,
            matrix_type=MatrixType.cm,
            cm_gen_method=request.cm_gen_method,
            max_age=request.max_age,
        )

    mitigator = mitigation_generator(request.mitigation_method)
    mm = mitigator.generate_mitigator(cm)
    return store_matrix_object_in_db(
        matrix=mm,
        qpu=request.qpu,
        matrix_type=MatrixType.mm,
        qubits=request.qubits,
        cm_gen_method=metadata["cm_gen_method"],
        mitigation_method=request.mitigation_method,
        cmfilename=metadata["name"],
        cm_gen_date=metadata["cm_gen_date"],
    )


def retrieve_mm(req: MMGetRequest):
    return load_matrix_object_from_db(
        qpu=req.qpu,
        matrix_type=MatrixType.mm,
        qubits=req.qubits,
        method=req.mitigation_method,
        max_age=req.max_age,
    )


if __name__ == "__main__":
    from credentials import Credentials as credentials

    json = {
        "max_age": 1,
        "cm_gen_method": "standard",
        "mitigation_method": "inversion",
        "qpu": "ibmq_lima",
        "qubits": [1, 2, 3],
        "provider": "ibm",
        "shots": 10,
        "credentials": credentials.CREDENTIALS_US,
    }
    req = MMGenRequest(**json)
    print(generate_mm(req))
