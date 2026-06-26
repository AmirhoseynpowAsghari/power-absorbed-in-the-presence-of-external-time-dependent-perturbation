# bayesian_opt.py
# =====================================================================
# Bayesian Optimization over (U, V_SO, n) to maximise Tc.
#
# Drop this file into project/tc_vs_U/ and run:
#
#     python bayesian_opt.py
#
# It reuses the existing solver (kgrid_u, gap_term_u, solvers_u)
# without modifying any other file.
#
# Output
# ------
#   results/bo_results.json   – full call history + optimum
#   figures/bo_convergence.png
#   figures/bo_surface.png    – Tc surface in (U, V_SO) at optimal n
# =====================================================================

import sys, os, json, time, warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from skopt            import gp_minimize
from skopt.space      import Real
from skopt.plots      import plot_convergence

# ── Search bounds (all in units of t) ────────────────────────────────
U_LOW,   U_HIGH   =  75.0,  125.0
VSO_LOW, VSO_HIGH =  0.0,   1.0
N_LOW,   N_HIGH   =  1.7,   2.0

# ── BO settings ───────────────────────────────────────────────────────
N_CALLS          = 60    # total solver calls (increase for more accuracy)
N_INITIAL_POINTS = 10    # random exploration before GP kicks in
RANDOM_STATE     = 42

# ── Output paths ──────────────────────────────────────────────────────
os.makedirs('results', exist_ok=True)
os.makedirs('figures', exist_ok=True)
RESULTS_JSON    = 'results/bo_results.json'
FIG_CONVERGENCE = 'figures/bo_convergence.png'
FIG_SURFACE     = 'figures/bo_surface.png'


# ─────────────────────────────────────────────────────────────────────
# Core: run the existing solver for one (U, V_SO, n) point
# ─────────────────────────────────────────────────────────────────────

def _build_dispersions(VSO, Nk=80):
    """Build eps_fixed for a given V_SO (mirrors kgrid_u.py logic)."""
    t = 1.0
    kx = np.linspace(0, np.pi, Nk)
    ky = np.linspace(0, np.pi, Nk)
    KX, KY = np.meshgrid(kx, ky)

    sqrt_sin = np.sqrt(np.sin(KX)**2 + np.sin(KY)**2)
    cos_sum  = np.cos(KX) + np.cos(KY)

    eps = np.zeros((Nk, Nk, 2))
    eps[:, :, 0] = -2.0 * t * cos_sum - 2.0 * VSO * sqrt_sin
    eps[:, :, 1] = -2.0 * t * cos_sum + 2.0 * VSO * sqrt_sin
    return eps


def _build_term(U, VSO, Nk=80):
    """Build the interaction kernel (mirrors gap_term_u.py logic)."""
    t        = 1.0
    Delta_t  = 4.5 * t
    kx = np.linspace(0, np.pi, Nk)
    ky = np.linspace(0, np.pi, Nk)
    KX, KY = np.meshgrid(kx, ky)

    sqrt_sin   = np.sqrt(np.sin(KX)**2 + np.sin(KY)**2)
    s_k_factor = 0.5 * (np.cos(KX) + np.cos(KY))
    s_prime    = np.array([1.0, -1.0])

    term = (
        U
        + 8.0 * Delta_t * s_k_factor[..., None]
        + 4.0 * (Delta_t / t) * VSO
          * s_prime[None, None, :] * sqrt_sin[..., None]
    )
    return term


def evaluate_Tc(U, VSO, n):
    """
    Run the self-consistency solver for a single (U, V_SO, n) point.
    Returns Tc/t (float).
    """
    # Import here so the script works standalone without sys.path tricks
    from solvers_u import find_Tc

    eps  = _build_dispersions(VSO)
    term = _build_term(U, VSO)
    Tc, _, _, _ = find_Tc(n_fill=n, epsilon_ks=eps,
                           term_for_Delta0=term, verbose=False)
    return float(Tc)


# ─────────────────────────────────────────────────────────────────────
# Objective (skopt minimises, so we return –Tc)
# ─────────────────────────────────────────────────────────────────────

call_log = []   # stores every evaluation for later analysis

def objective(params):
    U, VSO, n = params
    t0 = time.time()
    Tc = evaluate_Tc(U, VSO, n)
    elapsed = time.time() - t0

    call_log.append({'U': U, 'VSO': VSO, 'n': n,
                     'Tc': Tc, 'time': elapsed})

    print(f"  [{len(call_log):>3d}]  U={U:6.3f}  V_SO={VSO:5.3f}"
          f"  n={n:5.4f}  →  Tc={Tc:.6f}   ({elapsed:.1f}s)")
    return -Tc   # minimise negative Tc


# ─────────────────────────────────────────────────────────────────────
# Plotting helpers
# ─────────────────────────────────────────────────────────────────────

