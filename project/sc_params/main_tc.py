# main_tc.py
# =====================================================================
# Entry point for the Tc vs V_SO calculation
# =====================================================================

import numpy as np
import warnings
warnings.filterwarnings('ignore')

from parameters_tc import (
    V_SO_values, n_filling, U_over_t,
    Delta_t_over_t, Nk, META
)
from scanning_tc import run_vso_scan
from plotting_tc  import plot_tc_scan
from io_utils_tc  import save_json, save_npz, load_json, load_npz


def main(recompute=True,
         json_path="results/tc_vs_vso.json",
         npz_path ="results/Tc_vs_VSO.npz"):
    """
    Parameters
    ----------
    recompute : bool
        True  → run the V_SO scan, save results, then plot.
        False → load previously saved JSON and plot only.
    """
    # ── Print run header ──────────────────────────────────────────────
    print("=" * 60)
    print(f"  Tc vs V_SO  |  fixed n = {n_filling:.4f}")
    print("=" * 60)
    print(f"  U/t          = {U_over_t}")
    print(f"  Δt/t         = {Delta_t_over_t}")
    print(f"  n            = {n_filling}")
    print(f"  V_SO range   : {V_SO_values[0]:.3f} → {V_SO_values[-1]:.3f}"
          f"  ({len(V_SO_values)} points)")
    print(f"  Nk           = {Nk}")

    # ── Compute or load ───────────────────────────────────────────────
    if recompute:
        results = run_vso_scan(V_SO_arr=V_SO_values, n_fill=n_filling)

        # Save both formats
        save_json(results, meta=META, filepath=json_path)
        save_npz (results, meta=META, filepath=npz_path)

    else:
        print("\n  Loading saved results …")
        results, META_loaded = load_json(json_path)
        # Merge loaded meta so plot title is correct
        META.update(META_loaded)

    # ── Plot ──────────────────────────────────────────────────────────
    plot_tc_scan(results, meta=META)

    # ── Final summary ─────────────────────────────────────────────────
    V_SO = results['V_SO']
    Tc   = results['Tc']
    Deff = results['Deff_T0']

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Max Tc   = {Tc.max():.6f}  at V_SO = "
          f"{V_SO[Tc.argmax()]:.4f}")
    print(f"  Max Deff = {Deff.max():.6f}  at V_SO = "
          f"{V_SO[Deff.argmax()]:.4f}")
    elapsed = results.get('elapsed', 0)
    print(f"  Wall time: {elapsed:.1f} s")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Set recompute=False to skip physics and reload from disk
    results = main(recompute=True)