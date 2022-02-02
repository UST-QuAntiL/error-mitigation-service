import marshmallow as ma

class REMRequest:
    def __init__(self, counts, applmethod, cmgenmethod, qpu, qubits, mitmethod, maxage):
        self.qpu = qpu
        self.qubits = qubits
        self.cmgenmethod = cmgenmethod
        self.mitmethod = mitmethod
        self.applmethod = applmethod
        self.maxage = maxage
        self.counts= counts


class REMRequestSchema(ma.Schema):
    counts = ma.fields.List(ma.fields.Integer())
    applmethod = ma.fields.String()
    cmgenmethod = ma.fields.String()
    mitmethod = ma.fields.String()
    qpu = ma.fields.String()
    qubits = ma.fields.List(ma.fields.Integer())
    maxage = ma.fields.Integer()
