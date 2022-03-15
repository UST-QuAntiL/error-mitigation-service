import marshmallow as ma

class CMGenRequest:
    def __init__(self, cmgenmethod, provider, qpu, qubits, shots, credentials):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.credentials = credentials
        self.cmgenmethod = cmgenmethod


class CMGenRequestSchema(ma.Schema):
    cmgenmethod = ma.fields.String()
    provider = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    shots = ma.fields.Integer()
    credentials = ma.fields.String()


class CMGetRequest:
    def __init__(self, qpu, cmgenmethod = None, qubits = None, max_age= 1440):
        self.qpu = qpu
        self.qubits = qubits
        self.cmgenmethod = cmgenmethod
        self.max_age= max_age


class CMGetRequestSchema(ma.Schema):
    cmgenmethod = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    max_age = ma.fields.Integer()

