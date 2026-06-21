# absorption_u.py
# =====================================================================
# Ultrasonic absorption W and ratio W/W_N for the U-scan.
# Identical physics to absorption.py in the VSO scan.
# =====================================================================

import numpy as np
from scipy.integrate import trapezoid

from parameters_ua_u import hbar, omega, B, eta
from physics_ua_u    import fermi_vec


def compute_W(T, mu, Delta, E_grid, gE_table, include_gap=True):
    """
    Ultrasonic absorption power W(T).

    Parameters
    ----------
    T           : float
    mu          : float
    Delta       : float   – SC gap (0 when include_gap=False)
    E_grid      : ndarray
    gE_table    : ndarray – pre-computed DOS (same for all U iterations)
    include_gap : bool

    Returns
    -------
    float – W value
    """
    eps      = 1e-6
    Ep_grid  = E_grid + hbar * omega

    gE_vals  = gE_table.copy()
    gEp_vals = np.interp(Ep_grid, E_grid, gE_table, left=0.0, right=0.0)

    # Pair-breaking threshold at T ≈ 0
    if include_gap and Delta > 1e-10:
        if T < 1e-4 and (hbar * omega < 2.0 * Delta):
            return 0.0

    Delta_eff = Delta if include_gap else 0.0

    xi_E  = E_grid  - mu
    xi_Ep = Ep_grid - mu

    E_qp  = np.sqrt(xi_E**2  + Delta_eff**2)
    Ep_qp = np.sqrt(xi_Ep**2 + Delta_eff**2)

    xi_abs   = np.sqrt(np.maximum(E_qp**2  - Delta_eff**2, 0.0))
    xi_abs_p = np.sqrt(np.maximum(Ep_qp**2 - Delta_eff**2, 0.0))

    E_qp_safe  = np.where(E_qp  > eps, E_qp,  eps)
    Ep_qp_safe = np.where(Ep_qp > eps, Ep_qp, eps)

    bracket = 1.0 + (xi_abs * xi_abs_p) / (E_qp_safe * Ep_qp_safe)
    if include_gap and Delta_eff > 1e-10:
        bracket += eta * (Delta_eff**2) / (E_qp_safe * Ep_qp_safe)

    diffF     = fermi_vec(Ep_grid, T, mu) - fermi_vec(E_grid, T, mu)
    integrand = gE_vals * gEp_vals * bracket * diffF

    mask   = np.abs(E_grid) > eps
    result = trapezoid(integrand[mask], E_grid[mask])

    return 2.0 * np.pi * omega * (B**2) * result


def compute_ratio(T, mu, Delta, E_grid, gE_table):
    """W / W_N (nan if |W_N| < 1e-15)."""
    W  = compute_W(T, mu, Delta, E_grid, gE_table, include_gap=True)
    WN = compute_W(T, mu, Delta, E_grid, gE_table, include_gap=False)
    return abs(W / WN) if abs(WN) > 1e-15 else float('nan')