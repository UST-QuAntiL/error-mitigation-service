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

def restore_dict_by_qubitorder(adjusted_counts_dict: dict, counts_qubits: list, mitigator_qubits: list):
    """
    :param adjusted_counts_dict: dictionary containing measurement counts
    :return:
    """
    mapping =[]
    for i in counts_qubits:
        mapping.append(mitigator_qubits.index(i))
    sorted_dict = {}
    for key, value in adjusted_counts_dict.items():
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


import functools
import inspect
import warnings

string_types = (type(b""), type(u""))


def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter("always", DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                warnings.simplefilter("default", DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))


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
    print("default",dict)
    sorted = sort_dict_by_qubitorder(dict, counts_qubits, mitiagor_qubits)
    print("sorted", sorted)
    print("restore", restore_dict_by_qubitorder(sorted, counts_qubits, mitiagor_qubits))
