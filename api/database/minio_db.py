from minio import Minio
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

# TODO  use kwargs for metadata, differentiate cm/mm filenames
def store_matrix_file_in_db(matrix, qpu, type, used_qubits, method):
    date = datetime.now().strftime("%Y-%m-%d,_%H-%M-%S")
    filename = qpu+type+date + "." + "npy"
    source_filepath = os.path.join(TMPDIR, filename)
    qpu = qpu.replace('_', '-')
    bucket = qpu+"-"+type

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
    try :
        client.fput_object(bucket, filename, source_filepath, metadata={"Date": date,"Used_qubits": used_qubits, "Gen_method": method})
    finally:
        os.remove(source_filepath)
        return filename


#TODO maxsize, priority, date ...
def load_matrix_file_from_db(qpu, type, method = None, used_qubits=None, max_age=360):
    #Get all matrix metadata for QPU
    qpu = qpu.replace('_', '-')
    bucket = qpu + "-"+type
    objects = client.list_objects(bucket, include_user_meta=True)

    matrix_list = [{"name": obj.object_name,
                    "date": obj.metadata.get('X-Amz-Meta-Date'),
                    "qubits": [int(i) for i in obj.metadata.get('X-Amz-Meta-Used_qubits').split(',')],
                    "method": obj.metadata.get('X-Amz-Meta-Gen_method')} for obj in objects]

    return_matrix = None

    if used_qubits or method:
        fitting_matrices = matrix_list
        print(fitting_matrices)
        if used_qubits:
            fitting_matrices = [matrix for matrix in fitting_matrices if set(used_qubits) <= set(matrix["qubits"])]
        print(fitting_matrices)
        if method:
            fitting_matrices = [matrix for matrix in fitting_matrices if method == matrix["method"]]
        print("fitting matrices",fitting_matrices)
        if fitting_matrices:
            return_matrix = sorted(fitting_matrices, key=lambda x: x["date"])[-1]
    else:
        return_matrix = sorted(matrix_list, key=lambda x: x["date"])[-1]

    if return_matrix and (not max_age or (datetime.now() - datetime.strptime(return_matrix["date"], "%Y-%m-%d,_%H-%M-%S")).total_seconds()/60 < max_age):
        savepath = os.path.join(TMPDIR, return_matrix["name"])
        res = client.fget_object(bucket, return_matrix["name"],savepath)
        matrix = np.load(os.path.join(TMPDIR, res.object_name)).tolist()
        os.remove(savepath)
        # TODO return matrix list, or file or whats best?
        return matrix, return_matrix["date"]
    else:
        return

if __name__ == "__main__":
    a = [[1,2],[3,4.1]]
    store_matrix_file_in_db(matrix=a, qpu='ibmq-test', type="cm", used_qubits=[0,1,2,3,4], method="standard")
    res = load_matrix_file_from_db(qpu="ibmq-test", type="cm", used_qubits=[1, 2, 3, 4])
    print(res)

if __name__ == "__main__":
    res = load_matrix_file_from_db("ibmq-lima", type="cm", method="standard", max_age=43)
    print(res)