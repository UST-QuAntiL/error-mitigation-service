import marshmallow as ma


class MMGenRequest:
    def __init__(
        self,
        cmgenmethod,
        provider,
        qpu,
        qubits,
        credentials,
        mitmethod,
        shots=1000,
        max_age=1440,
    ):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.credentials = credentials
        self.cmgenmethod = cmgenmethod
        self.mitmethod = mitmethod
        self.max_age = max_age


class MMGenRequestSchema(ma.Schema):
    cmgenmethod = ma.fields.String(required=False)
    mitmethod = ma.fields.String(required=True)
    provider = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=True)
    max_age = ma.fields.Integer(required=False)


class MMGetRequest:
    def __init__(
        self, qpu, mitmethod=None, cmgenmethod=None, qubits=None, max_age=1440
    ):
        self.qpu = qpu
        self.qubits = qubits
        self.mitmethod = mitmethod
        self.cmgenmethod = cmgenmethod
        self.max_age = max_age


class MMGetRequestSchema(ma.Schema):
    mitmethod = ma.fields.String(required=True)
    cmgenmethod = ma.fields.String(required=False)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    max_age = ma.fields.Integer(required=False)
