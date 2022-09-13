import numpy as np
from qiskit.result import Counts


def dict_to_array(counts_dict: dict, n_qubits: int):
    array_counts = []
    for i in range(2 ** n_qubits):
        bitstring = "{:0{}b}".format(i, n_qubits)
        if bitstring in counts_dict:
            array_counts.append(counts_dict[bitstring])
        else:
            array_counts.append(0)
    return array_counts


def array_to_dict(counts_array: list, n_qubits: int):
    dict = {}
    for i, e in enumerate(counts_array):
        dict["{:0{}b}".format(i, n_qubits)] = e
    return dict


def sort_dict_by_qubitorder(
    counts_dict: dict, counts_qubits: list, mitigator_qubits: list
):
    """
    :param counts_dict: dictionary containing measurement counts
    :param counts_qubits:  list containing qubit order of measurement qubits
    :param mitigator_qubits:  list containing qubit order when creating mitigator
    :return: counts in qubit order
    """
    mapping = []
    for i in mitigator_qubits:
        mapping.append(counts_qubits.index(i))
    sorted_dict = {}
    for key, value in counts_dict.items():
        newkey = ""
        for i in mapping:
            newkey += key[i]
        sorted_dict[newkey] = value
    return sorted_dict


def restore_dict_by_qubitorder(
    adjusted_counts_dict: dict, counts_qubits: list, mitigator_qubits: list
):
    """
    :param adjusted_counts_dict: dictionary containing measurement counts
    :return: counts in restored qubit order
    """
    mapping = []
    for i in counts_qubits:
        mapping.append(mitigator_qubits.index(i))
    sorted_dict = {}
    for key, value in adjusted_counts_dict.items():
        newkey = ""
        for i in mapping:
            newkey += key[i]
        sorted_dict[newkey] = value
    return sorted_dict



class ResultsMock:
    def __init__(self, counts: list):
        """counts: list of dict"""
        self.counts = [Counts(c) for c in counts]

    def get_counts(self, i: int):
        return self.counts[i]
