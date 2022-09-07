from flask_smorest import Blueprint
from flask import request

from app.model.mmgen_request import (
    MMGenRequestSchema,
    MMGenRequest,
    MMGetRequest,
    MMGetRequestSchema,
)
from app.services.mitigator_gen_services.mmgen_service import generate_mm, retrieve_mm

blp = Blueprint(
    "mm",
    __name__,
    url_prefix="/mm",
    description="Generate and Request Mitigation Matrices",
)


@blp.route("/", methods=["POST"])
@blp.arguments(
    MMGenRequestSchema,
    example={
        "provider": "IBM",
        "qpu": "aer_qasm_simulator",
        "credentials": {"token": "YOUR_TOKEN"},
        "qubits": [0, 1, 2, 3, 4],
        "cm_gen_method": "standard",
        "mitigation_method": "inversion",
        "shots": 1000,
        "noise_model": "ibmq_lima",
        "only_measurement_errors": "True",
    },
)
@blp.response(200)
def generate(json: MMGenRequest):
    print(json)
    if json:
        return generate_mm(MMGenRequest(**json))


@blp.route("/", methods=["GET"])
@blp.arguments(MMGetRequestSchema, location="query")
@blp.response(200)
def retrieve(request):
    qpu = str(request.get("qpu"))
    cm_gen_method = str(request.get("cm_gen_method"))
    mitigation_method = str(request.get("mitigation_method"))
    qubits = request.get("qubits")
    max_age = int(request.get("max_age"))
    noise_model = str(request.get("noise_model"))
    only_measurement_errors = bool(request.get("only_measurement_errors"))

    req = MMGetRequest(
        qpu=qpu,
        cm_gen_method=cm_gen_method,
        mitigation_method=mitigation_method,
        qubits=qubits,
        max_age=max_age,
        noise_model=noise_model,
        only_measurement_errors=only_measurement_errors,
    )
    mm, _ = retrieve_mm(req)
    return mm.tolist() if mm is not None else "No suitable matrix found"
