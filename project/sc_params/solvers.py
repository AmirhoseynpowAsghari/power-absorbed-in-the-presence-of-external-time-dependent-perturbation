# solvers.py
# =====================================================================
# T=0 solver and Tc bisection — unchanged logic, fixed imports
# =====================================================================

import numpy as np
from scipy.optimize import fsolve

from parameters_tc import (
    t,
    MIN_GAP_FOR_SC,
    GAP_THRESHOLD_FRAC,
    BISECTION_TOL,
    BISECTION_ITER,
)
from gap_equations import find_mu_normal, gap_residual, effective_gap


def find_T0_solution(n_fill, epsilon_ks, term_for_Delta0):
    """
    Grid search for best SC solution at T=0.
    Identical initial-guess grids as the monolithic code.
    """
    mu0      = find_mu_normal(n_fill, np.inf, epsilon_ks)
    best_sol = None
    best_gap = 0.0

    D0_tries  = [0.1, 0.5, 1.0, 2.0, 5.0]
    DS_tries  = [0.1, 0.5, 1.0, 5.0, 10.0]
    dmu_tries = [-2.0, -0.5, 0.0, 0.5, 2.0]

    for D0i in D0_tries:
        for DSi in DS_tries:
            for dmu in dmu_tries:
                try:
                    sol, _, ier, _ = fsolve(
                        gap_residual,
                        [D0i, DSi, mu0 + dmu],
                        args=(np.inf, n_fill, epsilon_ks, term_for_Delta0),
                        full_output=True,
                    )
                    if ier == 1:
                        D0c  = abs(sol[0])
                        DSc  = abs(sol[1])
                        muc  = sol[2]
                        Deff = effective_gap(D0c, DSc, epsilon_ks)
                        if Deff > best_gap:
                            best_gap = Deff
                            best_sol = (D0c, DSc, muc)
                except Exception:
                    pass

    if best_sol is None or best_gap < MIN_GAP_FOR_SC:
        return 0.0, 0.0, mu0, 0.0

    D0, DS, mu = best_sol
    return D0, DS, mu, effective_gap(D0, DS, epsilon_ks)


def _gap_at_T(T, start_guess, n_fill, epsilon_ks, term_for_Delta0):
    """Solve gap equations at temperature T with warm start."""
    try:
        s    = fsolve(
            gap_residual, start_guess,
            args=(1.0 / T, n_fill, epsilon_ks, term_for_Delta0),
        )
        D0   = abs(s[0])
        DS   = abs(s[1])
        Deff = effective_gap(D0, DS, epsilon_ks)
        return Deff, [D0, DS, s[2]]
    except Exception:
        return 0.0, start_guess


def find_Tc(n_fill, epsilon_ks, term_for_Delta0, verbose=False):
    """Bisection Tc search — logic identical to monolithic find_Tc."""

    D0_T0, DS_T0, mu_T0, Deff_T0 = find_T0_solution(
        n_fill, epsilon_ks, term_for_Delta0
    )

    if Deff_T0 < MIN_GAP_FOR_SC:
        if verbose:
            print("    → no SC at T=0")
        return 0.0, 0.0, 0.0, 0.0

    sol_current = [D0_T0, DS_T0, mu_T0]
    threshold   = GAP_THRESHOLD_FRAC * Deff_T0

    # ── Walk T upward until gap closes ───────────────────────────────
    T_max = 0.57 * Deff_T0 * 3.0
    Deff, sol_current = _gap_at_T(
        T_max, sol_current, n_fill, epsilon_ks, term_for_Delta0
    )
    for _ in range(10):
        if Deff <= threshold:
            break
        T_max *= 1.5
        Deff, sol_current = _gap_at_T(
            T_max, sol_current, n_fill, epsilon_ks, term_for_Delta0
        )

    # ── Bisection ─────────────────────────────────────────────────────
    T_low       = 0.0
    T_high      = T_max
    sol_current = [D0_T0, DS_T0, mu_T0]   # restart from T=0

    for _ in range(BISECTION_ITER):
        T_mid         = (T_low + T_high) / 2.0
        Deff, sol_out = _gap_at_T(
            T_mid, sol_current, n_fill, epsilon_ks, term_for_Delta0
        )
        if Deff > threshold:
            T_low       = T_mid
            sol_current = sol_out
        else:
            T_high      = T_mid
        if (T_high - T_low) < BISECTION_TOL:
            break

    Tc = (T_low + T_high) / 2.0

    if verbose:
        if Tc > 0:
            print(f"    Deff(0) = {Deff_T0:.5f}   "
                  f"Tc = {Tc:.6f}   "
                  f"2D/kTc = {2*Deff_T0/Tc:.3f}")
        else:
            print(f"    Deff(0) = {Deff_T0:.5f}   Tc = 0")

    return Tc, Deff_T0, D0_T0, DS_T0