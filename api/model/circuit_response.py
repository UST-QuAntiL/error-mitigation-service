from datetime import datetime
import marshmallow as ma
from .encoding_request import BasisEncodingRequestSchema
from .algorithm_request import HHLAlgorithmRequestSchema


class CircuitResponse:
    def __init__(self, circuit, circuit_type, n_qubits, depth, input):
        super().__init__()
        self.circuit = circuit
        self.circuit_type = circuit_type
        self.n_qubits = n_qubits
        self.depth = depth
        self.input = input
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def to_json(self):
        json_circuit_response = {
            "circuit": self.circuit,
            "circuit_type": self.circuit_type,
            "n_qubits": self.n_qubits,
            "depth": self.depth,
            "timestamp": self.timestamp,
            "input": self.input,
        }
        return json_circuit_response


class CircuitResponseSchema(ma.Schema):
    circuit = ma.fields.String()
    circuit_type = ma.fields.String()
    n_qubits = ma.fields.Int()
    depth = ma.fields.Int()
    timestamp = ma.fields.String()
    # TODO change BasisEncodingRequestSchema for algorithms
    # input = ma.fields.Nested(HHLAlgorithmRequestSchema)
    input = ma.fields.Nested(BasisEncodingRequestSchema)
