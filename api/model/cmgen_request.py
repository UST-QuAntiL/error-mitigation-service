import marshmallow as ma

class CMGenRequest:
    def __init__(self, method, provider, qpu, qubits, shots, token):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.token = token
        self.method = method


class CMGenRequestSchema(ma.Schema):
    method = ma.fields.String()
    provider = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    shots = ma.fields.Integer()
    token = ma.fields.String()


class CMGetRequest:
    def __init__(self, qpu, method = None, qubits = None, max_age= 1440):
        self.qpu = qpu
        self.qubits = qubits
        self.method = method
        self.max_age= max_age


class CMGetRequestSchema(ma.Schema):
    method = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    max_age = ma.fields.Integer()

