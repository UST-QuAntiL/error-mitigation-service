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
        noise_model=None,
        only_measurement_errors=False
    ):
        self.provider = provider
        self.qpu = qpu
        self.qubits = qubits
        self.shots = shots
        self.credentials = credentials
        self.cm_gen_method = cm_gen_method
        self.mitigation_method = mitigation_method
        self.max_age = max_age
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors


class MMGenRequestSchema(ma.Schema):
    cm_gen_method = ma.fields.String(required=False)
    mitigation_method = ma.fields.String(required=True)
    provider = ma.fields.String(required=True)
    qpu = ma.fields.String(required=True)
    qubits = ma.fields.List(ma.fields.Integer(), required=True)
    shots = ma.fields.Integer(required=False)
    credentials = ma.fields.Raw(required=True)
    max_age = ma.fields.Integer(required=False)
    noise_model = ma.fields.Str(required=False)
    only_measurement_errors = ma.fields.Boolean(required=False)


class MMGetRequest:
    def __init__(
        self, qpu, mitigation_method=None, cm_gen_method=None, qubits=None, max_age=1440, noise_model=None,
            only_measurement_errors=False
    ):
        self.qpu = qpu
        self.qubits = qubits
        self.mitigation_method = mitigation_method
        self.cm_gen_method = cm_gen_method
        self.max_age = max_age
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors

class MMGetRequestSchema(ma.Schema):
    mitigation_method = ma.fields.String(required=True, example="inversion")
    cm_gen_method = ma.fields.String(required=True, example="standard")
    qpu = ma.fields.String(required=True, example="aer_qasm_simulator")
    qubits = ma.fields.List(ma.fields.Integer(), required=True, example=[0, 1, 2, 3, 4])
    max_age = ma.fields.Integer(required=False, example=360)
    noise_model = ma.fields.Str(required=False, example="ibmq_lima")
    only_measurement_errors = ma.fields.Boolean(required=False, example=False)