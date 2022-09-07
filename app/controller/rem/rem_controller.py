from flask_smorest import Blueprint
from app.model.rem_request import REMRequestSchema, REMRequest
from app.services.rem_services.rem_service import mitigate_results

blp = Blueprint(
    "rem",
    __name__,
    url_prefix="/rem",
    description="mitigate a circuit execution result",
)


@blp.route("/", methods=["POST"])
@blp.arguments(
    REMRequestSchema,
    example=dict(
        provider="ibm",
        qpu="aer_qasm_simulator",
        noise_model="ibmq_lima",
        only_measurement_errors="False",
        credentials={"token": "YOUR_TOKEN"},
        cm_gen_method="standard",
        mitigation_method="inversion",
        counts={
            "10000": 112,
            "10001": 25,
            "10010": 631,
            "10011": 111,
            "10100": 615,
            "10101": 132,
            "10110": 2965,
            "10111": 604,
            "11000": 19,
            "11001": 3,
            "11010": 110,
            "11011": 23,
            "11100": 113,
            "11101": 32,
            "11110": 571,
            "11111": 119,
            "01000": 10,
            "00001": 4,
            "01101": 10,
            "00101": 30,
            "01011": 11,
            "00000": 40,
            "01110": 209,
            "01010": 45,
            "00010": 197,
            "00110": 951,
            "00100": 194,
            "00011": 38,
            "00111": 190,
            "01111": 41,
            "01100": 37,
        },
        shots=1000,
        qubits=[0, 1, 2, 3, 4],
        max_age=0,
    ),
)
@blp.response(200)
def algorithm(json: REMRequest):
    print(json)
    if json:
        return mitigate_results(REMRequest(**json))
