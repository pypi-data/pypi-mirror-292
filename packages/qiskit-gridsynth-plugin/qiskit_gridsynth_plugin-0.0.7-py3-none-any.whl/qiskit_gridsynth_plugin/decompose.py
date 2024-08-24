import subprocess
import os
import platform
from qiskit import QuantumCircuit
from qiskit.dagcircuit import DAGCircuit
from qiskit.transpiler import PassManager, TranspilerError, TransformationPass
from qiskit.transpiler.passes import BasisTranslator
from qiskit.circuit.equivalence_library import StandardEquivalenceLibrary as sel
from qiskit.converters import circuit_to_dag

def call_gridsynth(angle,epsilon):
    system = platform.system().lower()
    if system == 'linux':
        executable_name = 'gridsynth_linux'
    elif system == 'darwin':
        executable_name = 'gridsynth_mac'
    elif system == 'windows':
        executable_name = "gridsynth_windows.exe"
    else:
        raise ValueError("Unsupported OS")
    executable_path = os.path.join(os.path.dirname(__file__), "lib", executable_name)
    angle_str = "{:.18f}".format(angle)
    if angle < 0:
        angle_str = f"({angle_str})"
    result = subprocess.run([executable_path, angle_str, f'--epsilon={epsilon}', '-p'], capture_output=True)
    out, err = result.stdout.decode(), result.stderr.decode()
    return out, err

def gate_str_to_circ(gate_str : str) -> QuantumCircuit:
    circ = QuantumCircuit(1)
    for char in reversed(gate_str):
        if char == "S":
            circ.s(0)
        elif char == "H":
            circ.h(0)
        elif char == "T":
            circ.t(0)
        elif char == "X":
            circ.x(0)
        elif char == "Y":
            circ.y(0)
        elif char == "Z":
            circ.z(0)
    return circ

class GridSynth(TransformationPass):


    def __init__(
        self,
        epsilon = 1e-10
    ) -> None:
        """
        Approximately decompose 1q gates to a discrete basis using gridsynth.
        Args:
        epsilon : the permitted error of approximation
        """
        super().__init__()
        self.approx_exp = epsilon

    def run(self, dag: DAGCircuit) -> DAGCircuit:
        """Run the ``GridSynth`` pass on `dag`.

        Args:
            dag: The input dag.

        Returns:
            Output dag with 1q gates synthesized in the discrete target basis.

        Raises:
            TranspilerError: if gridsynth fails
        """
        for node in dag.op_nodes():
            if not node.name == 'rz':
                continue  # ignore all non-rz qubit gates

            angle = node.op.params[0]
            gate_str, err = call_gridsynth(angle, self.approx_exp)
            if len(err) > 0:
                raise TranspilerError(
                    f"GridSynth returned error {err}"
                )

            approximation = gate_str_to_circ(gate_str)
            approx_dag = circuit_to_dag(approximation)

            # convert to a dag and replace the gate by the approximation
            dag.substitute_node_with_dag(node, approx_dag)

        return dag

def clifford_t_transpile(circ : QuantumCircuit, epsilon : float = -10)  -> QuantumCircuit:
    '''
    Transpiles an arbitrary unitary circuit to the Clifford + T gate set. 
    Works in two phases:
    1. Unroll to the CX, H, RZ gate set using the qiskit standard equivalence library. (This transformation is exact)
    2. Decompose the RZ gates using ``gridsynth`` (This transformation is approximate, with error up to epsilon)
    '''
    pm = PassManager([BasisTranslator(equivalence_library=sel, target_basis=["cx", "h", 'rz']), GridSynth(epsilon)])
    return pm.run(circ)
