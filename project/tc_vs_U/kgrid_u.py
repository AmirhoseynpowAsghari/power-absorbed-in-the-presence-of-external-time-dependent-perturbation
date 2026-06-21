# kgrid_u.py
# =====================================================================
# k-space grid for the Tc-vs-U scan.
#
# IMPORTANT DIFFERENCE from kgrid.py (VSO code):
#   V_SO is FIXED → band dispersions are built ONCE at import time.
#   Only the interaction kernel term_for_Delta0 changes with U.
# =====================================================================

import numpy as np
from parameters_u import t, V_SO, Nk

# ── Static k-space mesh ───────────────────────────────────────────────
kx_vals = np.linspace(0, np.pi, Nk)
ky_vals = np.linspace(0, np.pi, Nk)
KX, KY  = np.meshgrid(kx_vals, ky_vals)

# ── V_SO-independent geometry ─────────────────────────────────────────
sqrt_sin     = np.sqrt(np.sin(KX)**2 + np.sin(KY)**2)
cos_sum      = np.cos(KX) + np.cos(KY)
s_k_factor   = 0.5 * (np.cos(KX) + np.cos(KY))
s_prime_vals = np.array([1.0, -1.0])

# ── Band dispersions: built ONCE because V_SO is fixed ────────────────
eps_fixed = np.zeros((Nk, Nk, 2))
eps_fixed[:, :, 0] = -2.0 * t * cos_sum - 2.0 * V_SO * sqrt_sin  # s = +1
eps_fixed[:, :, 1] = -2.0 * t * cos_sum + 2.0 * V_SO * sqrt_sin  # s = -1


def get_fixed_dispersions():
    """
    Return the pre-computed band dispersions (V_SO is fixed).

    Returns
    -------
    eps_fixed : ndarray, shape (Nk, Nk, 2)
        eps_fixed[:,:,0] = eps_{k,+}
        eps_fixed[:,:,1] = eps_{k,-}
    """
    return eps_fixed