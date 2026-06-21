# dos_ua.py
# =====================================================================
# Numba-accelerated DOS for the ultrasonic calculation
# =====================================================================

import numpy as np
from numba import jit, prange

from parameters_ua import sigma, t, Nk_ua
from kgrid_ua      import dkx, dky


@jit(nopython=True, parallel=True)
def _dos_kernel(E_grid, eps_plus, eps_minus, sigma, t, dkx, dky):
    """
    Gaussian-broadened DOS kernel (Numba parallel).

    g(E) = prefactor * sum_k [ exp(-(E-eps_+)^2/σ^2)
                              + exp(-(E-eps_-)^2/σ^2) ] * norm
    """
    NE        = len(E_grid)
    Nkx, Nky = eps_plus.shape
    gE        = np.zeros(NE)
    prefactor = 1.0 / (np.pi ** 1.5 * sigma * t)
    norm      = dkx * dky / (2.0 * np.pi) ** 2

    for i in prange(NE):
        E     = E_grid[i]
        total = 0.0
        for ix in range(Nkx):
            for iy in range(Nky):
                d_plus  = (E / t - eps_plus[ix, iy]  / t)
                d_minus = (E / t - eps_minus[ix, iy] / t)
                total  += np.exp(-(d_plus  ** 2) / sigma ** 2)
                total  += np.exp(-(d_minus ** 2) / sigma ** 2)
        gE[i] = prefactor * total * norm

    return gE


def compute_dos(E_grid, eps_plus, eps_minus):
    """
    Public wrapper: compute DOS on E_grid.

    Parameters
    ----------
    E_grid    : 1-D ndarray
    eps_plus  : 2-D ndarray (Nk_ua, Nk_ua)
    eps_minus : 2-D ndarray (Nk_ua, Nk_ua)

    Returns
    -------
    gE : 1-D ndarray
    """
    return _dos_kernel(
        E_grid,
        eps_plus.astype(np.float64),
        eps_minus.astype(np.float64),
        sigma, t, dkx, dky
    )