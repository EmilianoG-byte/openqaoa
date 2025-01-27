#   Copyright 2022 Entropica Labs
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
import json
import numpy as np
from qiskit import QuantumCircuit

from openqaoa.qaoa_parameters import PauliOp, Hamiltonian, QAOACircuitParams
from openqaoa.qaoa_parameters.standardparams import QAOAVariationalStandardParams
from openqaoa.devices import DeviceQiskit
from openqaoa.backends.qpus.qaoa_qiskit_qpu import QAOAQiskitQPUBackend
from openqaoa.backends.simulators.qaoa_qiskit_sim import QAOAQiskitBackendStatevecSimulator
from openqaoa.utilities import X_mixer_hamiltonian


class TestingQAOAQiskitQPUBackend(unittest.TestCase):

    """This Object tests the QAOA Qiskit QPU Backend objects, which is tasked with the
    creation and execution of a QAOA circuit for the selected QPU provider and
    backend.

    For all of these tests, credentials.json MUST be filled with the appropriate
    credentials. If unsure about to correctness of the current input credentials
    , please run test_qpu_auth.py. 
    """

    def setUp(self):

        with open('./tests/credentials.json', 'r') as f:
            json_obj = json.load(f)['QISKIT']
            self.API_TOKEN = json_obj['API_TOKEN']
            self.HUB = json_obj['HUB']
            self.GROUP = json_obj['GROUP']
            self.PROJECT = json_obj['PROJECT']

        if self.API_TOKEN == "None":
            raise ValueError(
                "Please provide an appropriate API TOKEN in crendentials.json.")
        elif self.HUB == "None":
            raise ValueError(
                "Please provide an appropriate IBM HUB name in crendentials.json.")
        elif self.GROUP == "None":
            raise ValueError(
                "Please provide an appropriate IBMQ GROUP name in crendentials.json.")
        elif self.PROJECT == "None":
            raise ValueError(
                "Please provide an appropriate IBMQ Project name in crendentials.json.")

    def test_circuit_angle_assignment_qpu_backend(self):
        """
        A tests that checks if the circuit created by the Qiskit Backend
        has the appropriate angles assigned before the circuit is executed.
        Checks the circuit created on both IBM QPU Backends.
        """

        nqubits = 3
        p = 2
        weights = [1, 1, 1]
        gammas = [0, 1/8*np.pi]
        betas = [1/2*np.pi, 3/8*np.pi]
        shots = 10000

        cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
                                  PauliOp('ZZ', (0, 2))], weights, 1)
        mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
        circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
        variate_params = QAOAVariationalStandardParams(circuit_params,
                                                       betas, gammas)

        qiskit_device = DeviceQiskit(self.API_TOKEN, self.HUB, self.GROUP,
                                                  self.PROJECT, 'ibmq_qasm_simulator')

        qiskit_backend = QAOAQiskitQPUBackend(circuit_params, qiskit_device,
                                              shots, None,
                                              None, False)
        qpu_circuit = qiskit_backend.qaoa_circuit(variate_params)

        # Standard Decomposition
        main_circuit = QuantumCircuit(3)
        main_circuit.cx(0, 1)
        main_circuit.rz(2*gammas[0], 1)
        main_circuit.cx(0, 1)
        main_circuit.cx(1, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(1, 2)
        main_circuit.cx(0, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(0, 2)
        main_circuit.rx(-2*betas[0], 0)
        main_circuit.rx(-2*betas[0], 1)
        main_circuit.rx(-2*betas[0], 2)
        main_circuit.cx(0, 1)
        main_circuit.rz(2*gammas[1], 1)
        main_circuit.cx(0, 1)
        main_circuit.cx(1, 2)
        main_circuit.rz(2*gammas[1], 2)
        main_circuit.cx(1, 2)
        main_circuit.cx(0, 2)
        main_circuit.rz(2*gammas[1], 2)
        main_circuit.cx(0, 2)
        main_circuit.rx(-2*betas[1], 0)
        main_circuit.rx(-2*betas[1], 1)
        main_circuit.rx(-2*betas[1], 2)
        main_circuit.measure_all()

        self.assertEqual(main_circuit.to_instruction().definition,
                         qpu_circuit.to_instruction().definition)

    def test_circuit_angle_assignment_qpu_backend_w_hadamard(self):
        """
        Checks for consistent if init_hadamard is set to True.
        """

        nqubits = 3
        p = 2
        weights = [1, 1, 1]
        gammas = [0, 1/8*np.pi]
        betas = [1/2*np.pi, 3/8*np.pi]
        shots = 10000

        cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
                                  PauliOp('ZZ', (0, 2))], weights, 1)
        mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
        circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
        variate_params = QAOAVariationalStandardParams(circuit_params,
                                                       betas, gammas)

        qiskit_device = DeviceQiskit(self.API_TOKEN, self.HUB, self.GROUP,
                                                  self.PROJECT, 'ibmq_qasm_simulator')

        qiskit_backend = QAOAQiskitQPUBackend(circuit_params, qiskit_device,
                                              shots, None,
                                              None, True)
        qpu_circuit = qiskit_backend.qaoa_circuit(variate_params)

        # Standard Decomposition
        main_circuit = QuantumCircuit(3)
        main_circuit.h([0, 1, 2])
        main_circuit.cx(0, 1)
        main_circuit.rz(2*gammas[0], 1)
        main_circuit.cx(0, 1)
        main_circuit.cx(1, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(1, 2)
        main_circuit.cx(0, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(0, 2)
        main_circuit.rx(-2*betas[0], 0)
        main_circuit.rx(-2*betas[0], 1)
        main_circuit.rx(-2*betas[0], 2)
        main_circuit.cx(0, 1)
        main_circuit.rz(2*gammas[1], 1)
        main_circuit.cx(0, 1)
        main_circuit.cx(1, 2)
        main_circuit.rz(2*gammas[1], 2)
        main_circuit.cx(1, 2)
        main_circuit.cx(0, 2)
        main_circuit.rz(2*gammas[1], 2)
        main_circuit.cx(0, 2)
        main_circuit.rx(-2*betas[1], 0)
        main_circuit.rx(-2*betas[1], 1)
        main_circuit.rx(-2*betas[1], 2)
        main_circuit.measure_all()

        self.assertEqual(main_circuit.to_instruction().definition,
                         qpu_circuit.to_instruction().definition)

    def test_prepend_circuit(self):
        """
        Checks if prepended circuit has been prepended correctly.
        """

        nqubits = 3
        p = 1
        weights = [1, 1, 1]
        gammas = [1/8*np.pi]
        betas = [1/8*np.pi]
        shots = 10000

        # Prepended Circuit
        prepend_circuit = QuantumCircuit(3)
        prepend_circuit.x([0, 1, 2])

        cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
                                  PauliOp('ZZ', (0, 2))], weights, 1)
        mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
        circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
        variate_params = QAOAVariationalStandardParams(circuit_params,
                                                       betas, gammas)

        qiskit_device = DeviceQiskit(self.API_TOKEN, self.HUB, self.GROUP,
                                                  self.PROJECT, 'ibmq_qasm_simulator')

        qiskit_backend = QAOAQiskitQPUBackend(circuit_params, qiskit_device,
                                              shots, prepend_circuit,
                                              None, True)
        qpu_circuit = qiskit_backend.qaoa_circuit(variate_params)

        # Standard Decomposition
        main_circuit = QuantumCircuit(3)
        main_circuit.x([0, 1, 2])
        main_circuit.h([0, 1, 2])
        main_circuit.cx(0, 1)
        main_circuit.rz(2*gammas[0], 1)
        main_circuit.cx(0, 1)
        main_circuit.cx(1, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(1, 2)
        main_circuit.cx(0, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(0, 2)
        main_circuit.rx(-2*betas[0], 0)
        main_circuit.rx(-2*betas[0], 1)
        main_circuit.rx(-2*betas[0], 2)
        main_circuit.measure_all()

        self.assertEqual(main_circuit.to_instruction().definition,
                         qpu_circuit.to_instruction().definition)

    def test_append_circuit(self):
        """
        Checks if appended circuit is appropriately appended to the back of the
        QAOA Circuit.
        """

        nqubits = 3
        p = 1
        weights = [1, 1, 1]
        gammas = [1/8*np.pi]
        betas = [1/8*np.pi]
        shots = 10000

        # Appended Circuit
        append_circuit = QuantumCircuit(3)
        append_circuit.x([0, 1, 2])

        cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
                                  PauliOp('ZZ', (0, 2))], weights, 1)
        mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
        circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
        variate_params = QAOAVariationalStandardParams(circuit_params,
                                                       betas, gammas)

        qiskit_device = DeviceQiskit(self.API_TOKEN, self.HUB, self.GROUP,
                                                  self.PROJECT, 'ibmq_qasm_simulator')

        qiskit_backend = QAOAQiskitQPUBackend(circuit_params, qiskit_device,
                                              shots, None,
                                              append_circuit, True)
        qpu_circuit = qiskit_backend.qaoa_circuit(variate_params)

        # Standard Decomposition
        main_circuit = QuantumCircuit(3)
        main_circuit.h([0, 1, 2])
        main_circuit.cx(0, 1)
        main_circuit.rz(2*gammas[0], 1)
        main_circuit.cx(0, 1)
        main_circuit.cx(1, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(1, 2)
        main_circuit.cx(0, 2)
        main_circuit.rz(2*gammas[0], 2)
        main_circuit.cx(0, 2)
        main_circuit.rx(-2*betas[0], 0)
        main_circuit.rx(-2*betas[0], 1)
        main_circuit.rx(-2*betas[0], 2)
        main_circuit.x([0, 1, 2])
        main_circuit.measure_all()

        self.assertEqual(main_circuit.to_instruction().definition,
                         qpu_circuit.to_instruction().definition)
        
    def test_expectations_in_init(self):
        
        """
        Testing the Exceptions in the init function of the QiskitQPUShotBasedBackend
        """
        
        nqubits = 3
        p = 1
        weights = [1, 1, 1]
        gammas = [1/8*np.pi]
        betas = [1/8*np.pi]
        shots = 10000

        cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
                                  PauliOp('ZZ', (0, 2))], weights, 1)
        mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
        circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
        variate_params = QAOAVariationalStandardParams(circuit_params,
                                                       betas, gammas)

        qiskit_device = DeviceQiskit('', '', '', '', '')
        
        try:
            QAOAQiskitQPUBackend(circuit_params, qiskit_device, 
                                 shots, None, None, True)
        except Exception as e:
            self.assertEqual(str(e), 'Error connecting to IBMQ.')
        
        
        self.assertRaises(Exception, QAOAQiskitQPUBackend, (circuit_params, 
                                                            qiskit_device, 
                                                            shots, None, None, 
                                                            True))
        
        qiskit_device = DeviceQiskit(api_token=self.API_TOKEN,
                                                  hub=self.HUB, group=self.GROUP,
                                                  project=self.PROJECT, 
                                                  selected_qpu='')
        
        try:
            QAOAQiskitQPUBackend(circuit_params, qiskit_device, 
                                 shots, None, None, True)
        except Exception as e:
            self.assertEqual(str(e), 'Connection to IBMQ was made. Error connecting to the specified backend.')
        
        
        self.assertRaises(Exception, QAOAQiskitQPUBackend, (circuit_params, 
                                                            qiskit_device, 
                                                            shots, None, None, 
                                                            True))
            
    def test_remote_integration_sim_run(self):
        """
        Checks if Remote IBM QASM Simulator is similar/close to Local IBM 
        Statevector Simulator.
        This test also serves as an integration test for the IBMQPU Backend.

        This test takes a long time to complete.
        """

        nqubits = 3
        p = 1
        weights = [1, 1, 1]
        gammas = [[0], [1/8*np.pi], [0], [1/8*np.pi]]
        betas = [[0], [0], [1/8*np.pi], [1/8*np.pi]]
        shots = 10000

        for i in range(4):

            cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
                                      PauliOp('ZZ', (0, 2))], weights, 1)
            mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
            circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
            variate_params = QAOAVariationalStandardParams(circuit_params,
                                                           betas[i],
                                                           gammas[i])
            qiskit_device = DeviceQiskit(self.API_TOKEN, self.HUB, self.GROUP,
                                                      self.PROJECT, 'ibmq_qasm_simulator')

            qiskit_backend = QAOAQiskitQPUBackend(circuit_params, qiskit_device,
                                                  shots, None, None, False)
            qiskit_expectation = qiskit_backend.expectation(variate_params)

            qiskit_statevec_backend = QAOAQiskitBackendStatevecSimulator(circuit_params,
                                                                         None,
                                                                         None,
                                                                         False)
            qiskit_statevec_expectation = qiskit_statevec_backend.expectation(
                variate_params)

            acceptable_delta = 0.05*qiskit_statevec_expectation
            self.assertAlmostEqual(
                qiskit_expectation, qiskit_statevec_expectation, delta=acceptable_delta)

