import mthree
from qiskit import IBMQ
from qiskit_ionq import IonQProvider

from api.database.minio_db import store_matrix_object_in_db, load_matrix_object_from_db
from api.model.matrix_types import MatrixType
from api.model.mmgen_request import MMGetRequest
from api.services.cmgen_services.cmgen_service import generate_cm
from api.services.mitigator_gen_services.mitigation_generator import MatrixInversion
from api.services.cmgen_services.cmgen_service import retrieve_generator, retrieve_executor
from api.model.mmgen_request import MMGenRequest
from api.model.cmgen_request import CMGenRequest
from datetime import datetime
from qiskit.test.mock import FakeMontreal

def mitigation_generator(method):
    if method == "inversion":
        return MatrixInversion()

def generate_mm(request: MMGenRequest):
    mitmethod = request.mitmethod
    if mitmethod == "tpnm":
        return generate_mm_from_skratch(request)
    elif mitmethod == "mthree":
        return generate_mthree_mitigator(request)
    else:
        return generate_mm_from_cm(request)

def generate_mthree_mitigator(request: MMGenRequest):
    if request.provider == "ibm":
        provider = IBMQ.enable_account(**credentials)
        backend = provider.get_backend(request.qpu)
        # backend = FakeMontreal()
    elif request.provider == "ionq":
        backend = IonQProvider(request.credentials).get_backend(request.qpu)
    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(request.qubits, shots=request.shots)
    calstmp = mit.cals_to_matrices()

    filename = store_matrix_object_in_db(matrix=calstmp, qpu=request.qpu, matrix_type=MatrixType.mm, qubits=request.qubits, cmgenmethod=request.mitmethod, mitmethod=request.mitmethod, cmgendate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    if request.provider == "ibm":
        IBMQ.disable_account()
    return filename

def generate_mm_from_skratch(request: MMGenRequest):
    generator = retrieve_generator(request.mitmethod)
    circuits, labels = generator.generate_cm_circuits(request.qubits)
    executor = retrieve_executor(request.provider)
    results = executor.execute_circuits(circuits, request.qpu, request.credentials, request.shots)
    cm = generator.compute_sparse_mm(results, labels)
    return store_matrix_object_in_db(cm, request.qpu, MatrixType.mm, qubits=request.qubits, cmgenmethod=request.mitmethod, mitmethod=request.mitmethod, cmgendate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


def generate_mm_from_cm(request: MMGenRequest):

    try:
        cm, metadata = load_matrix_object_from_db(qpu=request.qpu, qubits=request.qubits, matrix_type=MatrixType.cm, cmgenmethod=request.cmgenmethod, max_age=request.maxage)
    except:
        raise

    if cm is None:
        cmgenrequest= CMGenRequest(cmgenmethod=request.cmgenmethod, qubits=request.qubits, qpu=request.qpu, shots=request.shots, credentials=request.credentials, provider=request.provider)
        generate_cm(cmgenrequest)
        cm, metadata = load_matrix_object_from_db(qpu=request.qpu, qubits=request.qubits, matrix_type=MatrixType.cm, cmgenmethod=request.cmgenmethod, max_age=request.maxage)

    mitigator = mitigation_generator(request.mitmethod)
    mm = mitigator.generate_mitigator(cm)
    return store_matrix_object_in_db(matrix=mm, qpu=request.qpu, matrix_type=MatrixType.mm, qubits=request.qubits, cmgenmethod=metadata['cmgenmethod'], mitmethod=request.mitmethod, cmfilename = metadata['name'], cmgendate = metadata['cmgendate'])


def retrieve_mm(req: MMGetRequest):
    return load_matrix_object_from_db(qpu=req.qpu, matrix_type=MatrixType.mm, qubits=req.qubits, method=req.mitmethod, max_age=req.max_age)




if __name__ == "__main__":
    from credentials import Credentials as credentials

    json = {'maxage':1,'cmgenmethod': 'standard', 'mitmethod':'inversion', 'qpu': 'ibmq_lima', 'qubits':[1,2,3], 'provider': 'ibm', 'shots': 10, 'credentials': credentials.CREDENTIALS_US}
    #json = {'cmgenmethod': 'tpnm', 'mitmethod':'tpnm', 'qpu': 'ibmq_lima', 'qubits':[1,2,3,4], 'provider': 'ibm', 'shots': 10, 'credentials': credentials.CREDENTIALS_US}
    #json = {'cmgenmethod': 'mthree', 'mitmethod':'mthree', 'qpu': 'ibmq_lima', 'qubits':[1,2,3,4], 'provider': 'ibm', 'shots': 10, 'credentials': credentials.CREDENTIALS_US}
    req = MMGenRequest(**json)
    print(generate_mm(req))