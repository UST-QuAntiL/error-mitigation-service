import marshmallow as ma


class CMGenRequest:
    def __init__(self, cm_gen_method, provider, qpu, qubits, credentials, shots=1000):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.credentials = credentials
        self.cm_gen_method = cm_gen_method


class CMGenRequestSchema(ma.Schema):
    cm_gen_method = ma.fields.String(required=True)
    provider = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=True)


class CMGetRequest:
    def __init__(self, qpu, cm_gen_method=None, qubits=None, max_age=1440):
        self.qpu = qpu
        self.qubits = qubits
        self.cm_gen_method = cm_gen_method
        self.max_age = max_age


class CMGetRequestSchema(ma.Schema):
    cm_gen_method = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    max_age = ma.fields.Integer(required=False)
