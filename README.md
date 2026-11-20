# Quantum Algorithms with Qiskit

Classic quantum algorithms implemented with [Qiskit](https://qiskit.org) and run on the local Aer simulator.

| Command | Algorithm | What it shows |
|---|---|---|
| `bell` | Bell state | Two entangled qubits: only `00` / `11` |
| `ghz --n 3` | GHZ state | n-qubit entanglement |
| `teleport --theta 1.0` | Quantum teleportation | Moves a qubit state using entanglement |
| `dj --oracle balanced` | Deutsch–Jozsa | Constant vs balanced in one query |
| `bv --secret 1011` | Bernstein–Vazirani | Recovers a hidden bitstring in one query |
| `grover --marked 101` | Grover's search | Finds a marked item in ~√N steps |
| `qft --n 4 --value 5` | Quantum Fourier transform | Encodes a number as phases and decodes it |
| `shor --a 7` | Shor's algorithm | Factors 15 = 3 × 5 via order finding |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python -m quantum_algorithms all                 # run every demo
python -m quantum_algorithms --draw grover       # show the circuit too
python -m quantum_algorithms --shots 4096 --seed 1 shor --a 13
```

## Tests

```bash
pytest
```

## Layout

- `quantum_algorithms/algorithms.py`: circuit builders and Shor's classical post-processing
- `quantum_algorithms/runner.py`: simulator wrapper and text histogram
- `quantum_algorithms/cli.py`: command-line interface
- `tests/`: checks each algorithm gives the correct answer
