# kgrid_ua_u.py
# =====================================================================
# k-space grid for the ultrasonic U-scan.
#
# CRITICAL PERFORMANCE NOTE:
#   V_SO is FIXED for the entire U scan.
#   → eps_plus_fixed and eps_minus_fixed are built ONCE at import time.
#   → The DOS table gE_table is also built ONCE (in dos_ua_u.py).
#   → Only Tc and Delta_eff change per U iteration (from SC_params).
# =====================================================================

import numpy as np
from parameters_ua_u import t, V_SO, Nk_ua

# ── Full BZ grid  [-π, π] × [-π, π] ─────────────────────────────────
kx = np.linspace(-np.pi, np.pi, Nk_ua)
ky = np.linspace(-np.pi, np.pi, Nk_ua)

dkx = 2.0 * np.pi / (Nk_ua - 1)
dky = 2.0 * np.pi / (Nk_ua - 1)

kx_grid, ky_grid = np.meshgrid(kx, ky)

# ── V_SO-independent geometry ─────────────────────────────────────────
sin_kx   = np.sin(kx_grid)
sin_ky   = np.sin(ky_grid)
cos_sum  = np.cos(kx_grid) + np.cos(ky_grid)
sqrt_sin = np.sqrt(sin_kx**2 + sin_ky**2)

# ── Band dispersions: FIXED because V_SO is constant ─────────────────
eps_plus_fixed  = -2.0 * t * cos_sum - 2.0 * V_SO * sqrt_sin
eps_minus_fixed = -2.0 * t * cos_sum + 2.0 * V_SO * sqrt_sin


def get_fixed_dispersions():
    """
    Return the pre-built band dispersions (V_SO is fixed).

    Returns
    -------
    eps_plus  : ndarray (Nk_ua, Nk_ua)
    eps_minus : ndarray (Nk_ua, Nk_ua)
    """
    return eps_plus_fixed, eps_minus_fixed