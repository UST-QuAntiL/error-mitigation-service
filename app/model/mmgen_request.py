import marshmallow as ma


class MMGenRequest:
    def __init__(
        self,
        cm_gen_method,
        provider,
        qpu,
        qubits,
        credentials,
        mitigation_method,
        shots=1000,
        max_age=1440,
    ):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.credentials = credentials
        self.cm_gen_method = cm_gen_method
        self.mitigation_method = mitigation_method
        self.max_age = max_age


class MMGenRequestSchema(ma.Schema):
    cm_gen_method = ma.fields.String(required=False)
    mitigation_method = ma.fields.String(required=True)
    provider = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=True)
    max_age = ma.fields.Integer(required=False)


class MMGetRequest:
    def __init__(
        self, qpu, mitigation_method=None, cm_gen_method=None, qubits=None, max_age=1440
    ):
        self.qpu = qpu
        self.qubits = qubits
        self.mitigation_method = mitigation_method
        self.cm_gen_method = cm_gen_method
        self.max_age = max_age


class MMGetRequestSchema(ma.Schema):
    mitigation_method = ma.fields.String(required=True)
    cm_gen_method = ma.fields.String(required=False)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    max_age = ma.fields.Integer(required=False)
