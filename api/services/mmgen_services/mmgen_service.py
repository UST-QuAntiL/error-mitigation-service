from api.database.minio_db import store_matrix_object_in_db, load_matrix_object_from_db
from api.model.matrix_types import MatrixType
from api.model.mmgen_request import MMGetRequest
from api.services.cmgen_services.cmgen_service import generate_cm
from api.services.mmgen_services.mitigation_generator import MatrixInversion
from api.services.cmgen_services.cmgen_service import retrieve_generator, retrieve_executor
from datetime import datetime

def mitigation_generator(method):
    if method == "inversion":
        return MatrixInversion()

def generate_mm(json):
    mitmethod = json.get("mitmethod")
    if mitmethod == "tpnm":
        generate_mm_from_skratch(json)
    else:
        generate_mm_from_cm(json)


def generate_mm_from_skratch(json):
    qubits = json.get("qubits")
    qpu = json.get("qpu")
    token = json.get("token")
    shots = json.get("shots")
    mitmethod = json.get("mitmethod").lower()
    provider = json.get("provider").lower()

    generator = retrieve_generator(mitmethod)
    circuits, labels = generator.generate_cm_circuits(qubits)
    executor = retrieve_executor(provider)
    results = executor.execute_circuits(circuits, qpu, token, shots)
    cm = generator.compute_sparse_mm(results, labels)
    return store_matrix_object_in_db(cm, qpu, MatrixType.mm, qubits=qubits, cmgenmethod=mitmethod, mitmethod=mitmethod, cmgendate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

# TODO just forward json for more flexibility
def generate_mm_from_cm(json):
    qubits = json.get("qubits")
    qpu = json.get("qpu")
    mitmethod = json.get("mitmethod")
    cmgenmethod = json.get("cmgenmethod")
    max_age = json.get("maxage")

    cm, metadata = None, None
    try:
        cm, metadata = load_matrix_object_from_db(qpu=qpu, qubits=qubits, matrix_type=MatrixType.cm, cmgenmethod=cmgenmethod, max_age=max_age)
    except:
        generate_cm(json)
        cm, metadata = load_matrix_object_from_db(qpu=qpu, qubits=qubits, matrix_type=MatrixType.cm, cmgenmethod=cmgenmethod, max_age=max_age)
    finally:
        mitigator = mitigation_generator(mitmethod)
        mm = mitigator.generate_mitigator(cm)
        # TODO save filename of cm
        return store_matrix_object_in_db(matrix=mm, qpu=qpu, matrix_type=MatrixType.mm, qubits=qubits, cmgenmethod=metadata['cmgenmethod'], mitmethod=mitmethod, cmfilename = metadata['name'], cmgendate = metadata['cmgendate'] )


def retrieve_mm(req: MMGetRequest):
    #TODO age should depend on cm age etc. split load cm and load mm maybe
    return load_matrix_object_from_db(qpu=req.qpu, qubits=req.qubits, method=req.mitmethod, max_age=req.max_age)




if __name__ == "__main__":
    # json = {'cmgenmethod': 'standard', 'mitmethod':'inversion', 'qpu': 'ibmq_lima', 'qubits':[1,2,3,4], 'provider': 'IBM', 'shots': 10, 'token': '350a71abf1741a8ad3a59a15f57dd56fa8c9621c27377fd43132c660d6dd47210577697228245e8d531130ed265c2589910bef4d3957580573edfd03c3157b84'}
    json = {'cmgenmethod': 'tpnm', 'mitmethod':'tpnm', 'qpu': 'ibmq_lima', 'qubits':[1,2,3,4], 'provider': 'IBM', 'shots': 10, 'token': '350a71abf1741a8ad3a59a15f57dd56fa8c9621c27377fd43132c660d6dd47210577697228245e8d531130ed265c2589910bef4d3957580573edfd03c3157b84'}
    print(generate_mm(json))