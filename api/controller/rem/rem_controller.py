from flask_smorest import Blueprint
from api.model.rem_request import REMRequestSchema, REMRequest
from api.services.rem_services.rem_service import mitigate_results

blp = Blueprint(
    "rem",
    __name__,
    url_prefix="/rem",
    description="mitigate a circuit execution result",
)


@blp.route("/", methods=["POST"])
@blp.arguments(
    REMRequestSchema,
    example=dict(qpu="ibmq_lima", applmethod = "multiplication",counts={
    "000": 117,
    "001": 121,
    "010": 122,
    "011": 98,
    "100": 138,
    "101": 138,
    "110": 119,
    "111": 143
    }, qubits=[0,1,4]),
)
@blp.response(200)
def algorithm(json: REMRequest):
    print(json)
    if json:
        return mitigate_results(json)

