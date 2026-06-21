# main_u.py
# =====================================================================
# Entry point for the Tc vs U scan.
#
# OUTPUT → results/tc_vs_U.json
#
# NEXT STAGE (ultrasonic code) reads this file via sc_loader.py
# by pointing SC_PARAMS_JSON at results/tc_vs_U.json instead of
# (or in addition to) tc_vs_vso.json.
# =====================================================================

import numpy as np
import warnings
warnings.filterwarnings('ignore')

from parameters_u import (
    U_values, n_filling, V_SO,
    Delta_t_over_t, Nk, META,
    JSON_PATH, NPZ_PATH
)
from scanning_u  import run_u_scan
from plotting_u  import plot_u_scan
from io_utils_u  import save_json, save_npz, load_json, load_npz


def main(recompute=True):
    """
    Parameters
    ----------
    recompute : bool
        True  → run U scan, save results, plot.
        False → load saved JSON, plot only.
    """
    # ── Header ────────────────────────────────────────────────────────
    print("="*65)
    print(f"  Tc vs U  |  fixed n = {n_filling:.4f},  V_SO/t = {V_SO:.4f}")
    print("="*65)
    print(f"  Delta_t/t = {Delta_t_over_t}")
    print(f"  U range   : {U_values[0]:.1f} → {U_values[-1]:.1f}"
          f"  ({len(U_values)} points)")
    print(f"  Nk        = {Nk}")

    # ── Run or load ───────────────────────────────────────────────────
    if recompute:
        results = run_u_scan(U_arr=U_values, n_fill=n_filling)

        save_json(results, meta=META, filepath=JSON_PATH)
        save_npz (results, meta=META, filepath=NPZ_PATH)
    else:
        print("\n  Loading saved results …")
        results, META_loaded = load_json(JSON_PATH)
        META.update(META_loaded)

    # ── Plot ──────────────────────────────────────────────────────────
    plot_u_scan(results, meta=META)

    # ── Summary ───────────────────────────────────────────────────────
    U    = results['U']
    Tc   = results['Tc']
    Deff = results['Deff_T0']

    print("\n" + "="*65)
    print("  SUMMARY")
    print("="*65)
    print(f"  Max Tc   = {Tc.max():.6f}  at U/t = "
          f"{U[Tc.argmax()]:.2f}")
    print(f"  Max Deff = {Deff.max():.6f}  at U/t = "
          f"{U[Deff.argmax()]:.2f}")
    print(f"  Elapsed  : {results.get('elapsed', 0):.1f} s")
    print("="*65)
    print(f"\n  Results saved → {JSON_PATH}")
    print(f"                 → {NPZ_PATH}")

    return results


if __name__ == "__main__":
    results = main(recompute=True)