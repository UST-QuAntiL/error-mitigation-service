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
    example=dict(qpu="ibmq_lima", applmethod = "multiplication",counts=[50, 450, 460, 40], qubits=[0,1,2,4]),
)
@blp.response(200)
def algorithm(json: REMRequest):
    print(json)
    if json:
        return mitigate_results(json)

