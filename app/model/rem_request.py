import marshmallow as ma
from marshmallow import fields, ValidationError


class REMRequest:
    def __init__(
        self,
        counts,
        qpu,
        qubits,
        mitigation_method,
        cm_gen_method=None,
        time_of_execution=None,
        provider=None,
        shots=None,
        credentials=None,
        max_age=1440,
        noise_model=None,
        only_measurement_errors=False
    ):
        self.qpu = qpu
        self.qubits = qubits
        self.cm_gen_method = cm_gen_method
        self.mitigation_method = mitigation_method
        self.max_age = max_age
        self.time_of_execution = time_of_execution
        self.counts = counts
        self.provider = provider
        self.shots = shots
        self.credentials = credentials
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors


class CountsField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list):
            if all(isinstance(x, dict) for x in value):
                return value
            else:
                raise ValidationError(
                    "Field should be list of dicts with bitstring as key and counts as measurement, e.g., [{'0': 980, '1': 20}] "
                )
        elif isinstance(value, dict):
            return value
        else:
            raise ValidationError(
                "Field should be list of dicts with bitstring as key and counts as measurement, e.g., [{'0': 980, '1': 20}] "
            )


class QubitsArrayField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list):
            if all(isinstance(x, int) for x in value):
                return value
            elif all(isinstance(x, list) for x in value) and all(
                all(isinstance(y, int) for y in x) for x in value
            ):
                return value
            else:
                raise ValidationError(
                    "Field should be list of integers or list of list of integers"
                )
        else:
            raise ValidationError(
                "Field should be list of integers or list of list of integers"
            )


class REMRequestSchema(ma.Schema):
    counts = CountsField(required=True)
    cm_gen_method = ma.fields.String(required=False)
    mitigation_method = ma.fields.String(required=False)
    qpu = ma.fields.String(required=True)
    qubits = QubitsArrayField(required=True)
    max_age = ma.fields.Integer(required=False)
    time_of_execution = ma.fields.DateTime(
        "%Y-%m-%d_%H-%M-%S", required=False, description="format:Y-m-d_H-M-S"
    )
    provider = ma.fields.String(required=False)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(
        required=False, description="Dictionary containing all required credentials"
    )
    noise_model = ma.fields.Str(required=False)
    only_measurement_errors = ma.fields.Boolean(required=False)
