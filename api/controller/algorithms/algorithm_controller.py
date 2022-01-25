from flask_smorest import Blueprint
from ...model.circuit_response import CircuitResponseSchema
from ...model.algorithm_request import (
    HHLAlgorithmRequestSchema,
    HHLAlgorithmRequest,
    QAOAAlgorithmRequestSchema,
    QAOAAlgorithmRequest,
)


blp = Blueprint(
    "algorithms",
    __name__,
    url_prefix="/algorithms",
    description="get quantum circuit algorithms",
)


@blp.route("/hhl", methods=["POST"])
@blp.arguments(
    HHLAlgorithmRequestSchema,
    example=dict(matrix=[[1.5, 0.5], [0.5, 1.5]], vector=[0, 1]),
)
@blp.response(200, CircuitResponseSchema)
def algorithm(json: HHLAlgorithmRequest):
    if json:
        return


@blp.route("/qaoa", methods=["POST"])
@blp.arguments(
    QAOAAlgorithmRequestSchema,
    example=dict(
        pauli_op_string="0.5 * ((I^Z^Z) + (Z^I^Z) + (Z^Z^I))",
        reps=2,
        gammas=[1.0, 1.2],
        betas=[0.4, 0.7],
    ),
)
@blp.response(200, CircuitResponseSchema)
def algorithm(json: QAOAAlgorithmRequest):
    if json:
        return None
