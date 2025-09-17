from qiskit_algorithms import Shor
from qiskit.utils import QuantumInstance
from qiskit import Aer





N = 15
backend = Aer.get_backend('aer_simulator')
qi = QuantumInstance(backend)

shor = Shor()
result = shor.factor(N, quantum_instance=qi)

print("Factoring result:", result)
