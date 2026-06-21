# gap_term_u.py
# =====================================================================
# Build the interaction kernel that enters the gap equation.
#
# In the U scan:
#   - eps_fixed  stays constant  (V_SO fixed)
#   - term       changes with U  (rebuilt each iteration)
#
# This module is the ONLY thing that changes between U iterations.
# =====================================================================

import numpy as np
from parameters_u import t, Delta_t, V_SO
from kgrid_u      import s_k_factor, s_prime_vals, sqrt_sin


def build_term(U):
    """
    Build the coupling kernel for a given interaction strength U.

        term(k,s) = U
                  + 8 * Delta_t * s_k(k)
                  + 4 * (Delta_t/t) * V_SO * s * |sin k|

    Parameters
    ----------
    U : float – on-site interaction (in units of t, e.g. 75 … 125)

    Returns
    -------
    term : ndarray, shape (Nk, Nk, 2)
    """
    term = (
        U
        + 8.0 * Delta_t * s_k_factor[..., None]
        + 4.0 * (Delta_t / t) * V_SO
          * s_prime_vals[None, None, :] * sqrt_sin[..., None]
    )
    return term