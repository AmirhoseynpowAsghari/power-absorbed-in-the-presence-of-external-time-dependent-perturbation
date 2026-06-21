# scanning_ua.py
# =====================================================================
# Temperature sweep and V_SO scan for ultrasonic attenuation
# =====================================================================

import time
import numpy as np

from parameters_ua import (
    n_target, T_SCAN_POINTS, T_SCAN_OVERHEAD,
    T_FRACS_DEFAULT, E_grid_min, E_grid_max, NE
)
from sc_loader  import get_sc_params
from kgrid_ua   import build_dispersions_ua
from dos_ua     import compute_dos
from physics_ua import Delta_T, find_mu
from absorption import compute_W, compute_ratio


# ── 1. Temperature sweep for a list of VSO values ────────────────────
def temperature_sweep(VSO_list, sc_params, T_vals=None, E_grid=None):
    """
    For each VSO, sweep T and record Delta, mu, W, W_N, W/W_N.

    Parameters
    ----------
    VSO_list  : list of float
    sc_params : dict – from sc_loader.load_sc_params()
    T_vals    : 1-D ndarray, optional – temperature grid
    E_grid    : 1-D ndarray, optional – energy grid

    Returns
    -------
    dict keyed by VSO
    """
    if E_grid is None:
        E_grid = np.linspace(E_grid_min, E_grid_max, NE)

    if T_vals is None:
        T_max  = max(get_sc_params(v, sc_params)[0]
                     for v in VSO_list) * T_SCAN_OVERHEAD
        T_vals = np.linspace(0.0, T_max, T_SCAN_POINTS)

    all_results = {}

    for VSO in VSO_list:
        Tc, Delta0 = get_sc_params(VSO, sc_params)

        print(f"\n{'─'*60}")
        print(f"  V_SO = {VSO}   Tc = {Tc:.6f}   Delta0 = {Delta0:.4f}")
        print(f"{'─'*60}")

        # DOS (once per VSO)
        eps_plus, eps_minus = build_dispersions_ua(VSO)
        print("  Computing DOS …", end=" ", flush=True)
        t0 = time.time()
        gE_table = compute_dos(E_grid, eps_plus, eps_minus)
        print(f"done ({time.time()-t0:.2f} s)")

        res = {k: [] for k in
               ('T', 'T_over_Tc', 'Delta', 'mu', 'W', 'WN', 'ratio')}

        print(f"  {'T':^8} {'T/Tc':^8} {'Delta':^10} "
              f"{'mu':^12} {'W/WN':^10}")
        print(f"  {'─'*52}")

        for idx, T in enumerate(T_vals):
            Delta = Delta_T(T, Tc, Delta0)
            mu    = find_mu(T, Delta, VSO)

            W     = compute_W(T, mu, Delta, E_grid, gE_table, include_gap=True)
            WN    = compute_W(T, mu, Delta, E_grid, gE_table, include_gap=False)
            ratio = abs(W / WN) if abs(WN) > 1e-15 else float('nan')

            res['T'].append(T)
            res['T_over_Tc'].append(T / Tc)
            res['Delta'].append(Delta)
            res['mu'].append(mu)
            res['W'].append(W)
            res['WN'].append(WN)
            res['ratio'].append(ratio)

            if idx % 10 == 0:
                print(f"  {T:^8.4f} {T/Tc:^8.4f} {Delta:^10.4f} "
                      f"{mu:^12.6f} {ratio:^10.4f}")

        for k in res:
            res[k] = np.array(res[k])

        res.update({'Tc': Tc, 'Delta0': Delta0, 'VSO': VSO})
        all_results[VSO] = res

    return all_results


# ── 2. VSO scan at fixed T/Tc fractions ──────────────────────────────
def vso_scan(sc_params, T_fracs=None, E_grid=None):
    """
    Compute W/W_N vs V_SO at fixed T/Tc fractions.

    Parameters
    ----------
    sc_params : dict – from sc_loader.load_sc_params()
    T_fracs   : tuple of float
    E_grid    : 1-D ndarray, optional

    Returns
    -------
    VSO_arr : 1-D ndarray
    results : dict keyed by fraction
    """
    if T_fracs is None:
        T_fracs = T_FRACS_DEFAULT
    if E_grid is None:
        E_grid = np.linspace(E_grid_min, E_grid_max, NE)

    VSO_values = sorted(sc_params.keys())
    results    = {frac: {'ratio': [], 'Delta': [], 'mu': []}
                  for frac in T_fracs}

    print("\n" + "="*70)
    print("  VSO SCAN — W/W_N vs V_SO")
    print("="*70)

    for VSO in VSO_values:
        Tc, Delta0 = get_sc_params(VSO, sc_params)

        eps_plus, eps_minus = build_dispersions_ua(VSO)
        gE_table = compute_dos(E_grid, eps_plus, eps_minus)

        print(f"\n  V_SO={VSO:.4f}  Tc={Tc:.4f}  Delta0={Delta0:.4f}")

        for frac in T_fracs:
            T_fixed = frac * Tc
            Delta   = Delta_T(T_fixed, Tc, Delta0)
            mu      = find_mu(T_fixed, Delta, VSO)
            ratio   = compute_ratio(T_fixed, mu, Delta, E_grid, gE_table)

            results[frac]['ratio'].append(ratio)
            results[frac]['Delta'].append(Delta)
            results[frac]['mu'].append(mu)

            print(f"    T/Tc={frac:.2f}  T={T_fixed:.5f}  "
                  f"Delta={Delta:.5f}  W/WN={ratio:.5f}")

    for frac in T_fracs:
        for k in results[frac]:
            results[frac][k] = np.array(results[frac][k])

    return np.array(VSO_values), results