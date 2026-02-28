#!/usr/bin/env python3
"""
CALIUSO_v8.8.1_CANON.py
Canonical runtime for the Z9 Inner Seal theorem.

Push button, prove it is real:
  - Exhausts all (s,g) pairs in Z9 x {+1,-1,+3,-3}
  - Builds the wound-collapse TPM
  - Solves for stationary distribution
  - Computes spectral gap
  - Prints Inner Seal (SHA-256)
  - Runs 10 self-tests

Expected Inner Seal: f7f7aaa0a857b799f97dfc3c2cb7dd1a056ab4ad5bb7c1927d14b1a8c49e5bf4

CALIUSO_v8.8.1 · Z9 · {0,3,6} · 2026-02-27 · 🕯️ ∎
"""

import hashlib
import math
import numpy as np

Z9         = list(range(9))
GENERATORS = [1, -1, 3, -3]
ATTRACTOR  = frozenset([0, 3, 6])
EXPECTED_SEAL = "f7f7aaa0a857b799f97dfc3c2cb7dd1a056ab4ad5bb7c1927d14b1a8c49e5bf4"


def circular_dist(a, b, n=9):
    d = abs(a - b) % n
    return min(d, n - d)


def nearest_attractor(s):
    return min(ATTRACTOR, key=lambda a: circular_dist(s, a))


def build_tpm():
    """
    Policy (K=2 wound-collapse):
    Generator +-1 (drift): always move to (s+g) mod 9
    Generator +-3 (wound): move to (s+g)%9 if that is in ATTRACTOR,
                           else collapse to nearest_attractor(s)
    Each generator selected with prob 1/4.
    """
    T = np.zeros((9, 9), dtype=float)
    for s in Z9:
        for g in GENERATORS:
            sp = (s + g) % 9
            if abs(g) == 3 and sp not in ATTRACTOR:
                sp = nearest_attractor(s)
            T[s][sp] += 0.25
    return T


def stationary(T):
    vals, vecs = np.linalg.eig(T.T)
    pi = np.real(vecs[:, np.argmax(np.real(vals))])
    return pi / pi.sum()


def spectral_gap(T):
    return 1.0 - sorted(np.abs(np.linalg.eigvals(T)), reverse=True)[1]


def inner_seal_hash(T, pi):
    rows = [",".join(f"{v:.10f}" for v in row) for row in T]
    blob = "Z9:CALIUSO_v8.8.1\n" + "\n".join(rows) + "\nPI:" + ",".join(f"{v:.10f}" for v in pi)
    return hashlib.sha256(blob.encode()).hexdigest()


def run_tests(T, pi, gap, seal):
    passed = 0
    results = []

    def test(name, cond):
        nonlocal passed
        passed += cond
        results.append(("PASS" if cond else "FAIL", name))

    test("T01: TPM rows sum to 1",
         all(abs(T[s].sum() - 1.0) < 1e-10 for s in Z9))

    test("T02: {0,3,6} closed under +3 mod 9",
         all((a + 3) % 9 in ATTRACTOR for a in ATTRACTOR))

    test("T03: Attractor stable under +-3 generators",
         all((a + g) % 9 in ATTRACTOR for a in ATTRACTOR for g in [3, -3]))

    non_att = [s for s in Z9 if s not in ATTRACTOR]
    test("T04: Non-attractor +-3 wound targets are in ATTRACTOR",
         all(nearest_attractor(s) in ATTRACTOR for s in non_att))

    att_mass = sum(pi[a] for a in ATTRACTOR)
    test(f"T05: Attractor stationary mass = {att_mass:.4f} > 0.5",
         att_mass > 0.5)

    test(f"T06: Spectral gap = {gap:.6f} > 0 (ergodic)",
         gap > 0)

    test("T07: Stationary distribution sums to 1",
         abs(pi.sum() - 1.0) < 1e-10)

    test("T08: pi @ T = pi (stationarity verified)",
         np.allclose(pi @ T, pi, atol=1e-8))

    test("T09: |ATTRACTOR| = 3 = 9/3 (order-3 subgroup)",
         len(ATTRACTOR) == 3)

    test("T10: Inner Seal hash matches expected",
         seal == EXPECTED_SEAL)

    for status, name in results:
        print(f"  [{status}] {name}")

    print(f"\n  {passed}/{len(results)} tests passed.")
    return passed == len(results)


def main():
    SEP = "=" * 62
    print(SEP)
    print("CALIUSO_v8.8.1_CANON.py — Z9 Inner Seal Runtime")
    print(SEP)

    print("\n[1] Building TPM (wound-collapse policy)...")
    T = build_tpm()

    print("[2] Solving stationary distribution...")
    pi = stationary(T)
    att_mass = sum(pi[a] for a in sorted(ATTRACTOR))
    print(f"    pi = {[round(float(pi[s]),4) for s in Z9]}")
    print(f"    Attractor mass: {att_mass:.6f}")

    print("[3] Computing spectral gap...")
    gap = spectral_gap(T)
    print(f"    Spectral gap: {gap:.6f}")

    print("[4] Computing Inner Seal (SHA-256)...")
    seal = inner_seal_hash(T, pi)
    print(f"    INNER SEAL: {seal}")

    print("\n[5] Self-tests (10 invariants):")
    all_pass = run_tests(T, pi, gap, seal)

    print("\n" + SEP)
    print("INVARIANTS:")
    print(f"  |Z9| = 9   Attractor = {{0,3,6}}   Generators = {{+1,-1,+3,-3}}")
    print(f"  Spectral gap     = {gap:.6f}")
    print(f"  Attractor mass   = {att_mass:.6f}")
    print(f"  INNER SEAL       = {seal}")
    print(SEP)
    status = "ALL INVARIANTS HOLD — CANON VERIFIED" if all_pass else "INVARIANT VIOLATION"
    print(f"\nSTATUS: {status}")
    print("\nCALIUSO_v8.8.1 · Z9 · {0,3,6} · 2026-02-27 · 🕯️ ∎")


if __name__ == "__main__":
    main()
