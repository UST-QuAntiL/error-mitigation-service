import io
import pickle
from minio import Minio
import sys
from app.model.matrix_types import MatrixType
from config import Config
import os
import numpy as np
from datetime import datetime


print(Config.MINIO_ENDPOINT)
client = Minio(
    Config.MINIO_ENDPOINT,
    access_key=Config.MINIO_USER,
    secret_key=Config.MINIO_PASSWORD,
    secure=Config.MINIO_SECURITY,
)

TMPDIR = os.path.join(os.getcwd(), "tmp")


def check_if_bucket_exists(bucketname):
    # Make QPU bucket if not exist.
    found = client.bucket_exists(bucketname)
    if not found:
        client.make_bucket(bucketname)
        print("Bucket '" + bucketname + "' created")
    else:
        print("Bucket '" + bucketname + "' already exists")


def store_matrix_object_in_db(matrix, qpu: str, matrix_type: MatrixType, **kwargs):
    """

    :param matrix: Calibration or Mitigation matrix as numpy compatible array
    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cm_gen_method: Method used for the generation of the calibration matrix
            mitigation_method: Method used for the generation of the mitigation matrix
            cm_gen_date: Date of cm generation
    :return:
    """
    filedate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = qpu + matrix_type.name + filedate + "." + "pkl"
    qpu = qpu.replace("_", "-")
    bucket = qpu + "-" + matrix_type.name

    matrix_data = io.BytesIO()
    pickle.dump(matrix, matrix_data)
    matrix_data.seek(0)
    size = matrix_data.getbuffer().nbytes

    check_if_bucket_exists(bucket)

    metadata = {"CreationDate": filedate}
    if matrix_type is MatrixType.cm:
        metadata["cm_gen_date"] = filedate
    for key, value in kwargs.items():
        metadata[key] = value
    try:
        client.put_object(
            bucket_name=bucket,
            object_name=filename,
            data=matrix_data,
            metadata=metadata,
            length=size,
        )
        return filename
    except:
        raise


def load_matrix_object_from_db(qpu, matrix_type: MatrixType, **kwargs):
    """

    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cm_gen_method: Method used for the generation of the calibration matrix
            mitigation_method: Method used for the generation of the mitigation matrix
            max_age: Maximum time since the execution of the calibration circuits
    :return:
    """
    # Get all matrix metadata for QPU
    qpu = qpu.replace("_", "-")
    bucket = qpu + "-" + matrix_type.name
    check_if_bucket_exists(bucket)

    objects = client.list_objects(bucket, include_user_meta=True)

    matrix_list = []
    for obj in objects:
        matrix_list.append(get_obj_metadata(obj))

    return_matrix = None

    qubits = kwargs["qubits"] if "qubits" in kwargs.keys() else None
    cm_gen_method = (
        kwargs["cm_gen_method"] if "cm_gen_method" in kwargs.keys() else None
    )
    mitigation_method = (
        kwargs["mitigation_method"] if "mitigation_method" in kwargs.keys() else None
    )
    time_of_execution = (
        kwargs["time_of_execution"] if "time_of_execution" in kwargs.keys() else None
    )

    def get_time_diff(elem):
        return abs(
            (
                time_of_execution
                - datetime.strptime(elem["cm_gen_date"], "%Y-%m-%d_%H-%M-%S")
            ).total_seconds()
        )

    if qubits or cm_gen_method or mitigation_method:
        fitting_matrices = matrix_list
        if qubits is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                if set(qubits) == set(matrix["qubits"])
            ]
        if cm_gen_method is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                if cm_gen_method == matrix["cm_gen_method"]
            ]
        if mitigation_method is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                if mitigation_method == matrix["mitigation_method"]
            ]

        if fitting_matrices:
            if time_of_execution is not None:
                # fitting_matrices.sort(key=get_time_diff)
                return_matrix = sorted(fitting_matrices, key=get_time_diff)[0]
            else:
                return_matrix = sorted(
                    fitting_matrices, key=lambda x: x["cm_gen_date"]
                )[-1]
    else:
        if time_of_execution is not None:
            # fitting_matrices.sort(key=get_time_diff)
            return_matrix = sorted(matrix_list, key=get_time_diff)[0]
        else:
            return_matrix = sorted(matrix_list, key=lambda x: x["cm_gen_date"])[-1]

    max_age = kwargs["max_age"] if "max_age" in kwargs.keys() else None
    if return_matrix and (
        max_age is None
        or (
            (time_of_execution or datetime.now())
            - datetime.strptime(return_matrix["cm_gen_date"], "%Y-%m-%d_%H-%M-%S")
        ).total_seconds()
        / 60
        < kwargs["max_age"]
    ):
        try:
            response = client.get_object(bucket, return_matrix["name"])
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
        return None, None


def load_mitigator_object_from_db_by_filename(
    qpu: str, matrix_type: MatrixType, filename: str
):
    qpu = qpu.replace("_", "-")
    bucket = qpu + "-" + matrix_type.name
    check_if_bucket_exists(bucket)

    objects = client.list_objects(bucket, include_user_meta=True)

    for obj in objects:
        if obj.object_name == filename:
            metadata = get_obj_metadata(obj)
            break
    try:
        response = client.get_object(bucket, filename)
        matrix_data = io.BytesIO(response.data)
        matrix_data.seek(0)
        matrix = pickle.load(matrix_data)
    finally:
        response.close()
        response.release_conn()
        return matrix, metadata


