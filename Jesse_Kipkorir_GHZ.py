from zuntenium import QuantumCircuit
from zuntenium.quantum_core.statevector.statevector_simulator import StatevectorSimulator


def apply_circuit(simulator, circuit):
    for instruction in circuit.instructions:
        simulator.apply_gate(instruction.gate.matrix(), instruction.qubits)


def apply_inverse(simulator, circuit):
    inverse_method = getattr(circuit, "inverse", None)
    if callable(inverse_method):
        inverse_circuit = inverse_method()
        apply_circuit(simulator, inverse_circuit)
        return "qc.inverse()"

    for instruction in reversed(circuit.instructions):
        simulator.apply_gate(
            instruction.gate.matrix().conj().T,
            instruction.qubits,
        )
    return "manual reverse (qc.inverse unavailable)"


print("GHZ experiments with Zuntenium")
print("Qubits | all-zero | all-one | other | uncompute | inverse method")

for n in (2, 3, 4):
    qc = QuantumCircuit(n)
    qc.h(0)
    for target in range(1, n):
        qc.cx(0, target)

    shot_simulator = StatevectorSimulator(n, seed=7)
    apply_circuit(shot_simulator, qc)
    counts = shot_simulator.sample(8192)

    zeros = "0" * n
    ones = "1" * n
    other = sum(count for bits, count in counts.items()
                if bits not in (zeros, ones))

    inverse_simulator = StatevectorSimulator(n, seed=7)
    apply_circuit(inverse_simulator, qc)
    inverse_method_used = apply_inverse(inverse_simulator, qc)
    after_uncompute = inverse_simulator.sample(32)
    uncompute_ok = after_uncompute == {zeros: 32}

    print(
        f"{n:>6} | {counts.get(zeros, 0):>8} | "
        f"{counts.get(ones, 0):>7} | {other:>5} | "
        f"{str(uncompute_ok):>9} | {inverse_method_used}"
    )
