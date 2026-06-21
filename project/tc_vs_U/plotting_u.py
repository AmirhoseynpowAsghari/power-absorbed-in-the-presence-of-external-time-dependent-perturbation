# plotting_u.py
# =====================================================================
# Visualisation for the Tc vs U scan
# =====================================================================

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from parameters_u import FIGURES_DIR

FIGURES_DIR.mkdir(exist_ok=True)


def _save(fig, name):
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=200, bbox_inches='tight')
    print(f"  ✓  Figure saved → {path}")
    plt.show()


def plot_u_scan(results, meta=None):
    """
    Three-panel figure:
      1. Tc / t  vs  U
      2. Deff(0) / t  vs  U
      3. 2Δ(0) / kB Tc  vs  U

    Parameters
    ----------
    results : dict – output of run_u_scan()
    meta    : dict, optional
    """
    U     = results['U']
    Tc    = results['Tc']
    Deff  = results['Deff_T0']
    ratio = results['ratio']

    if meta:
        title = (
            fr"$T_c$ vs $U$   "
            fr"(n = {meta.get('n_filling', '?')},  "
            fr"$V_{{SO}}/t$ = {meta.get('V_SO', '?')},  "
            fr"$\Delta_t/t$ = {meta.get('Delta_t_over_t', '?')})"
        )
    else:
        title = r"$T_c$ vs $U$"

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(title, fontsize=13)

    STYLE = dict(lw=2, ms=7, markerfacecolor='white', markeredgewidth=2)

    # ── Panel 1: Tc ───────────────────────────────────────────────────
    ax = axes[0]
    ax.plot(U, Tc, 'o-', color='crimson', **STYLE)
    ax.fill_between(U, 0, Tc, alpha=0.15, color='crimson')
    ax.set_xlabel(r"$U$ / t",    fontsize=13)
    ax.set_ylabel(r"$T_c$ / t",  fontsize=13)
    ax.set_title(r"Critical Temperature vs $U$", fontsize=12)
    ax.set_xlim(U[0], U[-1])
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    # ── Panel 2: Deff(0) ─────────────────────────────────────────────
    ax = axes[1]
    ax.plot(U, Deff, 's-', color='steelblue', **STYLE)
    ax.fill_between(U, 0, Deff, alpha=0.15, color='steelblue')
    ax.set_xlabel(r"$U$ / t",                    fontsize=13)
    ax.set_ylabel(r"$\Delta_{\rm eff}(0)$ / t",  fontsize=13)
    ax.set_title(r"Zero-Temperature Gap vs $U$",  fontsize=12)
    ax.set_xlim(U[0], U[-1])
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)

    # ── Panel 3: 2Δ/kTc ──────────────────────────────────────────────
    ax = axes[2]
    ax.plot(U, ratio, '^-', color='darkorange', **STYLE)
    ax.axhline(3.528, color='red', ls='--', lw=1.5, label='BCS = 3.528')
    ax.set_xlabel(r"$U$ / t",               fontsize=13)
    ax.set_ylabel(r"$2\Delta(0)/k_B T_c$",  fontsize=13)
    ax.set_title(r"BCS Ratio vs $U$",       fontsize=12)
    ax.set_xlim(U[0], U[-1])
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save(fig, 'Tc_vs_U.png')