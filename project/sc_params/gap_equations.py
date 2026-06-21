# gap_equations.py
# =====================================================================
# Self-consistency equations — matches monolithic code exactly
# =====================================================================

import numpy as np
from scipy.optimize import brentq
from parameters_tc import t, Delta_t, Nk


def find_mu_normal(n_target, beta, epsilon_ks):
    """Normal-state mu from the number equation."""
    def eq(mu):
        if np.isinf(beta):
            return np.mean(epsilon_ks < mu) - n_target
        x     = np.clip(beta * (epsilon_ks - mu), -500, 500)
        fermi = 1.0 / (1.0 + np.exp(x))
        return np.mean(fermi) - n_target

    lo = np.min(epsilon_ks) - 15.0
    hi = np.max(epsilon_ks) + 15.0
    try:
        return brentq(eq, lo, hi)
    except Exception:
        return float(np.mean(epsilon_ks))


def gap_residual(x, beta, n_fill, epsilon_ks, term_for_Delta0):
    """
    Residual of the three self-consistency equations.

    Matches the monolithic residual() exactly:
        r1 = Delta0  + (1/2N) sum[ term * Delta_ks * g_E ]
        r2 = DeltaS  + (1/2N) sum[ 8*Delta_t * Delta_ks * g_E ]
        r3 = (1/2N)  sum[ (xi/E) tanh ] - (1 - n)
    """
    Delta0, DeltaS, mu = x

    Delta_ks = Delta0 - (DeltaS / (4.0 * t)) * epsilon_ks
    xi_ks    = epsilon_ks - mu
    E_ks     = np.clip(
        np.sqrt(Delta_ks**2 + xi_ks**2), 1e-12, None
    )

    if np.isinf(beta):
        tanh_f = np.ones_like(E_ks)
    else:
        tanh_f = np.tanh(beta * E_ks / 2.0)

    g_E  = tanh_f / (2.0 * E_ks)
    Ntot = float(Nk**2)

    # ── r1: gap equation for Delta0 ───────────────────────────────────
    r1 = Delta0 + (1.0 / (2.0 * Ntot)) * np.sum(
            term_for_Delta0 * Delta_ks * g_E
         )

    # ── r2: gap equation for DeltaS ───────────────────────────────────
    # NOTE: coefficient is 8*Delta_t, NOT just 8
    # The modular version previously wrote "8 * Delta_ks * g_E"
    # which dropped Delta_t when Delta_t_over_t = 0 (invisible bug).
    # Here it must be explicit:
    r2 = DeltaS + (1.0 / (2.0 * Ntot)) * np.sum(
            8.0 * Delta_t * Delta_ks * g_E   # ← Delta_t must appear
         )

    # ── r3: number equation ───────────────────────────────────────────
    r3 = (1.0 / (2.0 * Ntot)) * np.sum(
            (xi_ks / E_ks) * tanh_f
         ) - (1.0 - n_fill)

    return [r1, r2, r3]


def effective_gap(Delta0, DeltaS, epsilon_ks):
    """
    Mean absolute k-resolved gap:
        Deff = < |Delta0 - (DeltaS/4t) * eps_ks| >_k
    """
    Delta_ks = Delta0 - (DeltaS / (4.0 * t)) * epsilon_ks
    return float(np.mean(np.abs(Delta_ks)))