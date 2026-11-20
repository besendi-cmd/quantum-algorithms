from math import pi, sin

import pytest
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator

from quantum_algorithms import algorithms as alg
from quantum_algorithms.runner import most_likely, run

SEED = 1234


def test_bell_only_correlated_outcomes():
    assert set(run(alg.bell(), seed=SEED)) == {"00", "11"}


def test_ghz_only_all_equal_outcomes():
    assert set(run(alg.ghz(4), seed=SEED)) == {"0000", "1111"}


@pytest.mark.parametrize("theta", [0.0, pi / 3, pi / 2, pi])
def test_teleportation_preserves_state(theta):
    counts = run(alg.teleportation(theta), shots=4000, seed=SEED)
    assert counts.get("1", 0) / 4000 == pytest.approx(sin(theta / 2) ** 2, abs=0.03)


def test_deutsch_jozsa_constant_and_balanced():
    assert run(alg.deutsch_jozsa(3, "constant"), seed=SEED) == {"000": 1024}
    assert "000" not in run(alg.deutsch_jozsa(3, "balanced", "101"), seed=SEED)


@pytest.mark.parametrize("secret", ["1", "1011", "000110"])
def test_bernstein_vazirani_recovers_secret(secret):
    assert run(alg.bernstein_vazirani(secret), seed=SEED) == {secret: 1024}


@pytest.mark.parametrize("marked", ["11", "101", "0110"])
def test_grover_finds_marked_item(marked):
    counts = run(alg.grover(marked), seed=SEED)
    assert most_likely(counts) == marked
    assert counts[marked] / 1024 > 0.9


def test_qft_matches_qiskit_reference():
    for n in range(1, 6):
        assert Operator(alg.qft(n)).equiv(Operator(QFTGate(n)))


@pytest.mark.parametrize("value", [0, 5, 15])
def test_qft_demo_decodes_value(value):
    assert run(alg.qft_demo(4, value), seed=SEED) == {format(value, "04b"): 1024}


@pytest.mark.parametrize("a", alg.SHOR_BASES)
def test_shor_factors_15(a):
    factors = alg.shor_factors(run(alg.shor_order_finding(a), seed=SEED), a)
    assert set(factors) <= {(3, 5)}
    if a not in (4, 11):  # order 2: half the shots give the trivial phase 0
        assert factors


def test_invalid_inputs():
    with pytest.raises(ValueError):
        alg.grover("1")
    with pytest.raises(ValueError):
        alg.shor_order_finding(5)
    with pytest.raises(ValueError):
        alg.qft_demo(3, 8)
