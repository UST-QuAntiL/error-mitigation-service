import io
import pickle
from minio import Minio
from app.model.matrix_types import MatrixType
from config import Config
import os
from datetime import datetime


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
        raise ConnectionError("File could not be stored in DB")


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
    print("retrieved bucket content from DB")
    matrix_list = []
    for obj in objects:
        matrix_list.append(get_obj_metadata(obj))

    return_matrix = None

    qubits = kwargs["qubits"] if "qubits" in kwargs.keys() else None

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

    # Check if matrix metadata matches request requirements
    if kwargs is not None:
        fitting_matrices = matrix_list
        if qubits is not None:
            fitting_matrices = [
                matrix
                for matrix in fitting_matrices
                # A matrix can be reused if the set is equal - the qubit order can be fixed in a later step
                if set(qubits) == set(matrix["qubits"])
            ]
        if kwargs is not None:
            for k, v in kwargs.items():
                if k and v and k != "max_age":
                    # Boolean values are stored as strings in the database metadata --> convert to string for comparison
                    v = str(v) if isinstance(v, bool) else v

                    fitting_matrices = [
                        matrix for matrix in fitting_matrices if v == matrix[k]
                    ]

        # Return matrix generated closest to the time of execution (if given) or most recently
        if fitting_matrices:
            if time_of_execution is not None:
                return_matrix = sorted(fitting_matrices, key=get_time_diff)[0]
            else:
                return_matrix = sorted(
                    fitting_matrices, key=lambda x: x["cm_gen_date"]
                )[-1]
    else:
        if time_of_execution is not None:
            return_matrix = sorted(matrix_list, key=get_time_diff)[0]
        else:
            return_matrix = sorted(matrix_list, key=lambda x: x["cm_gen_date"])[-1]

    # check if return matrix fulfills the max_age requirement
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
            raise ConnectionError("File could not be loaded")
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
    except:
        raise ConnectionError("File could not be loaded")
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