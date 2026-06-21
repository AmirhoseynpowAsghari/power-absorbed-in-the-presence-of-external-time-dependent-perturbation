# plotting_tc.py
# =====================================================================
# Visualisation for the Tc vs V_SO scan
# =====================================================================

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(exist_ok=True)


def _save(fig, name):
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=200, bbox_inches='tight')
    print(f"  ✓  Figure saved → {path}")
    plt.show()


def plot_tc_scan(results, meta=None):
    """
    Three-panel figure:
      1. Tc / t  vs  V_SO
      2. Deff(0) / t  vs  V_SO
      3. 2Δ(0) / kB Tc  vs  V_SO

    Parameters
    ----------
    results : dict – output of scanning_tc.run_vso_scan()
    meta    : dict, optional – metadata for suptitle
              (keys: n_filling, U_over_t, Delta_t_over_t)
    """
    V_SO  = results['V_SO']
    Tc    = results['Tc']
    Deff  = results['Deff_T0']
    ratio = results['ratio']

    # ── Suptitle ──────────────────────────────────────────────────────
    if meta is not None:
        title = (
            fr"$T_c$ vs $V_{{SO}}$   "
            fr"(n = {meta['n_filling']},  "
            fr"$U/t$ = {meta['U_over_t']},  "
            fr"$\Delta_t/t$ = {meta['Delta_t_over_t']})"
        )
    else:
        title = r"$T_c$ vs $V_{SO}$"

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(title, fontsize=13)

    STYLE = dict(lw=2, ms=7, markerfacecolor='white', markeredgewidth=2)

    # ── Panel 1: Tc ───────────────────────────────────────────────────
    ax = axes[0]
    ax.plot(V_SO, Tc, 'o-', color='crimson', **STYLE)
    ax.fill_between(V_SO, 0, Tc, alpha=0.15, color='crimson')
    ax.set_xlabel(r"$V_{SO}$ / t",  fontsize=13)
    ax.set_ylabel(r"$T_c$ / t",     fontsize=13)
    ax.set_title(r"Critical Temperature vs $V_{SO}$", fontsize=12)
    ax.set_xlim(V_SO[0], V_SO[-1])
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    # ── Panel 2: Deff(T=0) ───────────────────────────────────────────
    ax = axes[1]
    ax.plot(V_SO, Deff, 's-', color='steelblue', **STYLE)
    ax.fill_between(V_SO, 0, Deff, alpha=0.15, color='steelblue')
    ax.set_xlabel(r"$V_{SO}$ / t",              fontsize=13)
    ax.set_ylabel(r"$\Delta_{\rm eff}(0)$ / t", fontsize=13)
    ax.set_title(r"Zero-Temperature Gap vs $V_{SO}$", fontsize=12)
    ax.set_xlim(V_SO[0], V_SO[-1])
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    # ── Panel 3: 2Δ/kTc ──────────────────────────────────────────────
    ax = axes[2]
    ax.plot(V_SO, ratio, '^-', color='darkorange', **STYLE)
    ax.axhline(3.528, color='red', ls='--', lw=1.5, label='BCS = 3.528')
    ax.set_xlabel(r"$V_{SO}$ / t",           fontsize=13)
    ax.set_ylabel(r"$2\Delta(0)\,/\,k_B T_c$", fontsize=13)
    ax.set_title(r"BCS Ratio vs $V_{SO}$",   fontsize=12)
    ax.set_xlim(V_SO[0], V_SO[-1])
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save(fig, 'Tc_vs_VSO.png')