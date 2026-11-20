import argparse
from math import pi, sin

from . import algorithms as alg
from .runner import histogram, most_likely, run


def _show(title, qc, args, explain):
    print(f"\n=== {title} ===")
    if args.draw:
        print(qc.draw(output="text", fold=120))
    counts = run(qc, shots=args.shots, seed=args.seed)
    print(histogram(counts))
    print(explain(counts))
    return counts


def cmd_bell(args):
    _show("Bell state", alg.bell(), args, lambda c: "Only 00 and 11 appear: the two qubits are entangled.")


def cmd_ghz(args):
    _show(f"GHZ state ({args.n} qubits)", alg.ghz(args.n), args,
          lambda c: f"Only all-0 and all-1 appear across {args.n} entangled qubits.")


def cmd_teleport(args):
    expected = sin(args.theta / 2) ** 2

    def explain(c):
        got = c.get("1", 0) / sum(c.values())
        return f"P(1) on Bob's qubit: measured {got:.3f}, expected sin^2(theta/2) = {expected:.3f}."

    _show(f"Teleportation (theta={args.theta:.3f})", alg.teleportation(args.theta), args, explain)


def cmd_dj(args):
    qc = alg.deutsch_jozsa(args.n, args.oracle)

    def explain(c):
        verdict = "constant" if most_likely(c) == "0" * args.n else "balanced"
        return f"Oracle was {args.oracle}; one query says: {verdict}."

    _show("Deutsch-Jozsa", qc, args, explain)


def cmd_bv(args):
    _show("Bernstein-Vazirani", alg.bernstein_vazirani(args.secret), args,
          lambda c: f"Hidden string {args.secret}; recovered {most_likely(c)} in one query.")


def cmd_grover(args):
    _show(f"Grover search over {2 ** len(args.marked)} items", alg.grover(args.marked), args,
          lambda c: f"Marked item {args.marked}; most likely result {most_likely(c)}.")


def cmd_qft(args):
    _show("Quantum Fourier transform", alg.qft_demo(args.n, args.value), args,
          lambda c: f"Encoded {args.value} as phases; inverse QFT read back {int(most_likely(c), 2)}.")


def cmd_shor(args):
    def explain(c):
        factors = alg.shor_factors(c, args.a)
        if not factors:
            return "No factors found this run; try again or another base."
        best = max(factors, key=factors.get)
        share = factors[best] / sum(c.values())
        return f"Factored 15 = {best[0]} x {best[1]} (from {share:.0%} of shots, base a={args.a})."

    _show("Shor's algorithm (N=15)", alg.shor_order_finding(args.a), args, explain)


def cmd_all(args):
    for fn in (cmd_bell, cmd_ghz, cmd_teleport, cmd_dj, cmd_bv, cmd_grover, cmd_qft, cmd_shor):
        fn(args)


def build_parser():
    p = argparse.ArgumentParser(prog="quantum", description="Run classic quantum algorithms on a simulator.")
    p.add_argument("--shots", type=int, default=1024)
    p.add_argument("--seed", type=int, default=None, help="simulator seed for reproducible results")
    p.add_argument("--draw", action="store_true", help="print the circuit diagram")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("bell", help="Bell state").set_defaults(func=cmd_bell)
    s = sub.add_parser("ghz", help="GHZ state")
    s.add_argument("--n", type=int, default=3)
    s.set_defaults(func=cmd_ghz)
    s = sub.add_parser("teleport", help="quantum teleportation")
    s.add_argument("--theta", type=float, default=pi / 3)
    s.set_defaults(func=cmd_teleport)
    s = sub.add_parser("dj", help="Deutsch-Jozsa")
    s.add_argument("--n", type=int, default=3)
    s.add_argument("--oracle", choices=["constant", "balanced"], default="balanced")
    s.set_defaults(func=cmd_dj)
    s = sub.add_parser("bv", help="Bernstein-Vazirani")
    s.add_argument("--secret", default="1011")
    s.set_defaults(func=cmd_bv)
    s = sub.add_parser("grover", help="Grover's search")
    s.add_argument("--marked", default="101")
    s.set_defaults(func=cmd_grover)
    s = sub.add_parser("qft", help="quantum Fourier transform")
    s.add_argument("--n", type=int, default=4)
    s.add_argument("--value", type=int, default=5)
    s.set_defaults(func=cmd_qft)
    s = sub.add_parser("shor", help="Shor's algorithm factoring 15")
    s.add_argument("--a", type=int, default=7, choices=alg.SHOR_BASES)
    s.set_defaults(func=cmd_shor)
    s = sub.add_parser("all", help="run every demo with default settings")
    s.set_defaults(func=cmd_all, n=3, theta=pi / 3, oracle="balanced", secret="1011", marked="101", value=5, a=7)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
