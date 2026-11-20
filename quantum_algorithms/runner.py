from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def run(circuit: QuantumCircuit, shots: int = 1024, seed: int | None = None) -> dict[str, int]:
    """Simulate a circuit and return measurement counts (bitstrings are little-endian, qubit 0 rightmost)."""
    simulator = AerSimulator(seed_simulator=seed)
    compiled = transpile(circuit, simulator, seed_transpiler=seed)
    return simulator.run(compiled, shots=shots).result().get_counts()


def most_likely(counts: dict[str, int]) -> str:
    return max(counts, key=counts.get)


def histogram(counts: dict[str, int], width: int = 40) -> str:
    total = sum(counts.values())
    lines = []
    for bits, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        bar = "#" * max(1, round(width * n / total))
        lines.append(f"  {bits}  {bar} {n} ({n / total:.1%})")
    return "\n".join(lines)
