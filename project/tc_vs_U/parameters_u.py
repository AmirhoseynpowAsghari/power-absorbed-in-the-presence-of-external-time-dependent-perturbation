# parameters_u.py
# =====================================================================
# All parameters for the Tc vs U scan.
#
# KEY DIFFERENCE from Tc-vs-VSO code:
#   - V_SO is FIXED, U is the scan variable
#   - k-grid is built ONCE (V_SO fixed → bands don't change)
#   - Only build_term(U) is rebuilt each iteration
# =====================================================================

import numpy as np
from pathlib import Path

# ── Physical parameters ───────────────────────────────────────────────
t              = 1.0
Delta_t_over_t = 4.5
Delta_t        = Delta_t_over_t * t

# ── Fixed external parameters ─────────────────────────────────────────
V_SO      = 0.4      # fixed spin-orbit coupling
n_filling = 1.8850   # fixed electron density

# ── U scan range ──────────────────────────────────────────────────────
U_min        = 75.0
U_max        = 125.0
N_U_points   = 50
U_values     = np.linspace(U_min, U_max, N_U_points)

# ── Numerical parameters ──────────────────────────────────────────────
Nk = 80

# ── Solver tolerances (identical to VSO code) ─────────────────────────
BISECTION_TOL      = 0.001
BISECTION_ITER     = 35
GAP_THRESHOLD_FRAC = 0.01
MIN_GAP_FOR_SC     = 1e-6

# ── Extended initial-guess grid (U is large → larger D0 guesses) ──────
D0_INIT  = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]   # wider than VSO code
DS_INIT  = [0.1, 0.5, 1.0, 5.0, 10.0]
DMU_INIT = [-2.0, -0.5, 0.0, 0.5, 2.0]

# ── Output paths ──────────────────────────────────────────────────────
RESULTS_DIR  = Path("results")
JSON_PATH    = RESULTS_DIR / "tc_vs_U.json"
NPZ_PATH     = RESULTS_DIR / "Tc_vs_U.npz"
FIGURES_DIR  = Path("figures")

# ── Metadata dict (written into every saved file) ─────────────────────
META = {
    't'              : t,
    'Delta_t_over_t' : Delta_t_over_t,
    'V_SO'           : V_SO,
    'n_filling'      : n_filling,
    'U_min'          : U_min,
    'U_max'          : U_max,
    'N_U_points'     : N_U_points,
    'Nk'             : Nk,
}