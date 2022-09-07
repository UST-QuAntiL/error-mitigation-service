import marshmallow as ma
from marshmallow import fields, ValidationError


class CountsDictList(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list):
            if all(isinstance(x, dict) for x in value):
                return value
            else:
                raise ValidationError(
                    "Field should be list of dicts with bitstring as key and counts as measurement, e.g., [{'0': 980, '1': 20}] "
                )
        else:
            raise ValidationError(
                "Field should be list of dicts with bitstring as key and counts as measurement, e.g., [{'0': 980, '1': 20}] "
            )


class CMGenRequest:
    def __init__(self, cm_gen_method, provider, qpu, qubits, credentials, shots=1000, noise_model=None, only_measurement_errors=False):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.credentials = credentials
        self.cm_gen_method = cm_gen_method
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors


class CMGenRequestSchema(ma.Schema):
    cm_gen_method = ma.fields.String(required=True)
    provider = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=True)
    noise_model = ma.fields.Str(required=False)
    only_measurement_errors = ma.fields.Boolean(required=False)


class CMGetRequest:
    def __init__(self, qpu, cm_gen_method=None, qubits=None, max_age=1440, noise_model=None, only_measurement_errors=False):
        self.qpu = qpu
        self.qubits = qubits
        self.cm_gen_method = cm_gen_method
        self.max_age = max_age
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors



class CMGetRequestSchema(ma.Schema):
    cm_gen_method = ma.fields.String(required=True, example="standard")
    qpu = ma.fields.String(required=True, example="aer_qasm_simulator")
    qubits = ma.fields.List(ma.fields.Integer(), required=True, example=[0,1,2,3,4])
    max_age = ma.fields.Integer(required=False, example=360)
    noise_model = ma.fields.Str(required=False, example="ibmq_lima")
    only_measurement_errors = ma.fields.Boolean(required=False, example=False)


class CMGenFromCountsRequest:
    def __init__(self, counts, cm_gen_method, qpu, qubits):
        self.counts = counts
        self.qpu = qpu
        self.qubits = qubits
        self.cm_gen_method = cm_gen_method


class CMGenFromCountsRequestSchema(ma.Schema):
    counts = CountsDictList()
    cm_gen_method = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
