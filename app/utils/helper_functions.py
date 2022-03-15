import numpy as np


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
    :return:
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


# qubits [2,4,1]
# qubits_mm[0,1,2,4,5]
# mapping_to_array_position [2,3,1]
# key = '101'
# position = 011000
# TODO not properly working
def countsdict_to_array(dict, qubits, qubits_mm):
    vector = np.zeros(2 ** len(qubits_mm))
    indices_mapping = []
    for qubit in qubits:
        indices_mapping.append(qubits_mm.index(qubit))
    for key, val in dict.items():
        binary = ""
        for i in range(len(qubits_mm)):

            if i in indices_mapping:
                index_in_qubits = indices_mapping.index(i)
                # index = qubits[index_in_qubits]
                binary += key[index_in_qubits]
            else:
                binary += "0"
            print(binary)
        array_index = int(binary, 2)
        vector[array_index] = val
    print(vector)


if __name__ == "__main__":
    dict = {
        "111": 129,
        "000": 131,
        "101": 134,
        "100": 142,
        "011": 97,
        "110": 117,
        "001": 125,
        "010": 125,
    }
    # qubits =[2,4,1]
    # qubits_mm = [0,1,2,4,5]
    #
    # countsdict_to_array(dict,qubits,qubits_mm)

    counts_qubits = [4, 2, 7]
    mitiagor_qubits = [7, 4, 2]
    sort_dict_by_qubitorder(dict, counts_qubits, mitiagor_qubits)
