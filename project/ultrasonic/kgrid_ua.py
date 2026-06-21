# kgrid_ua.py
# =====================================================================
# k-space grid for the ultrasonic attenuation code.
# Uses Nk_ua = 200 (different from the Tc code's Nk = 80).
# =====================================================================

import numpy as np
from parameters_ua import t, Nk_ua

# ── Full BZ grid  [-π, π] × [-π, π] ─────────────────────────────────
kx = np.linspace(-np.pi, np.pi, Nk_ua)
ky = np.linspace(-np.pi, np.pi, Nk_ua)

dkx = 2 * np.pi / (Nk_ua - 1)
dky = 2 * np.pi / (Nk_ua - 1)

kx_grid, ky_grid = np.meshgrid(kx, ky)

# ── V_SO-independent geometry ─────────────────────────────────────────
sin_kx   = np.sin(kx_grid)
sin_ky   = np.sin(ky_grid)
cos_sum  = np.cos(kx_grid) + np.cos(ky_grid)
sqrt_sin = np.sqrt(sin_kx**2 + sin_ky**2)


def build_dispersions_ua(VSO):
    """
    Return the two helicity bands on the 200×200 k-grid.

        eps_+ = -2t (cos kx + cos ky) - 2 V_SO |sin k|
        eps_- = -2t (cos kx + cos ky) + 2 V_SO |sin k|

    Parameters
    ----------
    VSO : float

    Returns
    -------
    eps_plus  : ndarray (Nk_ua, Nk_ua)
    eps_minus : ndarray (Nk_ua, Nk_ua)
    """
    eps_plus  = -2.0 * t * cos_sum - 2.0 * VSO * sqrt_sin
    eps_minus = -2.0 * t * cos_sum + 2.0 * VSO * sqrt_sin
    return eps_plus, eps_minus