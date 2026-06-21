# dos_ua_u.py
# =====================================================================
# Numba DOS — built ONCE for the entire U scan (V_SO fixed).
#
# Public API:
#   build_dos_table(E_grid)  → gE_table  (call once in main)
#   get_dos_table()          → cached gE_table (call anywhere)
# =====================================================================

import numpy as np
import time
from numba import jit, prange

from parameters_ua_u import sigma, t, NE, E_grid_min, E_grid_max
from kgrid_ua_u      import dkx, dky, get_fixed_dispersions

# Module-level cache
_gE_cache: dict = {}


@jit(nopython=True, parallel=True)
def _dos_kernel(E_grid, eps_plus, eps_minus, sigma, t, dkx, dky):
    """Gaussian-broadened DOS — Numba parallel kernel."""
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


def build_dos_table(E_grid=None, verbose=True):
    """
    Build and cache the DOS table.

    Because V_SO is fixed, this only needs to be called ONCE
    regardless of how many U values are scanned.

    Parameters
    ----------
    E_grid  : 1-D ndarray, optional
    verbose : bool

    Returns
    -------
    gE_table : 1-D ndarray
    E_grid   : 1-D ndarray  (returned so callers have the grid)
    """
    if E_grid is None:
        E_grid = np.linspace(E_grid_min, E_grid_max, NE)

    cache_key = id(E_grid)
    if cache_key in _gE_cache:
        if verbose:
            print("  [dos_ua_u] Using cached DOS table.")
        return _gE_cache[cache_key], E_grid

    eps_plus, eps_minus = get_fixed_dispersions()

    if verbose:
        print("  [dos_ua_u] Computing DOS (V_SO fixed → built once) …",
              end=" ", flush=True)
    t0 = time.time()

    gE_table = _dos_kernel(
        E_grid,
        eps_plus.astype(np.float64),
        eps_minus.astype(np.float64),
        sigma, t, dkx, dky
    )

    if verbose:
        print(f"done ({time.time()-t0:.2f} s)")

    _gE_cache[cache_key] = gE_table
    return gE_table, E_grid


def get_dos_table(E_grid):
    """Return cached table (builds if not yet computed)."""
    return build_dos_table(E_grid, verbose=False)[0]