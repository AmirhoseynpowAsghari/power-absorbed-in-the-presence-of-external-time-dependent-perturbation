# main_ua.py
# =====================================================================
# Entry point — ultrasonic attenuation
# Loads SC params from previous code's JSON output automatically.
# =====================================================================

import numpy as np

from parameters_ua import (
    VSO_SWEEP_LIST, T_FRACS_DEFAULT,
    E_grid_min, E_grid_max, NE,
    UA_RESULTS_DIR
)
from sc_loader    import load_sc_params
from scanning_ua  import temperature_sweep, vso_scan
from plotting_ua  import (plot_temperature_sweep,
                           plot_vso_scan,
                           print_vso_summary)
from io_utils_ua  import (save_temperature_sweep,
                           load_temperature_sweep,
                           save_vso_scan,
                           load_vso_scan)


def main(recompute=True,
         sc_json=None,
         sc_npz=None):
    """
    Parameters
    ----------
    recompute : bool
        True  → run physics, save JSON, plot.
        False → load saved JSON, plot only.
    sc_json   : str, optional – path to SC params JSON from Tc code
    sc_npz    : str, optional – path to SC params NPZ  from Tc code
    """
    print("="*70)
    print("  ULTRASONIC ATTENUATION — modular version")
    print("  SC params loaded from Tc-vs-VSO code output")
    print("="*70)

    # ── Load SC parameters from the previous code's output ────────────
    sc_params, source = load_sc_params(
        json_path=sc_json,
        npz_path=sc_npz,
        verbose=True
    )
    print(f"  Source: {source}  |  {len(sc_params)} V_SO points")

    E_grid = np.linspace(E_grid_min, E_grid_max, NE)

    # ─────────────────────────────────────────────────────────────────
    # PART 1 — Temperature sweep
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─"*60)
    print("  PART 1 — Temperature sweep")
    print("─"*60)

    if recompute:
        all_results = temperature_sweep(
            VSO_SWEEP_LIST, sc_params, E_grid=E_grid
        )
        save_temperature_sweep(all_results, directory=UA_RESULTS_DIR)
    else:
        print("  Loading temperature-sweep results …")
        all_results = load_temperature_sweep(directory=UA_RESULTS_DIR)

    plot_temperature_sweep(
        all_results,
        VSO_list=VSO_SWEEP_LIST,
        colors=["blue", "red", "green"]
    )

    # ─────────────────────────────────────────────────────────────────
    # PART 2 — V_SO scan
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─"*60)
    print("  PART 2 — V_SO scan")
    print("─"*60)

    # FIX: use a single local variable that is always assigned
    #      BEFORE it is used, regardless of the recompute branch.
    if recompute:
        # Use the imported constant — no local re-assignment needed
        active_fracs = T_FRACS_DEFAULT

        VSO_arr, vso_results = vso_scan(
            sc_params,
            T_fracs=active_fracs,
            E_grid=E_grid
        )
        save_vso_scan(
            VSO_arr, vso_results, active_fracs,
            filepath=UA_RESULTS_DIR / "vso_scan.json"
        )
    else:
        print("  Loading VSO-scan results …")
        # load_vso_scan returns the fracs that were used when saving
        VSO_arr, vso_results, active_fracs = load_vso_scan(
            filepath=UA_RESULTS_DIR / "vso_scan.json"
        )

    # active_fracs is guaranteed to be defined here in both branches
    plot_vso_scan(VSO_arr, vso_results, active_fracs)
    print_vso_summary(VSO_arr, vso_results, active_fracs)

    return all_results, vso_results


if __name__ == "__main__":
    results, vso_results = main(recompute=True)