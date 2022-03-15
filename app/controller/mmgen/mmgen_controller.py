from flask_smorest import Blueprint
from flask import request

from app.model.mmgen_request import MMGenRequestSchema, MMGenRequest, MMGetRequest
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
def generate(json: MMGenRequest):
    print(json)
    if json:
        return generate_mm(MMGenRequest(**json))


@blp.route("/", methods=["GET"])
@blp.response(200)
def retrieve():
    qpu = str(request.args.get("qpu"))
    mitmethod = str(request.args.get("mitmethod"))
    cmgenmethod = str(request.args.get("mitmethod"))
    qubits = request.args.get("qubits")
    max_age = int(request.args.get("maxage"))
    req = MMGetRequest(
        qpu=qpu,
        cmgenmethod=cmgenmethod,
        mitmethod=mitmethod,
        qubits=qubits,
        max_age=max_age,
    )
    return retrieve_mm(req)
