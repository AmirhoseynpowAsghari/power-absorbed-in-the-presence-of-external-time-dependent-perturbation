# scanning_u.py
# =====================================================================
# Main U scan loop.
#
# Performance note:
#   eps_fixed is built ONCE (V_SO fixed).
#   Only build_term(U) is called each iteration → faster than VSO scan.
# =====================================================================

import time
import numpy as np

from parameters_u import U_values, n_filling
from kgrid_u      import get_fixed_dispersions
from gap_term_u   import build_term
from solvers_u    import find_Tc


def run_u_scan(U_arr=None, n_fill=None, verbose=False):
    """
    Scan Tc and Deff over an array of U values.

    Parameters
    ----------
    U_arr   : array_like, optional – defaults to parameters_u.U_values
    n_fill  : float, optional      – defaults to parameters_u.n_filling
    verbose : bool                 – per-U detail from find_Tc

    Returns
    -------
    dict with keys:
        'U'        – 1-D ndarray
        'Tc'       – 1-D ndarray
        'Deff_T0'  – 1-D ndarray
        'D0_T0'    – 1-D ndarray
        'DS_T0'    – 1-D ndarray
        'ratio'    – 1-D ndarray  (2*Deff/Tc, nan where Tc=0)
        'elapsed'  – float
    """
    if U_arr  is None: U_arr  = U_values
    if n_fill is None: n_fill = n_filling

    U_arr = np.asarray(U_arr)
    N     = len(U_arr)

    Tc_arr   = np.zeros(N)
    Deff_arr = np.zeros(N)
    D0_arr   = np.zeros(N)
    DS_arr   = np.zeros(N)

    # k-grid is fixed for the entire scan
    eps_fixed = get_fixed_dispersions()

    # ── Header ───────────────────────────────────────────────────────
    print("\n" + "─"*65)
    print(f"  {'U/t':^10} {'Tc/t':^14} {'Deff(0)/t':^14} {'2Δ/kTc':^10}")
    print("─"*65)

    t_start = time.time()

    for i, U in enumerate(U_arr):
        # Only the interaction term is rebuilt each step
        term = build_term(U)

        Tc, Deff, D0, DS = find_Tc(
            n_fill, eps_fixed, term, verbose=verbose
        )

        Tc_arr[i]   = Tc
        Deff_arr[i] = Deff
        D0_arr[i]   = D0
        DS_arr[i]   = DS

        ratio_str = f"{2*Deff/Tc:.3f}" if Tc > 1e-8 else "  —  "
        print(f"  {U:^10.2f}   {Tc:^14.6f}   {Deff:^14.6f}   "
              f"{ratio_str:^10}")

    elapsed = time.time() - t_start
    print("─"*65)
    print(f"  Done in {elapsed:.1f} s")

    ratio = np.where(Tc_arr > 1e-8, 2.0 * Deff_arr / Tc_arr, np.nan)

    return {
        'U'       : U_arr,
        'Tc'      : Tc_arr,
        'Deff_T0' : Deff_arr,
        'D0_T0'   : D0_arr,
        'DS_T0'   : DS_arr,
        'ratio'   : ratio,
        'elapsed' : elapsed,
    }