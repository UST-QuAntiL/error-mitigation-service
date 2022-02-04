import io
import pickle
from minio import Minio
import sys
from api.model.matrix_types import MatrixType
from config import Config
import os
import numpy as np
from datetime import datetime


client = Minio(
        Config.MINIO_ENDPOINT,
        access_key=Config.MINIO_USER,
        secret_key=Config.MINIO_PASSWORD,
        secure=Config.MINIO_SECURITY,
    )

TMPDIR = os.path.join(os.getcwd(), "tmp")

def store_matrix_object_in_db(matrix, qpu: str, matrix_type: MatrixType, **kwargs):
    """

    :param matrix: Calibration or Mitigation matrix as numpy compatible array
    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cmgenmethod: Method used for the generation of the calibration matrix
            mmgenmethod: Method used for the generation of the mitigation matrix
            cmgendate: Date of cm generation
    :return:
    """
    filedate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = qpu+matrix_type.name+filedate + "." + "pkl"
    qpu = qpu.replace('_', '-')
    bucket = qpu+"-"+matrix_type.name

    matrix_data = io.BytesIO()
    pickle.dump(matrix, matrix_data)
    matrix_data.seek(0)
    size =matrix_data.getbuffer().nbytes



    # Make QPU bucket if not exist.
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)
        print("Bucket '" + bucket + "' created")
    else:
        print("Bucket '" + bucket + "' already exists")

    # TODO delte file or don't save as file and directly upload - or other temp directory
    # Upload SOURCE_FILEPATH as object name FILENAME to bucket QPU
    metadata = {"CreationDate": filedate}
    if matrix_type is MatrixType.cm:
        metadata['cmgendate'] = filedate
    for key, value in kwargs.items():
        metadata[key] = value
    try :
        client.put_object(bucket_name=bucket, object_name=filename, data=matrix_data, metadata=metadata, length=size)
        return filename
    except:
        raise





def store_matrix_file_in_db(matrix, qpu: str, matrix_type: MatrixType, **kwargs):
    """

    :param matrix: Calibration or Mitigation matrix as numpy compatible array
    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cmgenmethod: Method used for the generation of the calibration matrix
            mmgenmethod: Method used for the generation of the mitigation matrix
            cmgendate: Date of cm generation
    :return:
    """
    filedate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = qpu+matrix_type.name+filedate + "." + "npy"
    source_filepath = os.path.join(TMPDIR, filename)
    qpu = qpu.replace('_', '-')
    bucket = qpu+"-"+matrix_type.name

    #Save in TMP Folder
    np.save(source_filepath, matrix)

    # Make QPU bucket if not exist.
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)
        print("Bucket '" + bucket + "' created")
    else:
        print("Bucket '" + bucket + "' already exists")

    # TODO delte file or don't save as file and directly upload - or other temp directory
    # Upload SOURCE_FILEPATH as object name FILENAME to bucket QPU
    metadata = {"CreationDate": filedate}
    if matrix_type is MatrixType.cm:
        metadata['cmgendate'] = filedate
    for key, value in kwargs.items():
        metadata[key] = value
    try :
        client.fput_object(bucket, filename, source_filepath, metadata=metadata)
    finally:
        os.remove(source_filepath)
        return filename


def load_matrix_object_from_db(qpu, matrix_type: MatrixType, **kwargs):
    """

    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cmgenmethod: Method used for the generation of the calibration matrix
            mmgenmethod: Method used for the generation of the mitigation matrix
            max_age: Maximum time since the execution of the calibration circuits
    :return:
    """
    #Get all matrix metadata for QPU
    qpu = qpu.replace('_', '-')
    bucket = qpu + "-"+matrix_type.name
    objects = client.list_objects(bucket, include_user_meta=True)

    matrix_list =[]
    for obj in objects:
        metadata = {"name": obj.object_name
                    }
        for key, value in obj.metadata.items():
            if key == 'X-Amz-Meta-Qubits':
                metadata["qubits"] = [int(i) for i in obj.metadata.get('X-Amz-Meta-Qubits').split(',')]
            else:
                updatedKey= str(key).replace('X-Amz-Meta-','').lower()
                metadata[updatedKey]= value
        matrix_list.append(metadata)

    return_matrix = None

    qubits = kwargs['qubits'] if 'qubits' in kwargs.keys() else None
    cmgenmethod = kwargs['cmgenmethod'] if 'cmgenmethod' in kwargs.keys() else None
    mmgenmethod = kwargs['mmgenmethod'] if 'mmgenmethod' in kwargs.keys() else None
    if qubits or cmgenmethod or mmgenmethod:
        fitting_matrices = matrix_list
        if qubits is not None:
            fitting_matrices = [matrix for matrix in fitting_matrices if set(qubits) <= set(matrix["qubits"])]
        if cmgenmethod is not None:
            fitting_matrices = [matrix for matrix in fitting_matrices if cmgenmethod == matrix["cmgenmethod"]]
        if mmgenmethod is not None:
            fitting_matrices = [matrix for matrix in fitting_matrices if mmgenmethod == matrix["mmgenmethod"]]

        if fitting_matrices:
            return_matrix = sorted(fitting_matrices, key=lambda x: x["cmgendate"])[-1]
    else:
        return_matrix = sorted(matrix_list, key=lambda x: x["cmgendate"])[-1]

    max_age = kwargs['max_age'] if 'max_age' in kwargs.keys() else None
    if return_matrix and ( max_age is None or (datetime.now() - datetime.strptime(return_matrix["cmgendate"], "%Y-%m-%d_%H-%M-%S")).total_seconds()/60 < kwargs['max_age']):
        try:
            response = client.get_object(bucket,return_matrix["name"])
            matrix_data = io.BytesIO(response.data)
            # matrix_data = response.data
            matrix_data.seek(0)
            matrix = pickle.load(matrix_data)
        except:
            raise
        finally:
            response.close()
            response.release_conn()
            return matrix, return_matrix
    else:
        return




