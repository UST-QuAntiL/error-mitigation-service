from api.database.minio_db import store_matrix_object_in_db, load_matrix_object_from_db
from api.model.cmgen_request import CMGetRequest, CMGenRequest
from api.model.matrix_types import MatrixType
from api.services.cmgen_services.circuit_executor import IBMCircuitExecutor,  IonQCircuitExecutor, RigettiCircuitExecutor
from api.services.cmgen_services.circuit_generator import StandardCMGenerator, CTMPCMGenerator, TPNMCMGenerator


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
    generator = retrieve_generator(request.cmgenmethod)
    circuits, labels = generator.generate_cm_circuits(request.qubits)
    executor = retrieve_executor(request.provider.lower())
    results = executor.execute_circuits(circuits, request.qpu, request.credentials, request.shots)
    cm = generator.compute_cm(results, labels)
    return store_matrix_object_in_db(cm, request.qpu, MatrixType.cm, qubits = request.qubits, cmgenmethod = request.cmgenmethod)


def retrieve_cm(req: CMGetRequest):
    return load_matrix_object_from_db(qpu=req.qpu, matrix_type=MatrixType.cm, qubits=req.qubits, method=req.cmgenmethod, max_age=req.max_age)




if __name__ == "__main__":
    from credentials import Credentials as credentials
    #STandard
    # json = {'cmgenmethod': 'standard', 'qpu': 'ibmq_lima', 'provider': 'IBM', 'shots': 10, 'credentials': credentials.CREDENTIALS_US, 'qubits': [1, 2, 3, 7]}
    #TPNM
    json = {'cmgenmethod': 'tpnm', 'qpu': 'ibmq_lima', 'provider': 'ibm', 'shots': 1000, 'credentials':credentials.CREDENTIALS_US, 'qubits': [1, 2, 4]}
    req = CMGenRequest(**json)
    res = generate_cm(req)
    print("test")