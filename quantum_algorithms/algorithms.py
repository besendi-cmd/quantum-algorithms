from fractions import Fraction
from math import floor, gcd, pi, sqrt

from qiskit import QuantumCircuit


def bell() -> QuantumCircuit:
    """Entangle two qubits into (|00> + |11>)/sqrt(2)."""
    qc = QuantumCircuit(2, 2, name="bell")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def ghz(n: int = 3) -> QuantumCircuit:
    """n-qubit GHZ state (|0...0> + |1...1>)/sqrt(2)."""
    if n < 2:
        raise ValueError("GHZ needs at least 2 qubits")
    qc = QuantumCircuit(n, n, name="ghz")
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.measure(range(n), range(n))
    return qc


def teleportation(theta: float = pi / 3) -> QuantumCircuit:
    """Teleport RY(theta)|0> from qubit 0 to qubit 2.

    Uses the deferred-measurement form: Bob's classically-controlled X/Z corrections become CX/CZ gates.
    Measuring qubit 2 gives '1' with probability sin^2(theta/2).
    """
    qc = QuantumCircuit(3, 1, name="teleportation")
    qc.ry(theta, 0)
    qc.barrier()
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.cx(1, 2)
    qc.cz(0, 2)
    qc.measure(2, 0)
    return qc


def _oracle_bits(bitstring: str) -> list[int]:
    """Qubit indices whose bit is '1', given a big-endian bitstring (matches Qiskit's printed counts)."""
    return [i for i, b in enumerate(reversed(bitstring)) if b == "1"]


def deutsch_jozsa(n: int = 3, oracle: str = "balanced", secret: str | None = None) -> QuantumCircuit:
    """Decide in one query whether f: {0,1}^n -> {0,1} is constant or balanced.

    Constant f gives all zeros; balanced f (here f(x) = s.x mod 2, s != 0) gives anything else.
    """
    if oracle not in ("constant", "balanced"):
        raise ValueError("oracle must be 'constant' or 'balanced'")
    secret = secret or "1" * n
    if oracle == "balanced" and (len(secret) != n or "1" not in secret):
        raise ValueError("balanced oracle needs a non-zero secret of length n")
    qc = QuantumCircuit(n + 1, n, name="deutsch_jozsa")
    qc.x(n)
    qc.h(range(n + 1))
    qc.barrier()
    if oracle == "constant":
        qc.x(n)
    else:
        for q in _oracle_bits(secret):
            qc.cx(q, n)
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def bernstein_vazirani(secret: str = "1011") -> QuantumCircuit:
    """Recover a hidden bitstring s from f(x) = s.x mod 2 with a single query."""
    if not secret or set(secret) - {"0", "1"}:
        raise ValueError("secret must be a non-empty bitstring")
    n = len(secret)
    qc = QuantumCircuit(n + 1, n, name="bernstein_vazirani")
    qc.x(n)
    qc.h(range(n + 1))
    qc.barrier()
    for q in _oracle_bits(secret):
        qc.cx(q, n)
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def _mcz(qc: QuantumCircuit, n: int) -> None:
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)


def grover(marked: str = "101", iterations: int | None = None) -> QuantumCircuit:
    """Search 2^n items for the marked bitstring in ~(pi/4)sqrt(2^n) oracle calls."""
    if len(marked) < 2 or set(marked) - {"0", "1"}:
        raise ValueError("marked must be a bitstring of length >= 2")
    n = len(marked)
    iterations = iterations if iterations is not None else floor(pi / 4 * sqrt(2**n))
    zeros = [i for i, b in enumerate(reversed(marked)) if b == "0"]

    qc = QuantumCircuit(n, n, name="grover")
    qc.h(range(n))
    for _ in range(iterations):
        qc.barrier()
        if zeros:
            qc.x(zeros)
        _mcz(qc, n)
        if zeros:
            qc.x(zeros)
        qc.barrier()
        qc.h(range(n))
        qc.x(range(n))
        _mcz(qc, n)
        qc.x(range(n))
        qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def qft(n: int) -> QuantumCircuit:
    """Quantum Fourier transform on n qubits: |x> -> 1/sqrt(N) sum_k e^{2 pi i x k / N} |k>."""
    qc = QuantumCircuit(n, name="QFT")
    for j in reversed(range(n)):
        qc.h(j)
        for k in reversed(range(j)):
            qc.cp(pi / 2 ** (j - k), k, j)
    for i in range(n // 2):
        qc.swap(i, n - i - 1)
    return qc


def qft_demo(n: int = 4, value: int = 5) -> QuantumCircuit:
    """Write `value` into the Fourier basis with phase gates, then decode it with the inverse QFT."""
    if not 0 <= value < 2**n:
        raise ValueError(f"value must be in [0, {2**n - 1}]")
    qc = QuantumCircuit(n, n, name="qft_demo")
    qc.h(range(n))
    for j in range(n):
        qc.p(2 * pi * value * 2**j / 2**n, j)
    qc.barrier()
    qc.compose(qft(n).inverse(), inplace=True)
    qc.measure(range(n), range(n))
    return qc


SHOR_BASES = (2, 4, 7, 8, 11, 13)


def _c_amod15(a: int, power: int):
    """Controlled multiplication by a^power mod 15 on a 4-qubit work register."""
    u = QuantumCircuit(4, name=f"{a}^{power} mod 15")
    for _ in range(power % 4):  # a^4 = 1 (mod 15) for every valid base
        if a in (2, 13):
            u.swap(2, 3)
            u.swap(1, 2)
            u.swap(0, 1)
        if a in (7, 8):
            u.swap(0, 1)
            u.swap(1, 2)
            u.swap(2, 3)
        if a in (4, 11):
            u.swap(1, 3)
            u.swap(0, 2)
        if a in (7, 11, 13):
            u.x(range(4))
    return u.to_gate().control()


def shor_order_finding(a: int = 7, n_count: int = 8) -> QuantumCircuit:
    """Quantum phase estimation of U|y> = |a*y mod 15>; the measured phase is s/r for the order r of a."""
    if a not in SHOR_BASES:
        raise ValueError(f"a must be one of {SHOR_BASES}")
    qc = QuantumCircuit(n_count + 4, n_count, name="shor_order_finding")
    qc.h(range(n_count))
    qc.x(n_count)  # work register starts in |1>
    for q in range(n_count):
        qc.append(_c_amod15(a, 2**q), [q] + list(range(n_count, n_count + 4)))
    qc.compose(qft(n_count).inverse(), qubits=range(n_count), inplace=True)
    qc.measure(range(n_count), range(n_count))
    return qc


def shor_factors(counts: dict[str, int], a: int, N: int = 15) -> dict[tuple[int, int], int]:
    """Classical post-processing: turn measured phases into orders, and orders into non-trivial factors."""
    found: dict[tuple[int, int], int] = {}
    for bits, n in counts.items():
        phase = int(bits, 2) / 2 ** len(bits)
        r = Fraction(phase).limit_denominator(N).denominator
        if r % 2 or pow(a, r, N) != 1 or pow(a, r // 2, N) == N - 1:
            continue
        p = gcd(pow(a, r // 2) - 1, N)
        q = gcd(pow(a, r // 2) + 1, N)
        for f in (p, q):
            if 1 < f < N:
                pair = tuple(sorted((f, N // f)))
                found[pair] = found.get(pair, 0) + n
                break
    return found
