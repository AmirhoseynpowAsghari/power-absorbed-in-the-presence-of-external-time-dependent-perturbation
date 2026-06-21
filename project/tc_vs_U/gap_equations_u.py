# gap_equations_u.py
# =====================================================================
# Self-consistency equations for the Tc-vs-U scan.
#
# The residual is IDENTICAL to the VSO-code's gap_equations.py.
# We keep a separate copy so each sub-project is self-contained,
# but the logic is bit-for-bit the same.
# =====================================================================

import numpy as np
from scipy.optimize import brentq
from parameters_u import t, Delta_t, Nk


def find_mu_normal(n_target, beta, epsilon_ks):
    """
    Normal-state mu from the number equation (Delta = 0).

    Parameters
    ----------
    n_target   : float
    beta       : float  (np.inf → T = 0)
    epsilon_ks : ndarray (Nk, Nk, 2)

    Returns
    -------
    float – chemical potential
    """
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
    Three-component residual for the coupled gap + number equations.

    Unknowns  x = [Delta0, DeltaS, mu]

        Delta_ks = Delta0 - (DeltaS / 4t) * eps_ks
        E_ks     = sqrt(Delta_ks^2 + (eps_ks - mu)^2)

        r1 : Delta0  gap equation
        r2 : DeltaS  gap equation
        r3 : number  equation

    Parameters
    ----------
    x               : (Delta0, DeltaS, mu)
    beta            : float
    n_fill          : float
    epsilon_ks      : ndarray (Nk, Nk, 2)
    term_for_Delta0 : ndarray (Nk, Nk, 2)  ← changes with U

    Returns
    -------
    [r1, r2, r3]
    """
    Delta0, DeltaS, mu = x

    Delta_ks = Delta0 - (DeltaS / (4.0 * t)) * epsilon_ks
    xi_ks    = epsilon_ks - mu
    E_ks     = np.clip(np.sqrt(Delta_ks**2 + xi_ks**2), 1e-12, None)

    if np.isinf(beta):
        tanh_f = np.ones_like(E_ks)
    else:
        tanh_f = np.tanh(beta * E_ks / 2.0)

    g_E  = tanh_f / (2.0 * E_ks)
    Ntot = float(Nk**2)

    r1 = Delta0 + (1.0 / (2.0 * Ntot)) * np.sum(
            term_for_Delta0 * Delta_ks * g_E)

    r2 = DeltaS + (1.0 / (2.0 * Ntot)) * np.sum(
            8.0 * Delta_t * Delta_ks * g_E)

    r3 = (1.0 / (2.0 * Ntot)) * np.sum(
            (xi_ks / E_ks) * tanh_f) - (1.0 - n_fill)

    return [r1, r2, r3]


def effective_gap(Delta0, DeltaS, epsilon_ks):
    """
    Mean absolute k-resolved gap  Deff = <|Delta0 - (DeltaS/4t) eps_k|>_k
    """
    Delta_ks = Delta0 - (DeltaS / (4.0 * t)) * epsilon_ks
    return float(np.mean(np.abs(Delta_ks)))