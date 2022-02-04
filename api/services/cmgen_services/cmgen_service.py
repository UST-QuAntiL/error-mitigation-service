from api.database.minio_db import store_matrix_object_in_db, load_matrix_object_from_db
from api.model.cmgen_request import CMGetRequest
from api.model.matrix_types import MatrixType
from api.services.cmgen_services.circuit_executor import IBMCircuitExecutor,  IonQCircuitExecutor, RigettiCircuitExecutor
from api.services.cmgen_services.circuit_generator import StandardCMGenerator, MthreeCMGenerator, CTMPCMGenerator, TPNMCMGenerator


def retrieve_executor(provider):
    if provider == "ibm":
        return IBMCircuitExecutor()
    if provider == "ionq":
        return IonQCircuitExecutor()
    if provider == "rigetti":
        return RigettiCircuitExecutor()

def retrieve_generator(method):
    if method == "standard":
        return StandardCMGenerator()
    if method == "tpnm":
        return TPNMCMGenerator()
    if method == "ctmp":
        return CTMPCMGenerator()
    if method == "mthree":
        return MthreeCMGenerator()


# TODO just forward json for more flexibility
def generate_cm(json):
    qubits = json.get("qubits")
    qpu = json.get("qpu")
    token = json.get("token")
    shots = json.get("shots")
    cmgenmethod = json.get("cmgenmethod").lower()
    provider = json.get("provider").lower()

    generator = retrieve_generator(cmgenmethod)
    circuits, labels = generator.generate_cm_circuits(qubits)
    executor = retrieve_executor(provider)
    results = executor.execute_circuits(circuits, qpu, token, shots)
    cm = generator.compute_cm(results, labels)
    return store_matrix_object_in_db(cm, qpu, MatrixType.cm, qubits = qubits, cmgenmethod = cmgenmethod)


def retrieve_cm(req: CMGetRequest):
    return load_matrix_object_from_db(qpu=req.qpu, qubits=req.qubits, method=req.method, max_age=req.max_age)




if __name__ == "__main__":
    #STandard
    # json = {'cmgenmethod': 'standard', 'qpu': 'ibmq_lima', 'provider': 'IBM', 'shots': 10, 'token': '350a71abf1741a8ad3a59a15f57dd56fa8c9621c27377fd43132c660d6dd47210577697228245e8d531130ed265c2589910bef4d3957580573edfd03c3157b84', 'qubits': [1, 2, 3, 7]}
    #TPNM
    json = {'cmgenmethod': 'tpnm', 'qpu': 'ibmq_lima', 'provider': 'IBM', 'shots': 10, 'token': '350a71abf1741a8ad3a59a15f57dd56fa8c9621c27377fd43132c660d6dd47210577697228245e8d531130ed265c2589910bef4d3957580573edfd03c3157b84', 'qubits': [1, 2, 3, 7]}
    res = generate_cm(json)
    print("test")