def plot_convergence_curve(result):
    fig, ax = plt.subplots(figsize=(7, 4))
    iters = np.arange(1, len(result.func_vals) + 1)
    best  = np.maximum.accumulate(-result.func_vals)
    ax.plot(iters, best, 'o-', color='steelblue', lw=1.8, ms=4)
    ax.set_xlabel('Number of evaluations', fontsize=12)
    ax.set_ylabel('Best $T_c / t$ found', fontsize=12)
    ax.set_title('Bayesian Optimisation — Convergence', fontsize=13)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_CONVERGENCE, dpi=150)
    plt.close(fig)
    print(f'  ✓  Convergence figure → {FIG_CONVERGENCE}')


def plot_Tc_surface(opt_U, opt_VSO, opt_n):
    """
    Dense 2-D surface of Tc(U, V_SO) at the optimal n,
    evaluated on a coarse grid using the solver.
    """
    NU, NVSO = 20, 20
    U_grid   = np.linspace(U_LOW,   U_HIGH,   NU)
    VSO_grid = np.linspace(VSO_LOW, VSO_HIGH, NVSO)
    Tc_grid  = np.zeros((NVSO, NU))

    print(f'\n  Computing Tc surface at n = {opt_n:.4f} '
          f'({NU}×{NVSO} grid) …')

    from solvers_u import find_Tc

    for j, vso in enumerate(VSO_grid):
        eps = _build_dispersions(vso)
        for i, u in enumerate(U_grid):
            term = _build_term(u, vso)
            Tc, _, _, _ = find_Tc(opt_n, eps, term, verbose=False)
            Tc_grid[j, i] = Tc
        print(f'    V_SO={vso:.3f} done')

    fig, ax = plt.subplots(figsize=(7, 5))
    cf = ax.contourf(U_grid, VSO_grid, Tc_grid, levels=20, cmap='plasma')
    cb = fig.colorbar(cf, ax=ax)
    cb.set_label('$T_c / t$', fontsize=11)
    ax.plot(opt_U, opt_VSO, 'w*', ms=14, label=f'Optimum\n'
            f'U={opt_U:.2f}, V_SO={opt_VSO:.2f}\n'
            f'n={opt_n:.4f}, Tc={Tc_grid[np.argmin(np.abs(VSO_grid-opt_VSO)),np.argmin(np.abs(U_grid-opt_U))]:.4f}')
    ax.set_xlabel('$U / t$',   fontsize=12)
    ax.set_ylabel('$V_{SO}/t$', fontsize=12)
    ax.set_title(f'$T_c(U, V_{{SO}})$ at $n={opt_n:.4f}$', fontsize=13)
    ax.legend(fontsize=9, loc='upper right')
    fig.tight_layout()
    fig.savefig(FIG_SURFACE, dpi=150)
    plt.close(fig)
    print(f'  ✓  Surface figure → {FIG_SURFACE}')


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    print('=' * 65)
    print('  Bayesian Optimisation  —  maximise Tc(U, V_SO, n)')
    print('=' * 65)
    print(f'  Search space:')
    print(f'    U/t    ∈ [{U_LOW}, {U_HIGH}]')
    print(f'    V_SO/t ∈ [{VSO_LOW}, {VSO_HIGH}]')
    print(f'    n      ∈ [{N_LOW}, {N_HIGH}]')
    print(f'  Total calls : {N_CALLS}  '
          f'(random={N_INITIAL_POINTS}, BO={N_CALLS-N_INITIAL_POINTS})')
    print('─' * 65)

    space = [
        Real(U_LOW,   U_HIGH,   name='U'),
        Real(VSO_LOW, VSO_HIGH, name='V_SO'),
        Real(N_LOW,   N_HIGH,   name='n'),
    ]

    t_start = time.time()

    result = gp_minimize(
        func             = objective,
        dimensions       = space,
        n_calls          = N_CALLS,
        n_initial_points = N_INITIAL_POINTS,
        acq_func         = 'EI',          # Expected Improvement
        random_state     = RANDOM_STATE,
        noise            = 1e-6,
    )

    elapsed = time.time() - t_start

    # ── Best result ───────────────────────────────────────────────────
    best_U, best_VSO, best_n = result.x
    best_Tc = -result.fun

    print('\n' + '=' * 65)
    print('  OPTIMUM FOUND')
    print('=' * 65)
    print(f'  U/t    = {best_U:.4f}')
    print(f'  V_SO/t = {best_VSO:.4f}')
    print(f'  n      = {best_n:.4f}')
    print(f'  Tc/t   = {best_Tc:.6f}')
    print(f'  Total elapsed : {elapsed:.1f} s')
    print('=' * 65)

    # ── Save JSON ─────────────────────────────────────────────────────
    output = {
        'optimum': {'U': best_U, 'VSO': best_VSO,
                    'n': best_n, 'Tc': best_Tc},
        'search_bounds': {
            'U':   [U_LOW,   U_HIGH],
            'VSO': [VSO_LOW, VSO_HIGH],
            'n':   [N_LOW,   N_HIGH],
        },
        'n_calls': N_CALLS,
        'elapsed_s': elapsed,
        'call_history': call_log,
    }
    with open(RESULTS_JSON, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'\n  ✓  Results saved → {RESULTS_JSON}')

    # ── Figures ───────────────────────────────────────────────────────
    plot_convergence_curve(result)
    plot_Tc_surface(best_U, best_VSO, best_n)


if __name__ == '__main__':
    main()