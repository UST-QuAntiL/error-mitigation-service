import marshmallow as ma


class MMGenRequest:
    def __init__(self, cmgenmethod, provider, qpu, qubits, shots, token, mitmethod, maxage):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.token = token
        self.cmgenmethod = cmgenmethod
        self.mitmethod = mitmethod
        self.maxage = maxage


class MMGenRequestSchema(ma.Schema):
    cmgenmethod = ma.fields.String()
    mitmethod = ma.fields.String()
    provider = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    shots = ma.fields.Integer()
    token = ma.fields.String()
    maxage = ma.fields.Integer()


class MMGetRequest:
    def __init__(self, qpu, mitmethod = None, cmgenmethod = None, qubits = None, max_age= 1440):
        self.qpu = qpu
        self.qubits = qubits
        self.mitmethod = mitmethod
        self.cmgenmethod = cmgenmethod
        self.max_age= max_age


class MMGetRequestSchema(ma.Schema):
    mitmethod = ma.fields.String()
    cmgenmethod = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    max_age = ma.fields.Integer()

