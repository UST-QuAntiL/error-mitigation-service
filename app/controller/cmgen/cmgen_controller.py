from flask_smorest import Blueprint
from ...model.cmgen_request import (
    CMGenRequest,
    CMGenRequestSchema,
    CMGenFromCountsRequestSchema,
    CMGenFromCountsRequest,
    CMGetRequest,
    CMGetRequestSchema,
)
from app.services.cmgen_services.cmgen_service import (
    generate_cm,
    retrieve_cm,
    generate_cm_from_counts,
)
from flask import request

blp = Blueprint(
    "Calibration Matrix",
    __name__,
    url_prefix="/cm",
    description="Generate and Request Calibration Matrices",
)


@blp.route("/", methods=["POST"])
@blp.arguments(
    CMGenRequestSchema,
    example={
        "provider": "IBM",
        "qpu": "aer_qasm_simulator",
        "credentials": {"token": "YOUR_TOKEN"},
        "qubits": [0, 1, 2, 3, 4],
        "cm_gen_method": "standard",
        "shots": 1000,
        "noise_model": "ibmq_lima",
        "only_measurement_errors": False,
    },
)
@blp.response(200)
def generate(json: CMGenRequest):
    print(json)
    if json:
        return generate_cm(CMGenRequest(**json))


@blp.route("/fromCounts", methods=["POST"])
@blp.arguments(
    CMGenFromCountsRequestSchema,
    example=dict(
        counts=[{"0": 990, "1": 10}, {"0": 30, "1": 970}],
        qpu="ibmq_lima",
        cm_gen_method="standard",
        qubits=[0],
    ),
)
@blp.response(200)
def generate(json: CMGenFromCountsRequest):
    print(json)
    if json:
        return generate_cm_from_counts(CMGenFromCountsRequest(**json))


@blp.route("/", methods=["GET"])
@blp.arguments(CMGetRequestSchema, location="query")
@blp.response(200)
def retrieve(request):
    qpu = str(request.get("qpu"))
    cm_gen_method = str(request.get("cm_gen_method"))
    qubits = request.get("qubits")
    max_age = int(request.get("max_age"))
    noise_model = str(request.get("noise_model"))
    only_measurement_errors = bool(request.get("only_measurement_errors"))

    req = CMGetRequest(
        qpu=qpu,
        cm_gen_method=cm_gen_method,
        qubits=qubits,
        max_age=max_age,
        noise_model=noise_model,
        only_measurement_errors=only_measurement_errors,
    )
    cm, _ = retrieve_cm(req)
    return cm.tolist() if cm is not None else "No suitable matrix found"
