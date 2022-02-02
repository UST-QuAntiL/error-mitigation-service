from api.database.minio_db import load_matrix_file_from_db
from api.services.rem_services.mitigation_application import MatrixMultiplication


def application_generator(method):
    if method == "multiplication":
        return MatrixMultiplication()

# TODO just forward json for more flexibility
def mitigate_results(json):
    qubits = json.get("qubits")
    qpu = json.get("qpu")
    mitmethod = json.get("mitmethod")
    cmgenmethod = json.get("mmgenmethod")
    applmethod = json.get("applmethod")
    max_age = json.get("maxage")
    counts = json.get("counts")

    application_method = application_generator(applmethod)
    mitigator = None
    try:
        mitigator, _ = load_matrix_file_from_db(qpu=qpu, used_qubits=qubits, type="mm", method=cmgenmethod, max_age=max_age)
    except:
        return "Mitigator not available"
    finally:
        return application_method.appyl_mitigation(mitigator, counts=counts)



if __name__ == "__main__":
    json = {'counts':[50,450,470,30,0,0,0,0,0,0,0,0,0,0,0,0],'applmethod':'multiplication','mitmethod':'inversion','cmgenmethod': 'standard', 'qpu': 'ibmq_lima', 'provider': 'IBM', 'shots': 10, 'token': '350a71abf1741a8ad3a59a15f57dd56fa8c9621c27377fd43132c660d6dd47210577697228245e8d531130ed265c2589910bef4d3957580573edfd03c3157b84', 'qubits': [1, 2, 3]}
    print(mitigate_results(json))