#     def test_remote_integration_qpu_run(self):
#         """
#         Test Actual QPU Workflow. Checks if the expectation value is returned
#         after the circuit run.
#         """

#         nqubits = 3
#         p = 1
#         weights = [1, 1, 1]
#         gammas = [[1/8*np.pi]]
#         betas = [[1/8*np.pi]]
#         shots = 10000

#         cost_hamil = Hamiltonian([PauliOp('ZZ', (0, 1)), PauliOp('ZZ', (1, 2)),
#                                   PauliOp('ZZ', (0, 2))], weights, 1)
#         mixer_hamil = X_mixer_hamiltonian(n_qubits=nqubits)
#         circuit_params = QAOACircuitParams(cost_hamil, mixer_hamil, p=p)
#         variate_params = QAOAVariationalStandardParams(circuit_params,
#                                                        betas,
#                                                        gammas)
#         qiskit_device = DeviceQiskit(self.API_TOKEN, self.HUB, self.GROUP,
#                                                   self.PROJECT, 'ibmq_bogota')

#         qiskit_backend = QAOAQiskitQPUBackend(circuit_params, qiskit_device,
#                                               shots, None, None, False)
#         qiskit_expectation = qiskit_backend.expectation(variate_params)

#         self.assertEqual(type(qiskit_expectation.item()), float)


if __name__ == '__main__':
    unittest.main()
