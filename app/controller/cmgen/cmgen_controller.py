from flask_smorest import Blueprint
from ...model.cmgen_request import (
    CMGenRequest,
    CMGenRequestSchema,
    CMGenFromCountsRequestSchema,
    CMGenFromCountsRequest,
    CMGetRequest,
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
    example=dict(
        provider="IBM",
        qpu="ibmq_lima",
        method="standard",
        qubits=[0, 1, 2, 4],
        shots=1000,
        credentials="YOUR_CREDENTIALS",
    ),
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
        counts="[{'0':990, '1':10},{'0':30, '1':970}]",
        qpu="ibmq_lima",
        method="standard",
        qubits=[0],
    ),
)
@blp.response(200)
def generate(json: CMGenFromCountsRequest):
    print(json)
    if json:
        return generate_cm_from_counts(CMGenFromCountsRequest(**json))


@blp.route("/", methods=["GET"])
@blp.response(200)
def retrieve():
    qpu = str(request.args.get("qpu"))
    cm_gen_method = str(request.args.get("cm_gen_method"))
    qubits = request.args.get("qubits")
    max_age = int(request.args.get("max_age"))
    req = CMGetRequest(
        qpu=qpu, cm_gen_method=cm_gen_method, qubits=qubits, max_age=max_age
    )
    cm, _ = retrieve_cm(req)
    return cm
