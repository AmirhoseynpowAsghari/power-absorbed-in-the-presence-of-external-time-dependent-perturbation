# kgrid.py
# =====================================================================
# k-space grid — imports t, U, Delta_t from parameters_tc
# =====================================================================

import numpy as np
from parameters_tc import t, U, Delta_t, Nk

# ── Static geometry (built once) ──────────────────────────────────────
kx_vals = np.linspace(0, np.pi, Nk)
ky_vals = np.linspace(0, np.pi, Nk)
KX, KY  = np.meshgrid(kx_vals, ky_vals)

sqrt_sin     = np.sqrt(np.sin(KX)**2 + np.sin(KY)**2)
cos_sum      = np.cos(KX) + np.cos(KY)
s_k_factor   = 0.5 * (np.cos(KX) + np.cos(KY))
s_prime_vals = np.array([1.0, -1.0])


def build_dispersions(V_SO):
    """
    eps[:,:,0] = -2t cos_sum - 2 V_SO |sin k|   (+ helicity)
    eps[:,:,1] = -2t cos_sum + 2 V_SO |sin k|   (- helicity)
    """
    eps = np.zeros((Nk, Nk, 2))
    eps[:, :, 0] = -2.0 * t * cos_sum - 2.0 * V_SO * sqrt_sin
    eps[:, :, 1] = -2.0 * t * cos_sum + 2.0 * V_SO * sqrt_sin
    return eps


def build_gap_kernel(V_SO):
    """
    Coupling kernel entering the Delta0 gap equation:

        term = U + 8*Delta_t*s_k
                 + 4*(Delta_t/t)*V_SO * s'_± * |sin k|

    Uses U and Delta_t from parameters_tc — so it automatically
    reflects U/t=75, Delta_t/t=4.5 for this physical problem.
    """
    term = (
        U
        + 8.0 * Delta_t * s_k_factor[..., None]
        + 4.0 * (Delta_t / t) * V_SO
          * s_prime_vals[None, None, :] * sqrt_sin[..., None]
    )
    return term


def build_kgrid(V_SO):
    """Return (eps, term) — identical interface to monolithic build_kgrid."""
    return build_dispersions(V_SO), build_gap_kernel(V_SO)