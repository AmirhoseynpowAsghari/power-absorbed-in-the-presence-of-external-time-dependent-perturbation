# scanning_ua_u.py
# =====================================================================
# Temperature sweep and U scan for the ultrasonic attenuation code.
#
# PERFORMANCE:
#   gE_table is passed in — built ONCE outside these functions.
#   Neither the temperature sweep nor the U scan rebuilds the DOS.
# =====================================================================

import numpy as np

from parameters_ua_u import (
    n_target, T_SCAN_POINTS, T_SCAN_OVERHEAD, T_FRACS_DEFAULT
)
from sc_loader_u  import get_sc_params
from physics_ua_u import Delta_T, find_mu
from absorption_u import compute_W, compute_ratio


# ── 1. Temperature sweep for a list of U values ───────────────────────
def temperature_sweep(U_list, sc_params, gE_table, E_grid):
    """
    For each U in U_list, sweep T and record Delta, mu, W, W_N, ratio.

    Parameters
    ----------
    U_list    : list of float
    sc_params : dict – from sc_loader_u.load_sc_params()
    gE_table  : 1-D ndarray – pre-computed DOS (FIXED, passed in)
    E_grid    : 1-D ndarray

    Returns
    -------
    dict keyed by U value
    """
    T_max  = max(get_sc_params(U, sc_params)[0]
                 for U in U_list) * T_SCAN_OVERHEAD
    T_vals = np.linspace(0.0, T_max, T_SCAN_POINTS)

    all_results = {}

    for U in U_list:
        Tc, Delta0 = get_sc_params(U, sc_params)

        print(f"\n{'─'*60}")
        print(f"  U = {U:.2f}   Tc = {Tc:.6f}   Delta_eff = {Delta0:.4f}")
        print(f"{'─'*60}")
        print(f"  {'T':^8} {'T/Tc':^8} {'Delta':^10} "
              f"{'mu':^12} {'W/WN':^10}")
        print(f"  {'─'*52}")

        res = {k: [] for k in
               ('T', 'T_over_Tc', 'Delta', 'mu', 'W', 'WN', 'ratio')}

        for idx, T in enumerate(T_vals):
            Delta = Delta_T(T, Tc, Delta0)
            mu    = find_mu(T, Delta)

            W     = compute_W(T, mu, Delta, E_grid, gE_table,
                              include_gap=True)
            WN    = compute_W(T, mu, Delta, E_grid, gE_table,
                              include_gap=False)
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

        res.update({'Tc': Tc, 'Delta0': Delta0, 'U': U})
        all_results[U] = res

    return all_results


# ── 2. U scan at fixed T/Tc fractions ────────────────────────────────
def u_scan(sc_params, gE_table, E_grid, T_fracs=None):
    """
    Compute W/W_N vs U at fixed T/Tc fractions.

    DOS table is passed in — built ONCE, reused for every U.

    Parameters
    ----------
    sc_params : dict
    gE_table  : 1-D ndarray – pre-computed DOS
    E_grid    : 1-D ndarray
    T_fracs   : tuple of float

    Returns
    -------
    U_arr   : 1-D ndarray
    results : dict keyed by fraction
    """
    if T_fracs is None:
        T_fracs = T_FRACS_DEFAULT

    U_values = sorted(sc_params.keys())
    results  = {frac: {'ratio': [], 'Delta': [], 'mu': []}
                for frac in T_fracs}

    print("\n" + "="*70)
    print(f"  U SCAN — W/W_N vs U  (V_SO fixed, DOS built once)")
    print("="*70)

    for U in U_values:
        Tc, Delta0 = get_sc_params(U, sc_params)
        print(f"\n  U={U:.2f}  Tc={Tc:.4f}  Delta_eff={Delta0:.4f}")

        for frac in T_fracs:
            T_fixed = frac * Tc
            Delta   = Delta_T(T_fixed, Tc, Delta0)
            mu      = find_mu(T_fixed, Delta)

            # gE_table is already built — no DOS rebuild here
            ratio = compute_ratio(T_fixed, mu, Delta, E_grid, gE_table)

            results[frac]['ratio'].append(ratio)
            results[frac]['Delta'].append(Delta)
            results[frac]['mu'].append(mu)

            print(f"    T/Tc={frac:.2f}  T={T_fixed:.5f}  "
                  f"Delta={Delta:.5f}  W/WN={ratio:.5f}")

    for frac in T_fracs:
        for k in results[frac]:
            results[frac][k] = np.array(results[frac][k])

    return np.array(U_values), results