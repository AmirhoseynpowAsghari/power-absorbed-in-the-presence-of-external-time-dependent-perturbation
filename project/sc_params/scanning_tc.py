# scanning_tc.py
# =====================================================================
# Main V_SO scan loop
# =====================================================================

import time
import numpy as np

from parameters_tc import V_SO_values, n_filling
from kgrid          import build_kgrid
from solvers        import find_Tc


def run_vso_scan(V_SO_arr=None, n_fill=None, verbose=False):
    """
    Scan Tc and Deff over an array of V_SO values.

    Parameters
    ----------
    V_SO_arr : array_like, optional
        V_SO values to scan.  Defaults to parameters_tc.V_SO_values.
    n_fill   : float, optional
        Electron filling.  Defaults to parameters_tc.n_filling.
    verbose  : bool
        Print per-V_SO details from the Tc finder.

    Returns
    -------
    dict with keys:
        'V_SO'     – 1-D ndarray
        'Tc'       – 1-D ndarray
        'Deff_T0'  – 1-D ndarray
        'D0_T0'    – 1-D ndarray
        'DS_T0'    – 1-D ndarray
        'ratio'    – 1-D ndarray  (2*Deff/Tc, nan where Tc=0)
        'elapsed'  – float (wall-clock seconds)
    """
    if V_SO_arr is None:
        V_SO_arr = V_SO_values
    if n_fill is None:
        n_fill = n_filling

    V_SO_arr = np.asarray(V_SO_arr)
    N        = len(V_SO_arr)

    Tc_list   = np.zeros(N)
    Deff_list = np.zeros(N)
    D0_list   = np.zeros(N)
    DS_list   = np.zeros(N)

    # ── Header ───────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print(f"  {'V_SO/t':^10} {'Tc/t':^14} {'Deff(0)/t':^14} {'2Δ/kTc':^10}")
    print("─" * 60)

    t_start = time.time()

    for i, V_SO in enumerate(V_SO_arr):
        eps, term = build_kgrid(V_SO)
        Tc, Deff, D0, DS = find_Tc(n_fill, eps, term, verbose=verbose)

        Tc_list[i]   = Tc
        Deff_list[i] = Deff
        D0_list[i]   = D0
        DS_list[i]   = DS

        ratio_str = f"{2*Deff/Tc:.3f}" if Tc > 1e-8 else "  —  "
        print(f"  {V_SO:^10.4f}   {Tc:^14.6f}   {Deff:^14.6f}   "
              f"{ratio_str:^10}")

    elapsed = time.time() - t_start
    print("─" * 60)
    print(f"  Done in {elapsed:.1f} s")

    ratio = np.where(Tc_list > 1e-8, 2.0 * Deff_list / Tc_list, np.nan)

    return {
        'V_SO'    : V_SO_arr,
        'Tc'      : Tc_list,
        'Deff_T0' : Deff_list,
        'D0_T0'   : D0_list,
        'DS_T0'   : DS_list,
        'ratio'   : ratio,
        'elapsed' : elapsed,
    }