from api.database.minio_db import store_matrix_file_in_db, load_matrix_file_from_db
from api.model.mmgen_request import MMGetRequest
from api.services.cmgen_services.cmgen_service import generate_cm
from api.services.mmgen_services.mitigation_generator import MatrixInversion

def mitigation_generator(method):
    if method == "inversion":
        return MatrixInversion()

# TODO just forward json for more flexibility
def generate_mm(json):
    qubits = json.get("qubits")
    qpu = json.get("qpu")
    mitmethod = json.get("mitmethod")
    cmgenmethod = json.get("mmgenmethod")
    max_age = json.get("maxage")
    type = "cm"

    cm = None
    try:
        cm, filename = load_matrix_file_from_db(qpu=qpu, used_qubits=qubits, type=type, method=cmgenmethod, max_age=max_age)
    except:
        generate_cm(json)
        cm, filename = load_matrix_file_from_db(qpu=qpu, used_qubits=qubits, type=type, method=cmgenmethod, max_age=max_age)
    finally:
        if cm:
            mitigator = mitigation_generator(mitmethod)
            mm = mitigator.generate_mitigator(cm)
            # TODO save filename of cm
            return store_matrix_file_in_db(matrix=mm,qpu=qpu, type="mm", used_qubits=qubits, method=mitmethod)


def retrieve_mm(req: MMGetRequest):
    #TODO age should depend on cm age etc. split load cm and load mm maybe
    return load_matrix_file_from_db(qpu=req.qpu, used_qubits=req.qubits, method=req.mitmethod, max_age=req.max_age)




if __name__ == "__main__":
    json = {'cmgenmethod': 'standard', 'mitmethod':'inversion', 'qpu': 'ibmq_lima', 'qubits':[1,2,3,4], 'provider': 'IBM', 'shots': 10, 'token': '350a71abf1741a8ad3a59a15f57dd56fa8c9621c27377fd43132c660d6dd47210577697228245e8d531130ed265c2589910bef4d3957580573edfd03c3157b84'}
    print(generate_mm(json))