from flask_smorest import Blueprint
from ...model.circuit_response import CircuitResponseSchema
from ...model.encoding_request import (
    BasisEncodingRequestSchema,
    AngleEncodingRequestSchema,
    AmplitudeEncodingRequestSchema,
    SchmidtDecompositionRequestSchema,
    SchmidtDecompositionRequest,
    AmplitudeEncodingRequest,
    AngleEncodingRequest,
    BasisEncodingRequest,
)

blp = Blueprint(
    "encodings",
    __name__,
    url_prefix="/encoding",
    description="get quantum circuit encodings",
)


@blp.route("/basis", methods=["POST"])
@blp.etag
@blp.arguments(
    BasisEncodingRequestSchema,
    example=dict(vector=[1.25, 3.14], integral_bits=3, fractional_bits=3),
)
@blp.response(200, CircuitResponseSchema)
def encoding(json: BasisEncodingRequest):
    if json:
        return


@blp.route("/angle", methods=["POST"])
@blp.etag
@blp.arguments(
    AngleEncodingRequestSchema, example=dict(vector=[1.25, 3.14], rotationaxis="x")
)
@blp.response(200, CircuitResponseSchema)
def encoding(json: AngleEncodingRequest):
    if json:
        return


@blp.route("/amplitude", methods=["POST"])
@blp.etag
@blp.arguments(AmplitudeEncodingRequestSchema, example=dict(vector=[1.25, 3.14]))
@blp.response(200, CircuitResponseSchema)
def encoding(json: AmplitudeEncodingRequest):
    if json:
        return


@blp.route("/schmidt", methods=["POST"])
@blp.arguments(
    SchmidtDecompositionRequestSchema, example=dict(vector=[1.25, 3.14, 0, 1])
)
@blp.response(200, CircuitResponseSchema)
def encoding(json: SchmidtDecompositionRequest):
    if json:
        return
