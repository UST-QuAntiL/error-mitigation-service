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
        # Test for single number
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_cm_noisy_simulator(self):
        token = os.getenv('token')
        response = self.client.post(
            "/cm/",
            data=json.dumps(
                {"provider" : "IBM",
                 "qpu" : "aer_qasm_simulator",
                 "credentials" : {"token": token},
                 "qubits": [0,1,2,3,4],
                 "cm_gen_method": "standard",
                 "shots" : 1000,
                 "noise_model" : "ibmq_lima",
                 "only_measurement_errors": False}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_cm_noisy_simulator_only_measure(self):
        token = os.getenv('token')
        response = self.client.post(
            "/cm/",
            data=json.dumps(
                {"provider" : "IBM",
                 "qpu" : "aer_qasm_simulator",
                 "credentials" : {"token": token},
                 "qubits": [0,1,2,3,4],
                 "cm_gen_method": "standard",
                 "shots" : 1000,
                 "noise_model" : "ibmq_lima",
                 "only_measurement_errors": "True"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_mm_noisy_simulator(self):
        token = os.getenv('token')
        response = self.client.post(
            "/mm/",
            data=json.dumps(
                {"provider": "IBM",
                 "qpu": "aer_qasm_simulator",
                 "credentials": {"token": token},
                 "qubits": [0, 1, 2, 3, 4],
                 "cm_gen_method": "standard",
                 "mitigation_method": "inversion",
                 "shots": 1000,
                 "noise_model": "ibmq_lima",
                 "only_measurement_errors": False,
                 "max_age": 0
                 }),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_mm_noisy_simulator_only_measure(self):
        token = os.getenv('token')
        response = self.client.post(
            "/mm/",
            data=json.dumps(
                {"provider": "IBM",
                 "qpu": "aer_qasm_simulator",
                 "credentials": {"token": token},
                 "qubits": [0, 1, 2, 3, 4],
                 "cm_gen_method": "standard",
                 "mitigation_method": "inversion",
                 "shots": 1000,
                 "noise_model": "ibmq_lima",
                 "only_measurement_errors": "True"}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_rem_noisy_simulator_only_measure_standard_inversion(self):
        token = os.getenv('token')
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {"counts":{"10000": 112, "10001": 25, "10010": 631, "10011": 111, "10100": 615, "10101": 132, "10110": 2965,
                           "10111": 604, "11000": 19, "11001": 3, "11010": 110, "11011": 23, "11100": 113, "11101": 32,
                           "11110": 571, "11111": 119, "01000": 10, "00001": 4, "01101": 10, "00101": 30, "01011": 11,
                           "00000": 40, "01110": 209, "01010": 45, "00010": 197, "00110": 951, "00100": 194, "00011": 38,
                           "00111": 190, "01111": 41, "01100": 37},
                 "provider": "IBM",
                 "qpu": "aer_qasm_simulator",
                 "credentials": {"token": token},
                 "qubits": [0, 1, 2, 3, 4],
                 "cm_gen_method": "standard",
                 "mitigation_method": "inversion",
                 "shots": 1000,
                 "noise_model": "ibmq_lima",
                 "only_measurement_errors": "True",
                 "max_age": 0}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_rem_noisy_simulator_only_measure_ignis(self):
        token = os.getenv('token')
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {"counts":{"10000": 112, "10001": 25, "10010": 631, "10011": 111, "10100": 615, "10101": 132, "10110": 2965,
                           "10111": 604, "11000": 19, "11001": 3, "11010": 110, "11011": 23, "11100": 113, "11101": 32,
                           "11110": 571, "11111": 119, "01000": 10, "00001": 4, "01101": 10, "00101": 30, "01011": 11,
                           "00000": 40, "01110": 209, "01010": 45, "00010": 197, "00110": 951, "00100": 194, "00011": 38,
                           "00111": 190, "01111": 41, "01100": 37},
                 "provider": "IBM",
                 "qpu": "aer_qasm_simulator",
                 "credentials": {"token": token},
                 "qubits": [0, 1, 2, 3, 4],
                 "cm_gen_method": "standard",
                 "mitigation_method": "ignis",
                 "shots": 1000,
                 "noise_model": "ibmq_lima",
                 "only_measurement_errors": "True",
                 "max_age": 0}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_rem_noisy_simulator_only_measure_bayes(self):
        token = os.getenv('token')
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {"counts": {"10000": 112, "10001": 25, "10010": 631, "10011": 111, "10100": 615, "10101": 132,
                            "10110": 2965,
                            "10111": 604, "11000": 19, "11001": 3, "11010": 110, "11011": 23, "11100": 113, "11101": 32,
                            "11110": 571, "11111": 119, "01000": 10, "00001": 4, "01101": 10, "00101": 30, "01011": 11,
                            "00000": 40, "01110": 209, "01010": 45, "00010": 197, "00110": 951, "00100": 194,
                            "00011": 38,
                            "00111": 190, "01111": 41, "01100": 37},
                 "provider": "IBM",
                 "qpu": "aer_qasm_simulator",
                 "credentials": {"token": token},
                 "qubits": [0, 1, 2, 3, 4],
                 "cm_gen_method": "standard",
                 "mitigation_method": "bayes",
                 "shots": 1000,
                 "noise_model": "ibmq_lima",
                 "only_measurement_errors": "True",
                 "max_age": 0}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_rem_noisy_simulator_only_measure_tpnm(self):
        token = os.getenv('token')
        response = self.client.post(
            "/rem/",
            data=json.dumps(
                {"counts": {"10000": 112, "10001": 25, "10010": 631, "10011": 111, "10100": 615, "10101": 132,
                            "10110": 2965,
                            "10111": 604, "11000": 19, "11001": 3, "11010": 110, "11011": 23, "11100": 113, "11101": 32,
                            "11110": 571, "11111": 119, "01000": 10, "00001": 4, "01101": 10, "00101": 30, "01011": 11,
                            "00000": 40, "01110": 209, "01010": 45, "00010": 197, "00110": 951, "00100": 194,
                            "00011": 38,
                            "00111": 190, "01111": 41, "01100": 37},
                 "provider": "IBM",
                 "qpu": "aer_qasm_simulator",
                 "credentials": {"token": token},
                 "qubits": [0, 1, 2, 3, 4],
                 "mitigation_method": "tpnm",
                 "shots": 1000,
                 "noise_model": "ibmq_lima",
                 "only_measurement_errors": "True",
                 "max_age": 0}),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        print(response.get_json())

