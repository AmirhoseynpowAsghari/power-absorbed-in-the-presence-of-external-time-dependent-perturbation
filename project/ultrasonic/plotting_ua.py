# plotting_ua.py
# =====================================================================
# All visualisation for the ultrasonic attenuation results
# =====================================================================

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("figures")
OUTPUT_DIR.mkdir(exist_ok=True)


def _save(fig, name):
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=200, bbox_inches='tight')
    print(f"  ✓  Figure → {path}")
    plt.show()


# ── 1. Six-panel temperature-sweep figure ────────────────────────────
def plot_temperature_sweep(all_results, VSO_list=None, colors=None):
    if VSO_list is None:
        VSO_list = list(all_results.keys())
    if colors is None:
        palette = plt.cm.tab10.colors
        colors  = [palette[i % 10] for i in range(len(VSO_list))]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    ax1, ax2, ax3, ax4, ax5, ax6 = axes.flat

    for col, VSO in zip(colors, VSO_list):
        res    = all_results[VSO]
        Tc     = res['Tc']
        Delta0 = res['Delta0']
        lbl    = f'$V_{{SO}}={VSO}$'

        mask = res['Delta'] > 1e-4
        ax1.plot(res['Delta'][mask] / Delta0, res['ratio'][mask],
                 'o-', color=col, lw=2, ms=4, label=lbl)
        ax2.plot(res['T_over_Tc'], res['ratio'],
                 'o-', color=col, lw=2, ms=4, label=lbl)
        ax3.plot(res['T_over_Tc'], res['Delta'] / Delta0,
                 '-', color=col, lw=2, label=lbl)
        ax4.plot(res['T'], res['mu'], '-', color=col, lw=2,
                 label=f'{lbl} (Tc={Tc:.3f})')
        ax4.axvline(Tc, color=col, ls=':', alpha=0.5)
        ax5.plot(res['T_over_Tc'], res['mu'], '-', color=col, lw=2, label=lbl)
        ax6.plot(res['T'], res['Delta'], '-', color=col, lw=2,
                 label=f'{lbl} (Δ₀={Delta0:.3f})')
        ax6.axvline(Tc, color=col, ls=':', alpha=0.5)

    for ax in (ax2, ax3, ax5):
        ax.axvline(1.0, color='gray', ls='--', alpha=0.5)
        ax.set_xlim(0, 1.5)

    ax1.set(xlabel=r'$\Delta/\Delta_0$',   ylabel=r'$W/W_N$',
            title=r'$W/W_N$ vs Normalised Gap',   ylim=(0.8, 1.0))
    ax2.set(xlabel=r'$T/T_c$',             ylabel=r'$W/W_N$',
            title=r'$W/W_N$ vs $T/T_c$',          ylim=(0.8, 1.0))
    ax3.set(xlabel=r'$T/T_c$',             ylabel=r'$\Delta/\Delta_0$',
            title='BCS Gap (universal)')
    ax4.set(xlabel=r'$T$',                 ylabel=r'$\mu(T)$',
            title=r'$\mu$ vs $T$')
    ax5.set(xlabel=r'$T/T_c$',             ylabel=r'$\mu(T)$',
            title=r'$\mu$ vs $T/T_c$')
    ax6.set(xlabel=r'$T$',                 ylabel=r'$\Delta(T)$',
            title=r'$\Delta$ vs $T$')

    for ax in axes.flat:
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.suptitle(r'Ultrasonic Attenuation — '
                 r'$U=-75t$, $n=1.885$, $\hbar\omega=0.7t$',
                 fontsize=13, y=1.01)
    plt.tight_layout()
    _save(fig, 'W_WN_temperature_sweep.png')


# ── 2. W/W_N vs V_SO ─────────────────────────────────────────────────
def plot_vso_scan(VSO_arr, results, T_fracs):
    palette = ['darkred', 'red', 'orangered', 'orange', 'gold']
    colors  = palette[:len(T_fracs)]
    fig, ax = plt.subplots(figsize=(8, 5))

    for frac, col in zip(T_fracs, colors):
        ax.plot(VSO_arr, results[frac]['ratio'],
                'o-', color=col, lw=2, ms=6,
                label=fr'$T/T_c={frac:.1f}$')

    ax.set_xlabel(r'$V_{SO}\;[t]$', fontsize=13)
    ax.set_ylabel(r'$W/W_N$',       fontsize=13)
    ax.set_title(r'Ultrasonic Attenuation vs Spin-Orbit Coupling'
                 '\n'
                 r'$U=-75t$,  $n=1.885$,  $\hbar\omega=0.7t$',
                 fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save(fig, 'W_WN_vs_VSO.png')


# ── 3. Console summary ────────────────────────────────────────────────
def print_vso_summary(VSO_arr, results, T_fracs):
    print("\n" + "="*70)
    print("  W/W_N  vs  V_SO  (fixed T/Tc fractions)")
    print("="*70)
    hdr = f"  {'VSO':>6}" + "".join(f"  T/Tc={f:.1f}" for f in T_fracs)
    print(hdr)
    print("  " + "─"*60)
    for i, VSO in enumerate(VSO_arr):
        row = f"  {VSO:>6.4f}"
        for frac in T_fracs:
            row += f"  {results[frac]['ratio'][i]:>9.4f}"
        print(row)
    print("="*70)