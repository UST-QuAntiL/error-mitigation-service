import marshmallow as ma


# TODO add timeofexecution as optional parameter for running old_data mitigation
from marshmallow import fields, ValidationError


class REMRequest:
    def __init__(
        self,
        counts,
        cmgenmethod,
        qpu,
        qubits,
        mitmethod,
        time_of_execution=None,
        provider=None,
        shots=None,
        credentials=None,
        maxage=1440,
    ):
        self.qpu = qpu
        self.qubits = qubits
        self.cmgenmethod = cmgenmethod
        self.mitmethod = mitmethod
        self.maxage = maxage
        self.timeofexecution = time_of_execution
        self.counts = counts
        self.provider = provider
        self.shots = shots
        self.credentials = credentials


class ValueField(fields.Field):
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
    cmgenmethod = ma.fields.String(required=False)
    mitmethod = ma.fields.String(required=False)
    qpu = ma.fields.String(required=True)
    # qubits = ma.fields.List(ma.fields.Integer(), required=True) \
    #          or ma.fields.List(ma.fields.List(ma.fields.Integer()), required=True)
    qubits = ValueField()
    maxage = ma.fields.Integer(required=False)
    timeofexecution = ma.fields.DateTime(required=False)
    provider = ma.fields.String(required=False)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=False)
