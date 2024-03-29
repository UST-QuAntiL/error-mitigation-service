# Error Mitigation Service for NISQ Devices

![Tests passed](https://github.com/UST-QuAntiL/error-mitigation-service/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/UST-QuAntiL/error-mitigation-service/branch/master/graph/badge.svg?token=7S4XT6UJNR)](https://codecov.io/gh/UST-QuAntiL/error-mitigation-service)

The error mitigation service can mitigate the impact of errors of noisy measurement results obtained from a quantum computer.

This service enables the generation and management of calibration and mitigation data for multiple QPU providers.
Further, it allows users to mitigate their execution results based on newly generated or already existing mitigation data, speeding up the error mitigation process.
The error mitigation service currently implements various methods, such as [Mthree](https://journals.aps.org/prxquantum/pdf/10.1103/PRXQuantum.2.040326) or [TPNM](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.103.042605) for IBMQ and IonQ.
Moreover, the service enables to simulate error mitigation for results obtained on noisy quantum simulators. 
Thereby, users can choose between complete noise models and noise models only containing readout errors.

## Running the Service

The easiest way to get start is using [Docker-Compose](https://docs.docker.com/compose/): 
1. Clone the repository using ``git clone https://github.com/UST-QuAntiL/error-mitigation-service.git``
2. Navigate to the repository and start it by running ``docker-compose up``

Then the service can be accessed via: [http://127.0.0.1:5071](http://127.0.0.1:5071).

## API Documentation

The error mitigation services provides a Swagger UI, specifying the request schemas and showcasing exemplary requests for all API endpoints.
 * Swagger UI: [http://127.0.0.1:5071/api/swagger-ui](http://127.0.0.1:5071/api/swagger-ui).

## Developer Guide

### Setup (exemplary for ubuntu 18.04): 
```shell
git clone https://github.com/UST-QuAntiL/error-mitigation-service.git
cd error-mitigation-service

# if virtualenv is not installed
sudo -H pip install virtualenv

# create new virtualenv called 'venv'
virtualenv venv

# activate virtualenv; in Windows systems activate might be in 'venv/Scripts'
source venv/bin/activate

#install service requirements.
pip install -r requirements.txt
```

Note: The error mitigation service uses [MinIO](https://docs.min.io/docs/deploy-minio-on-docker-compose.html) for data storage and management.
Further, [Qiskit-Service](https://github.com/UST-QuAntiL/qiskit-service) needs to be running for the execution of quantum circuits on IBM quantum devices.
It is recommended to use the setup included in the [docker-compose.yml](./docker-compose.yml) file for deploying these services.

### Execution:

* Run the service with: ``flask run --port=5071``
* Test with: ``python -m unittest discover`` 
* Coverage with: ``coverage run --branch --include 'app/*' -m unittest discover; coverage report``

Note: Make sure to have included all required credentials as environment variables for testing when running tests.

### Codestyle: 
``black . `` OR ``black FILE|DIRECTORY``

## Disclaimer of Warranty
Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.

## Haftungsausschluss
Dies ist ein Forschungsprototyp. Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.

## Acknowledgements
The initial code contribution has been supported by the project [SEQUOIA](https://www.iaas.uni-stuttgart.de/forschung/projekte/sequoia/) funded by the [Baden-Wuerttemberg Ministry of the Economy, Labour and Housing](https://wm.baden-wuerttemberg.de/).