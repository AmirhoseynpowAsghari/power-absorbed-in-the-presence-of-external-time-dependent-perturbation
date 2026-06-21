# main_ua_u.py
# =====================================================================
# Entry point — ultrasonic attenuation (U scan, fixed V_SO).
#
# Data flow:
#   tc_vs_U/results/tc_vs_U.json  →  sc_loader_u  →  SC_params dict
#   kgrid_ua_u  →  eps_plus/minus (fixed, built at import)
#   dos_ua_u    →  gE_table       (fixed, built ONCE here)
#   scanning_ua_u → W/W_N arrays  →  io_utils_ua_u → JSON files
# =====================================================================

import numpy as np
import warnings
warnings.filterwarnings('ignore')

from parameters_ua_u import (
    V_SO, T_FRACS_DEFAULT, U_DETAIL_LIST,
    NE, E_grid_min, E_grid_max,
    UA_U_RESULTS_DIR
)
from sc_loader_u      import load_sc_params
from dos_ua_u         import build_dos_table
from scanning_ua_u    import temperature_sweep, u_scan
from plotting_ua_u    import (plot_temperature_sweep,
                               plot_u_scan,
                               print_u_summary)
from io_utils_ua_u    import (save_temperature_sweep,
                               load_temperature_sweep,
                               save_u_scan,
                               load_u_scan)


def main(recompute=True, sc_json=None, sc_npz=None):
    """
    Parameters
    ----------
    recompute : bool
        True  → run physics, save JSON, plot.
        False → load saved JSON, plot only.
    sc_json   : str, optional – override path to tc_vs_U.json
    sc_npz    : str, optional – override path to Tc_vs_U.npz
    """
    print("="*70)
    print(f"  ULTRASONIC ATTENUATION — U scan (fixed V_SO = {V_SO})")
    print("  SC params loaded from tc_vs_U code output")
    print("="*70)

    # ── Load SC parameters ────────────────────────────────────────────
    sc_params, source = load_sc_params(
        json_path=sc_json, npz_path=sc_npz, verbose=True
    )
    print(f"  Source: {source}  |  {len(sc_params)} U points")

    # ── Build energy grid ─────────────────────────────────────────────
    E_grid = np.linspace(E_grid_min, E_grid_max, NE)

    # ── Build DOS table ONCE (V_SO fixed for the entire scan) ─────────
    # This is the key performance gain over the VSO scan:
    # rebuilding gE_table for every U is unnecessary.
    gE_table, E_grid = build_dos_table(E_grid, verbose=True)

    # ── Select U values for the 6-panel detail figure ─────────────────
    all_U = sorted(sc_params.keys())
    if U_DETAIL_LIST is not None:
        U_detail = U_DETAIL_LIST
    else:
        # Auto: first, middle, last
        U_detail = [all_U[0], all_U[len(all_U) // 2], all_U[-1]]
    print(f"\n  Detail figure U values: {U_detail}")

    # ─────────────────────────────────────────────────────────────────
    # PART 1 — Temperature sweep (3 representative U values)
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─"*60)
    print("  PART 1 — Temperature sweep")
    print("─"*60)

    if recompute:
        all_results = temperature_sweep(
            U_detail, sc_params, gE_table, E_grid
        )
        save_temperature_sweep(all_results, directory=UA_U_RESULTS_DIR)
    else:
        print("  Loading temperature-sweep results …")
        all_results = load_temperature_sweep(directory=UA_U_RESULTS_DIR)

    plot_temperature_sweep(
        all_results,
        U_list=U_detail,
        colors=["blue", "red", "green"]
    )

    # ─────────────────────────────────────────────────────────────────
    # PART 2 — Full U scan at fixed T/Tc fractions
    # ─────────────────────────────────────────────────────────────────
    print("\n" + "─"*60)
    print("  PART 2 — Full U scan")
    print("─"*60)

    # Always assign active_fracs before use (avoids UnboundLocalError)
    if recompute:
        active_fracs = T_FRACS_DEFAULT
        U_arr, u_results = u_scan(
            sc_params, gE_table, E_grid, T_fracs=active_fracs
        )
        save_u_scan(
            U_arr, u_results, active_fracs,
            filepath=UA_U_RESULTS_DIR / "u_scan.json"
        )
    else:
        print("  Loading U-scan results …")
        U_arr, u_results, active_fracs = load_u_scan(
            filepath=UA_U_RESULTS_DIR / "u_scan.json"
        )

    plot_u_scan(U_arr, u_results, active_fracs)
    print_u_summary(U_arr, u_results, active_fracs)

    return all_results, u_results


if __name__ == "__main__":
    results, u_results = main(recompute=True)