# parameters_tc.py
# =====================================================================
# Parameters matching:  U/t = +75,  Delta_t/t = 4.5,  n = 1.885
# =====================================================================

import numpy as np

# ── Physical parameters ───────────────────────────────────────────────
t              = 1.0
U_over_t       = 145.0          # ← was -1.0 in the first modular version
Delta_t_over_t = 4.5           # ← was  0.0 in the first modular version

U       = U_over_t * t         #  75.0
Delta_t = Delta_t_over_t * t   #   4.5

# ── Numerical parameters ──────────────────────────────────────────────
Nk           = 80
n_filling    = 1.8850          # ← was 0.80 in the first modular version
N_VSO_points = 50
VSO_min      = 0.0
VSO_max      = 0.8

V_SO_values  = np.linspace(VSO_min, VSO_max, N_VSO_points)

# ── Solver tolerances (identical to monolithic code) ──────────────────
BISECTION_TOL      = 0.001
BISECTION_ITER     = 35
GAP_THRESHOLD_FRAC = 0.01
MIN_GAP_FOR_SC     = 1e-6

# ── Metadata for JSON headers ─────────────────────────────────────────
META = {
    't'              : t,
    'U_over_t'       : U_over_t,
    'Delta_t_over_t' : Delta_t_over_t,
    'n_filling'      : n_filling,
    'Nk'             : Nk,
    'VSO_min'        : VSO_min,
    'VSO_max'        : VSO_max,
    'N_VSO_points'   : N_VSO_points,
}