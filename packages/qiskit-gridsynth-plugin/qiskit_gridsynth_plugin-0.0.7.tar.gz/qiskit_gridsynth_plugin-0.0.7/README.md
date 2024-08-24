# Qiskit GridSynth plugin

This package integrates angle decomposition with ``gridsynth`` [1] into the ``qiskit`` [2]
software stack, facilitating efficient transpilation to the Clifford+T gate set.

## Installation 
Install via pip:
```
pip install qiskit-gridsynth-plugin
```

## Example Usage
Read a circuit from a qasm file `circ.qasm`, transpile to Clifford+T, and write the result to ``out.qasm``
```
from qiskit import qasm2, QuantumCircuit
from qiskit_gridsynth_plugin.decompose import clifford_t_transpile
circ = QuantumCircuit.from_qasm_file('circ.qasm')
decomposed = clifford_t_transpile(circ, epsilon=1e-4)
qiskit.qasm2.dump(decomposed, "out.qasm")
```
Include ``gridsynth`` angle decomposition as part of a qiskit compilation pipeline that also cancels out back-to-back CNOT gates

```
from qiskit.circuit.library.standard_gates import CXGate
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import InverseCancellation
from qiskit_gridsynth_plugin.decompose import GridSynth
circ = QuantumCircuit.from_qasm_file('circ.qasm')
pm = PassManager(InverseCancellation([CXGate()]), GridSynth(1e-4))
decomposed = pm.run(circ)
```


## References
[1] N. J. Ross and P. Selinger, "Optimal ancilla-free Clifford+T approximation of z-rotations", arXiv:1403.2975 \
[2] https://www.ibm.com/quantum/qiskit