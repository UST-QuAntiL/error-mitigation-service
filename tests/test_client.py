import unittest
import os, sys
import json
import re

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from app import create_app


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.app_context.pop()

    def test_app_running(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_cm_noisy_simulator(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/cm/",
            data=json.dumps(
                {
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": False,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(".pkl" in response.json)

        response_get = self.client.get(
            "/cm/?noise_model=ibmq_lima&cm_gen_method=standard&qpu=aer_qasm_simulator&qubits=0&qubits=1&qubits=2&qubits=3&qubits=4&max_age=360"
        )
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(len(response_get.json), 32)

    def test_cm_tpnm_noisy_simulator(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/cm/",
            data=json.dumps(
                {
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "tpnm",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": False,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(".pkl" in response.json)

    def test_gen_from_counts(self):
        response = self.client.post(
            "/cm/fromCounts",
            data=json.dumps(
                {
                    "counts": [
                        {
                            "00000": 902,
                            "10000": 39,
                            "00001": 18,
                            "00100": 16,
                            "01000": 7,
                            "00010": 16,
                            "00011": 1,
                            "10001": 1,
                        },
                        {
                            "11111": 863,
                            "11110": 51,
                            "11101": 30,
                            "11011": 11,
                            "01111": 15,
                            "10111": 15,
                            "01110": 3,
                            "01101": 4,
                            "11100": 3,
                            "10110": 1,
                            "11010": 2,
                            "10101": 1,
                            "10011": 1,
                        },
                    ],
                    "cm_gen_method": "tpnm",
                    "qpu": "aspen-m-1",
                    "qubits": [11, 16, 114, 17, 10],
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(".pkl" in response.json)

    def test_cm_noisy_simulator_only_measure(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/cm/",
            data=json.dumps(
                {
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(".pkl" in response.json)

    def test_mm_noisy_simulator(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/mm/",
            data=json.dumps(
                {
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "mitigation_method": "inversion",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": False,
                    "max_age": 0,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(".pkl" in response.json)

    def test_mm_noisy_simulator_only_measure(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/mm/",
            data=json.dumps(
                {
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "mitigation_method": "inversion",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(".pkl" in response.json)

        response_get = self.client.get(
            "/mm/?noise_model=ibmq_lima&cm_gen_method=standard&mitigation_method=inversion&qpu=aer_qasm_simulator&qubits=0&qubits=1&qubits=2&qubits=3&qubits=4&max_age=360"
        )
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(len(response_get.json), 32)

    def test_rem_noisy_simulator_only_measure_standard_inversion(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {
                    "counts": {
                        "10000": 112,
                        "10001": 25,
                        "10010": 631,
                        "10011": 111,
                        "10100": 615,
                        "10101": 132,
                        "10110": 2965,
                        "10111": 604,
                        "11000": 19,
                        "11001": 3,
                        "11010": 110,
                        "11011": 23,
                        "11100": 113,
                        "11101": 32,
                        "11110": 571,
                        "11111": 119,
                        "01000": 10,
                        "00001": 4,
                        "01101": 10,
                        "00101": 30,
                        "01011": 11,
                        "00000": 40,
                        "01110": 209,
                        "01010": 45,
                        "00010": 197,
                        "00110": 951,
                        "00100": 194,
                        "00011": 38,
                        "00111": 190,
                        "01111": 41,
                        "01100": 37,
                    },
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "mitigation_method": "inversion",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                    "max_age": 0,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("11110" in response.json.keys())

    def test_rem_noisy_simulator_only_measure_standard_inversion_reuse_mitigator(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {
                    "counts": {
                        "10000": 112,
                        "10001": 25,
                        "10010": 631,
                        "10011": 111,
                        "10100": 615,
                        "10101": 132,
                        "10110": 2965,
                        "10111": 604,
                        "11000": 19,
                        "11001": 3,
                        "11010": 110,
                        "11011": 23,
                        "11100": 113,
                        "11101": 32,
                        "11110": 571,
                        "11111": 119,
                        "01000": 10,
                        "00001": 4,
                        "01101": 10,
                        "00101": 30,
                        "01011": 11,
                        "00000": 40,
                        "01110": 209,
                        "01010": 45,
                        "00010": 197,
                        "00110": 951,
                        "00100": 194,
                        "00011": 38,
                        "00111": 190,
                        "01111": 41,
                        "01100": 37,
                    },
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "mitigation_method": "inversion",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                    "max_age": 300,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("11110" in response.json.keys())

    def test_rem_noisy_simulator_only_measure_ignis(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {
                    "counts": {
                        "10000": 112,
                        "10001": 25,
                        "10010": 631,
                        "10011": 111,
                        "10100": 615,
                        "10101": 132,
                        "10110": 2965,
                        "10111": 604,
                        "11000": 19,
                        "11001": 3,
                        "11010": 110,
                        "11011": 23,
                        "11100": 113,
                        "11101": 32,
                        "11110": 571,
                        "11111": 119,
                        "01000": 10,
                        "00001": 4,
                        "01101": 10,
                        "00101": 30,
                        "01011": 11,
                        "00000": 40,
                        "01110": 209,
                        "01010": 45,
                        "00010": 197,
                        "00110": 951,
                        "00100": 194,
                        "00011": 38,
                        "00111": 190,
                        "01111": 41,
                        "01100": 37,
                    },
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "mitigation_method": "ignis",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                    "max_age": 0,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("11110" in response.json.keys())

    def test_rem_noisy_simulator_only_measure_bayes(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {
                    "counts": {
                        "10000": 112,
                        "10001": 25,
                        "10010": 631,
                        "10011": 111,
                        "10100": 615,
                        "10101": 132,
                        "10110": 2965,
                        "10111": 604,
                        "11000": 19,
                        "11001": 3,
                        "11010": 110,
                        "11011": 23,
                        "11100": 113,
                        "11101": 32,
                        "11110": 571,
                        "11111": 119,
                        "01000": 10,
                        "00001": 4,
                        "01101": 10,
                        "00101": 30,
                        "01011": 11,
                        "00000": 40,
                        "01110": 209,
                        "01010": 45,
                        "00010": 197,
                        "00110": 951,
                        "00100": 194,
                        "00011": 38,
                        "00111": 190,
                        "01111": 41,
                        "01100": 37,
                    },
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "cm_gen_method": "standard",
                    "mitigation_method": "bayes",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                    "max_age": 0,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("11110" in response.json.keys())

    def test_rem_noisy_simulator_only_measure_tpnm(self):
        token = os.environ["TOKEN"]
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {
                    "counts": {
                        "10000": 112,
                        "10001": 25,
                        "10010": 631,
                        "10011": 111,
                        "10100": 615,
                        "10101": 132,
                        "10110": 2965,
                        "10111": 604,
                        "11000": 19,
                        "11001": 3,
                        "11010": 110,
                        "11011": 23,
                        "11100": 113,
                        "11101": 32,
                        "11110": 571,
                        "11111": 119,
                        "01000": 10,
                        "00001": 4,
                        "01101": 10,
                        "00101": 30,
                        "01011": 11,
                        "00000": 40,
                        "01110": 209,
                        "01010": 45,
                        "00010": 197,
                        "00110": 951,
                        "00100": 194,
                        "00011": 38,
                        "00111": 190,
                        "01111": 41,
                        "01100": 37,
                    },
                    "provider": "IBM",
                    "qpu": "aer_qasm_simulator",
                    "credentials": {"token": token},
                    "qubits": [0, 1, 2, 3, 4],
                    "mitigation_method": "tpnm",
                    "shots": 1000,
                    "noise_model": "ibmq_lima",
                    "only_measurement_errors": "True",
                    "max_age": 0,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("11110" in response.json.keys())
