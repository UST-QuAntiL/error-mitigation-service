import marshmallow as ma
from marshmallow import pre_load, ValidationError
import numpy as np


class HHLAlgorithmRequest:
    def __init__(self, matrix, vector):
        self.matrix = matrix
        self.vector = vector


class HHLAlgorithmRequestSchema(ma.Schema):
    matrix = ma.fields.List(ma.fields.List(ma.fields.Float()))
    vector = ma.fields.List(ma.fields.Float())


class QAOAAlgorithmRequest:
    def __init__(self, pauli_op_string, gammas, betas):
        self.pauli_op_string = pauli_op_string
        self.reps = reps
        self.gammas = gammas
        self.betas = betas


class QAOAAlgorithmRequestSchema(ma.Schema):
    pauli_op_string = ma.fields.String()
    reps = ma.fields.Int()
    gammas = ma.fields.List(ma.fields.Float())
    betas = ma.fields.List(ma.fields.Float())
