from api.database.minio_db import load_matrix_object_from_db, load_mitigator_object_from_db_by_filename
from api.model.cmgen_request import CMGenRequest
from api.model.matrix_types import MatrixType
from api.model.rem_request import REMRequest
from api.model.mmgen_request import MMGenRequest
from api.services.cmgen_services.cmgen_service import generate_cm
from api.services.mitigator_gen_services.mmgen_service import generate_mm
from api.services.rem_services.mitigation_application import MatrixMultiplication, MthreeApplication, \
    IterativeBayesApplication, IgnisUnfoldingApplication
from api.utils.helper_functions import sort_dict_by_qubitorder


def application_generator(method):
    if method in ['inversion', 'tpnm']:
        return MatrixMultiplication()
    if method == "mthree":
        return MthreeApplication()
    if method == "bayes":
        return IterativeBayesApplication()
    if method == "ignis":
        return IgnisUnfoldingApplication()



def mitigate_results(request: REMRequest):
    application_method = application_generator(request.mitmethod)

    if application_method.requires == MatrixType.mm:
        mitigator, metadata = load_matrix_object_from_db(qpu=request.qpu, qubits=request.qubits, matrix_type=MatrixType.mm, mitmethod=request.mitmethod,
                                                  cmgenmethod=request.cmgenmethod, max_age=request.maxage)
        if mitigator is not None:
            sorted_counts = sort_dict_by_qubitorder(request.counts, request.qubits, metadata['qubits'])
            return application_method.appyl_mitigation(mitigator, counts=sorted_counts, qubits=request.qubits)
        elif request.credentials and request.provider:
            mmgenrequest = MMGenRequest(mitmethod= request.mitmethod, cmgenmethod=request.cmgenmethod, qubits=request.qubits, qpu=request.qpu,
                                        shots=request.shots, credentials=request.credentials, provider=request.provider, maxage=request.maxage)
            filename = generate_mm(mmgenrequest)
            mitigator, metadata = load_mitigator_object_from_db_by_filename(qpu=request.qpu, matrix_type=MatrixType.mm, filename=filename)
            sorted_counts = sort_dict_by_qubitorder(request.counts, request.qubits, metadata['qubits'])
            return application_method.appyl_mitigation(mitigator, counts=sorted_counts, qubits=request.qubits)
        return 'No matching mitigatior available - Add credentials and provider to generate a new mitigator'
    elif application_method.requires == MatrixType.cm:
        cm, metadata = load_matrix_object_from_db(qpu=request.qpu, qubits=request.qubits, matrix_type=MatrixType.cm,
                                                  cmgenmethod=request.cmgenmethod, max_age=request.maxage)
        if cm is not None:
            sorted_counts = sort_dict_by_qubitorder(request.counts, request.qubits, metadata['qubits'])
            return application_method.appyl_mitigation(cm, counts=sorted_counts, qubits=request.qubits)
        elif request.credentials and request.provider:
            cmgenrequest = CMGenRequest(cmgenmethod=request.cmgenmethod, qubits=request.qubits, qpu=request.qpu,
                                        shots=request.shots, credentials=request.credentials, provider=request.provider)
            filename = generate_cm(cmgenrequest)
            cm, metadata = load_mitigator_object_from_db_by_filename(qpu=request.qpu, matrix_type=MatrixType.cm, filename=filename)
            sorted_counts = sort_dict_by_qubitorder(request.counts, request.qubits, metadata['qubits'])
            return application_method.appyl_mitigation(cm, counts=sorted_counts, qubits=request.qubits)
        return 'No matching mitigatior available - Add credentials and provider to generate a new mitigator'




if __name__ == "__main__":
    from credentials import Credentials as credentials
    json = {'counts': {"111": 129, "000": 131, "101": 134, "100": 142, "011": 97, "110": 117, "001": 125, "010": 125},'mitmethod':'inversion','cmgenmethod': 'standard', 'qpu': 'ibmq_lima', 'qubits': [3, 1, 2], 'maxage':1}
    json = {'counts': {"111": 129, "000": 131, "101": 134, "100": 142, "011": 97, "110": 117, "001": 125, "010": 125},
            'mitmethod':'inversion','cmgenmethod': 'standard', 'qpu': 'ibmq_lima', 'qubits': [3, 1, 2], 'maxage':3, 'credentials':credentials.CREDENTIALS_US, 'provider': "IBM"}
    json = {'counts': {"111": 129, "000": 131, "101": 134, "100": 142, "011": 97, "110": 117, "001": 125, "010": 125},
            'mitmethod':'ignis','cmgenmethod': 'standard', 'qpu': 'ibmq_lima', 'qubits': [3, 1, 2], 'maxage':2, 'credentials':credentials.CREDENTIALS_US, 'provider': "IBM"}
    print(mitigate_results(REMRequest(**json)))