def get_obj_metadata(obj):
    metadata = {"name": obj.object_name}
    for key, value in obj.metadata.items():
        if key == "X-Amz-Meta-Qubits":
            metadata["qubits"] = [
                int(i) for i in obj.metadata.get("X-Amz-Meta-Qubits").split(",")
            ]
        else:
            updatedKey = str(key).replace("X-Amz-Meta-", "").lower()
            metadata[updatedKey] = value
    return metadata


if __name__ == "__main__":
    a = [[1.123123123123123123123123123, 2], [3, 4.1]]
    store_matrix_object_in_db(
        matrix=a,
        qpu="ibmq-test",
        matrix_type=MatrixType.cm,
        qubits=[0, 1, 2, 3, 4],
        cm_gen_method="standard",
        test="1",
    )
    res = load_matrix_object_from_db(
        qpu="ibmq-test", matrix_type=MatrixType.cm, qubits=[1, 2, 3, 4]
    )
    print(res)


########################################################
#                                                      #
#      LEGACY FEATURE - RATHER USE OBJECT INSTEAD      #
#                                                      #
########################################################

from app.utils.helper_functions import deprecated


@deprecated
def store_matrix_file_in_db(matrix, qpu: str, matrix_type: MatrixType, **kwargs):
    """

    :param matrix: Calibration or Mitigation matrix as numpy compatible array
    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cm_gen_method: Method used for the generation of the calibration matrix
            mitigation_method: Method used for the generation of the mitigation matrix
            cm_gen_date: Date of cm generation
    :return:
    """
    filedate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = qpu + matrix_type.name + filedate + "." + "npy"
    source_filepath = os.path.join(TMPDIR, filename)
    qpu = qpu.replace("_", "-")
    bucket = qpu + "-" + matrix_type.name

    # Save in TMP Folder
    np.save(source_filepath, matrix)

    check_if_bucket_exists(bucket)

    # Upload SOURCE_FILEPATH as object name FILENAME to bucket QPU
    metadata = {"CreationDate": filedate}
    if matrix_type is MatrixType.cm:
        metadata["cm_gen_date"] = filedate
    for key, value in kwargs.items():
        metadata[key] = value
    try:
        client.fput_object(bucket, filename, source_filepath, metadata=metadata)
    finally:
        os.remove(source_filepath)
        return filename


@deprecated
def load_matrix_file_from_db(qpu, matrix_type: MatrixType, **kwargs):
    """

    :param qpu: Name of the used QPU
    :param matrix_type: CM or MM (CalibrationMatrix or MitigationMatrix)
    :param kwargs:
            qubits: Array of used qubits, e.g., [0,1,2,3,7,8]
            cm_gen_method: Method used for the generation of the calibration matrix
            mitigation_method: Method used for the generation of the mitigation matrix
            max_age: Maximum time since the execution of the calibration circuits
    :return:
    """
    # Get all matrix metadata for QPU
    qpu = qpu.replace("_", "-")
    bucket = qpu + "-" + matrix_type.name
    check_if_bucket_exists(bucket)

    objects = client.list_objects(bucket, include_user_meta=True)

    matrix_list = []
    for obj in objects:
        matrix_list.append(get_obj_metadata(obj))
    return_matrix = None

    qubits = kwargs["qubits"] if "qubits" in kwargs.keys() else None
    cm_gen_method = (
        kwargs["cm_gen_method"] if "cm_gen_method" in kwargs.keys() else None
    )
    mitigation_method = (
        kwargs["mitigation_method"] if "mitigation_method" in kwargs.keys() else None
    )
    if qubits or cm_gen_method or mitigation_method:
        fitting_matrices = matrix_list
        if qubits is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                if set(qubits) == set(matrix["qubits"])
            ]
        if cm_gen_method is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                if cm_gen_method == matrix["cm_gen_method"]
            ]
        if mitigation_method is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                if mitigation_method == matrix["mitigation_method"]
            ]

        if fitting_matrices:
            return_matrix = sorted(fitting_matrices, key=lambda x: x["cm_gen_date"])[-1]
    else:
        return_matrix = sorted(matrix_list, key=lambda x: x["cm_gen_date"])[-1]

    max_age = kwargs["max_age"] if "max_age" in kwargs.keys() else None
    if return_matrix and (
        max_age is None
        or (
            datetime.now()
            - datetime.strptime(return_matrix["cm_gen_date"], "%Y-%m-%d,_%H-%M-%S")
        ).total_seconds()
        / 60
        < kwargs["max_age"]
    ):
        savepath = os.path.join(TMPDIR, return_matrix["name"])
        res = client.fget_object(bucket, return_matrix["name"], savepath)
        matrix = np.load(os.path.join(TMPDIR, res.object_name)).tolist()
        os.remove(savepath)
        return matrix, return_matrix
    else:
        return
