from app.database.minio_db import (
    load_matrix_object_from_db,
    load_mitigator_object_from_db_by_filename,
)
from app.model.cmgen_request import CMGenRequest
from app.model.matrix_types import MatrixType
from app.model.rem_request import REMRequest
from app.model.mmgen_request import MMGenRequest
from app.services.cmgen_services.cmgen_service import generate_cm
from app.services.mitigator_gen_services.mmgen_service import generate_mm
from app.services.rem_services.mitigation_application import (
    MatrixMultiplication,
    MthreeApplication,
    IterativeBayesApplication,
    IgnisUnfoldingApplication,
)
from app.utils.helper_functions import sort_dict_by_qubitorder, restore_dict_by_qubitorder
import itertools


def application_generator(method):
    if method in ["inversion", "tpnm"]:
        return MatrixMultiplication()
    if method == "mthree":
        return MthreeApplication()
    if method == "bayes":
        return IterativeBayesApplication()
    if method == "ignis":
        return IgnisUnfoldingApplication()

def perform_mitigation(counts, qubits, metadata, application_method, mitigator):
    sorted_counts = sort_dict_by_qubitorder(
                    counts, qubits, metadata["qubits"]
                )
    mitigated_counts=  application_method.appyl_mitigation(
        mitigator, counts=sorted_counts, qubits=qubits)

    return restore_dict_by_qubitorder(mitigated_counts, qubits, metadata["qubits"])


def mitigate_results(request: REMRequest):
    application_method = application_generator(request.mitmethod)

    if isinstance(request.qubits[0], int):
        request.qubits = [request.qubits]
    if not isinstance(request.counts, list) and isinstance(list(request.counts.values())[0], int):
        request.counts = [request.counts]

    solution_counts= []
    for counts, qubits in itertools.zip_longest(request.counts, request.qubits):
        if application_method.requires == MatrixType.mm:
            mitigator, metadata = load_matrix_object_from_db(
                qpu=request.qpu,
                qubits=qubits,
                matrix_type=MatrixType.mm,
                mitmethod=request.mitmethod,
                cmgenmethod=request.cmgenmethod,
                max_age=request.maxage,
            )
            if mitigator is not None:
                if len(request.counts) != len(request.qubits):
                    for c in request.counts:
                        solution_counts.append(perform_mitigation(c,qubits,metadata,application_method,mitigator))
                    return solution_counts
                else:
                    solution_counts.append(perform_mitigation(counts,qubits,metadata,application_method,mitigator))
            elif request.credentials and request.provider:
                mmgenrequest = MMGenRequest(
                    mitmethod=request.mitmethod,
                    cmgenmethod=request.cmgenmethod,
                    qubits=qubits,
                    qpu=request.qpu,
                    shots=request.shots,
                    credentials=request.credentials,
                    provider=request.provider,
                    maxage=request.maxage,
                )
                filename = generate_mm(mmgenrequest)
                mitigator, metadata = load_mitigator_object_from_db_by_filename(
                    qpu=request.qpu, matrix_type=MatrixType.mm, filename=filename
                )
                if len(request.counts) != len(request.qubits):
                    for c in request.counts:
                        solution_counts.append(perform_mitigation(c, qubits, metadata, application_method, mitigator))
                    return solution_counts
                else:
                    solution_counts.append(perform_mitigation(counts, qubits, metadata, application_method, mitigator))
            else:
                return "No matching mitigatior available - Add credentials and provider to generate a new mitigator"
        elif application_method.requires == MatrixType.cm:
            cm, metadata = load_matrix_object_from_db(
                qpu=request.qpu,
                qubits=qubits,
                matrix_type=MatrixType.cm,
                cmgenmethod=request.cmgenmethod,
                max_age=request.maxage,
            )
            if cm is not None:
                if len(request.counts) != len(request.qubits):
                    for c in request.counts:
                        solution_counts.append(perform_mitigation(c, qubits, metadata, application_method, cm))
                    return solution_counts
                else:
                    solution_counts.append(perform_mitigation(counts, qubits, metadata, application_method, cm))
            elif request.credentials and request.provider:
                cmgenrequest = CMGenRequest(
                    cmgenmethod=request.cmgenmethod,
                    qubits=qubits,
                    qpu=request.qpu,
                    shots=request.shots,
                    credentials=request.credentials,
                    provider=request.provider,
                )
                filename = generate_cm(cmgenrequest)
                cm, metadata = load_mitigator_object_from_db_by_filename(
                    qpu=request.qpu, matrix_type=MatrixType.cm, filename=filename
                )
                if len(request.counts) != len(request.qubits):
                    for c in request.counts:
                        solution_counts.append(perform_mitigation(c, qubits, metadata, application_method, cm))
                    return solution_counts
                else:
                    solution_counts.append(perform_mitigation(counts, qubits, metadata, application_method, cm))
            else:
                return "No matching mitigatior available - Add credentials and provider to generate a new mitigator"
    return solution_counts if len(solution_counts) > 1 else solution_counts[0]

if __name__ == "__main__":
    from credentials import Credentials as credentials

    json = {
        "counts": {
            "111": 129,
            "000": 131,
            "101": 134,
            "100": 142,
            "011": 97,
            "110": 117,
            "001": 125,
            "010": 125,
        },
        "mitmethod": "inversion",
        "cmgenmethod": "standard",
        "qpu": "ibmq_lima",
        "qubits": [3, 1, 2],
        "maxage": 1,
    }
    json = {
        "counts": {
            "111": 129,
            "000": 131,
            "101": 134,
            "100": 142,
            "011": 97,
            "110": 117,
            "001": 125,
            "010": 125,
        },
        "mitmethod": "inversion",
        "cmgenmethod": "standard",
        "qpu": "ibmq_lima",
        "qubits": [3, 1, 2],
        "maxage": 3,
        "credentials": credentials.CREDENTIALS_US,
        "provider": "IBM",
    }
    json = {
        "counts": {
            "111": 129,
            "000": 131,
            "101": 134,
            "100": 142,
            "011": 97,
            "110": 117,
            "001": 125,
            "010": 125,
        },
        "mitmethod": "ignis",
        "cmgenmethod": "standard",
        "qpu": "ibmq_lima",
        "qubits": [3, 1, 2],
        "maxage": 2,
        "credentials": credentials.CREDENTIALS_US,
        "provider": "IBM",
    }
    print(mitigate_results(REMRequest(**json)))
