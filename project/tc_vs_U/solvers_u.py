# solvers_u.py
# =====================================================================
# T=0 solver and Tc bisection for the Tc-vs-U scan.
#
# Logic identical to solvers.py in the VSO code.
# Extended D0_INIT grid handles the larger gaps at large U.
# =====================================================================

import numpy as np
from scipy.optimize import fsolve

from parameters_u    import (
    MIN_GAP_FOR_SC, GAP_THRESHOLD_FRAC,
    BISECTION_TOL, BISECTION_ITER,
    D0_INIT, DS_INIT, DMU_INIT,
)
from gap_equations_u import (
    find_mu_normal, gap_residual, effective_gap
)


def find_T0_solution(n_fill, epsilon_ks, term_for_Delta0):
    """
    Grid search for the best (largest Deff) SC solution at T = 0.

    Uses a wider D0_INIT range than the VSO code because
    large U → large Delta0.
    """
    mu0      = find_mu_normal(n_fill, np.inf, epsilon_ks)
    best_sol = None
    best_gap = 0.0

    for D0i in D0_INIT:
        for DSi in DS_INIT:
            for dmu in DMU_INIT:
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
    """
    Bisection search for Tc.

    Parameters
    ----------
    n_fill          : float
    epsilon_ks      : ndarray (Nk, Nk, 2) – FIXED for the whole U scan
    term_for_Delta0 : ndarray (Nk, Nk, 2) – rebuilt for each U
    verbose         : bool

    Returns
    -------
    Tc, Deff_T0, D0_T0, DS_T0 : floats
    """
    D0_T0, DS_T0, mu_T0, Deff_T0 = find_T0_solution(
        n_fill, epsilon_ks, term_for_Delta0
    )

    if Deff_T0 < MIN_GAP_FOR_SC:
        if verbose:
            print("    → no SC at T = 0")
        return 0.0, 0.0, 0.0, 0.0

    sol_current = [D0_T0, DS_T0, mu_T0]
    threshold   = GAP_THRESHOLD_FRAC * Deff_T0

    # Walk T upward until gap closes
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

    # Bisection
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