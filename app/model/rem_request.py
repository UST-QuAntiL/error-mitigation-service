import marshmallow as ma
from marshmallow import fields, ValidationError


class REMRequest:
    def __init__(
        self,
        counts,
        cm_gen_method,
        qpu,
        qubits,
        mitigation_method,
        time_of_execution=None,
        provider=None,
        shots=None,
        credentials=None,
        max_age=1440,
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


class QubitsArrayField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list):
            if all(isinstance(x, int) for x in value):
                return value
            elif all(isinstance(x, list) for x in value) and all(all(isinstance(y, int) for y in x) for x in value):
                return value
            else:
                raise ValidationError('Field should be list of integers or list of list of integers')
        else:
            raise ValidationError('Field should be list of integers or list of list of integers')

class REMRequestSchema(ma.Schema):


    counts = ma.fields.Raw(required=True)
    cm_gen_method = ma.fields.String(required=False)
    mitigation_method = ma.fields.String(required=False)
    qpu = ma.fields.String(required=True)
    qubits = QubitsArrayField()
    max_age = ma.fields.Integer(required=False)
    time_of_execution = ma.fields.DateTime("%Y-%m-%d_%H-%M-%S",required=False)
    provider = ma.fields.String(required=False)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=False)
