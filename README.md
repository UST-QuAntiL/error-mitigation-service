![Tests passed](https://github.com/UST-QuAntiL/Quokka/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/UST-QuAntiL/error-mitigation-service/branch/main/graph/badge.svg?token=7S4XT6UJNR)](https://codecov.io/gh/UST-QuAntiL/error-mitigation-service)

# Error mitigation service for NISQ devices

The error mitigation service can mitigate the impact of errors of noisy measurement results obtained from a quantum computer.

The service enables the generation and management of calibration and mitigation data for multiple QPU providers.
Further, it allows users to mitigate their execution results on the basis of freshly generated or already existing mitigation data, speeding up the typical error mitigation process.
The error mitigation service currently implements multiple methods, such as [Mthree](https://journals.aps.org/prxquantum/pdf/10.1103/PRXQuantum.2.040326) or [TPNM](https://journals.aps.org/pra/pdf/10.1103/PhysRevA.103.042605?casa_token=koyKjM2FHGYAAAAA%3ATh-Or-IqYFWgEC-EN3qskcbL4_mOchqyBAfxCRU4cR203XJCGdlI5GpIVjfMgGZ3E_jfZqAhDcwXLw) for IBMQ and IonQ.
Additional mitigation methods and QPU providers can easily be integrated into the service.


### Running the Application
Run the App with [Docker-Compose](https://docs.docker.com/compose/)

``docker-compose up``

### API Structure
In the following the structure of the error mitigation service API is explained briefly.
The full API specification can be found [here](http://127.0.0.1:5000/api/swagger-ui) when the service is running.

#### /cm
Endpoint for generating calibration matrices by generating and running calibration circuits on QPUs.

#### /mm
Endpoint for generating mitigators based on calibration data. 
If no calibration data is available, it will automatically be generated if the required QPU credentials are included in the request.
Mitigators can be used to mitigate execution results.

#### /rem
Endpoint for mitigating results retrieved from circuit executions on NISQ devices.
If no calibration data is available, it will automatically be generated if the required QPU credentials are included in the request.



## Developer Guide

### Setup (exemplary for ubuntu 18.04): 
* ``git clone https://github.com/UST-QuAntiL/error-mitigation-service.git`` 
* ``cd error-mitigation-service``
* ``sudo -H pip install virtualenv`` (if you don't have virtualenv installed)
* ``virtualenv venv`` (create virtualenv named 'venv')
* ``source venv/bin/activate`` (enter virtualenv; in Windows systems activate might be in ``venv/Scripts``)
* ``pip install -r requirements.txt`` (install application requirements)

Note: [MinIO](https://docs.min.io/docs/deploy-minio-on-docker-compose.html) needs to be running for the error-mitigation-service to work. For setting up MinIO, it is recommended to use the setup included in the ``docker-compose.yml`` file .

### Execution:
* Run with: ``flask run``
* Test with: ``flask test``
* Coverage with: ``coverage run --branch --include 'api/*' -m unittest discover; coverage report``

#### Codestyle: 
``black . `` OR ``black FILE|DIRECTORY``

#### Update requirements with: 
``pip freeze>requirements.txt``

### Disclaimer of Warranty
Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.

### Haftungsausschluss
Dies ist ein Forschungsprototyp. Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.