#TODO maxsize, priority, date ...
def load_matrix_file_from_db(qpu, matrix_type: MatrixType, **kwargs):
    """

    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cmgenmethod: Method used for the generation of the calibration matrix
            mmgenmethod: Method used for the generation of the mitigation matrix
            max_age: Maximum time since the execution of the calibration circuits
    :return:
    """
    #Get all matrix metadata for QPU
    qpu = qpu.replace('_', '-')
    bucket = qpu + "-"+matrix_type.name
    objects = client.list_objects(bucket, include_user_meta=True)

    matrix_list =[]
    for obj in objects:
        metadata = {"name": obj.object_name
                    }
        for key, value in obj.metadata.items():
            if key == 'X-Amz-Meta-Qubits':
                metadata["qubits"] = [int(i) for i in obj.metadata.get('X-Amz-Meta-Qubits').split(',')]
            else:
                updatedKey= str(key).replace('X-Amz-Meta-','').lower()
                metadata[updatedKey]= value
        matrix_list.append(metadata)

    return_matrix = None

    qubits = kwargs['qubits'] if 'qubits' in kwargs.keys() else None
    cmgenmethod = kwargs['cmgenmethod'] if 'cmgenmethod' in kwargs.keys() else None
    mmgenmethod = kwargs['mmgenmethod'] if 'mmgenmethod' in kwargs.keys() else None
    if qubits or cmgenmethod or mmgenmethod:
        fitting_matrices = matrix_list
        if qubits is not None:
            fitting_matrices = [matrix for matrix in fitting_matrices if set(qubits) <= set(matrix["qubits"])]
        if cmgenmethod is not None:
            fitting_matrices = [matrix for matrix in fitting_matrices if cmgenmethod == matrix["cmgenmethod"]]
        if mmgenmethod is not None:
            fitting_matrices = [matrix for matrix in fitting_matrices if mmgenmethod == matrix["mmgenmethod"]]

        if fitting_matrices:
            return_matrix = sorted(fitting_matrices, key=lambda x: x["cmgendate"])[-1]
    else:
        return_matrix = sorted(matrix_list, key=lambda x: x["cmgendate"])[-1]

    max_age = kwargs['max_age'] if 'max_age' in kwargs.keys() else None
    if return_matrix and ( max_age is None or (datetime.now() - datetime.strptime(return_matrix["cmgendate"], "%Y-%m-%d,_%H-%M-%S")).total_seconds()/60 < kwargs['max_age']):
        savepath = os.path.join(TMPDIR, return_matrix["name"])
        res = client.fget_object(bucket, return_matrix["name"],savepath)
        matrix = np.load(os.path.join(TMPDIR, res.object_name)).tolist()
        os.remove(savepath)
        # TODO return matrix list, or file or whats best?
        return matrix, return_matrix
    else:
        return

# if __name__ == "__main__":
    # a = [[1,2],[3,4.1]]
    # store_matrix_file_in_db(matrix=a, qpu='ibmq-test', matrix_type=MatrixType.cm, qubits=[0,1,2,3,4], cmgenmethod="standard", test="1")
    # res = load_matrix_file_from_db(qpu="ibmq-test", matrix_type=MatrixType.cm, qubits=[1, 2, 3, 4])
    # print(res)

# if __name__ == "__main__":
#     res = load_matrix_file_from_db("ibmq-lima", matrix_type="cm", method="standard", max_age=43)
#     print(res)
if __name__ == "__main__":
    a = [[1.123123123123123123123123123, 2], [3, 4.1]]
    store_matrix_object_in_db(matrix=a, qpu='ibmq-test', matrix_type=MatrixType.cm, qubits=[0,1,2,3,4], cmgenmethod="standard", test="1")
    res = load_matrix_object_from_db(qpu="ibmq-test", matrix_type=MatrixType.cm, qubits=[1, 2, 3, 4])
    print(res)