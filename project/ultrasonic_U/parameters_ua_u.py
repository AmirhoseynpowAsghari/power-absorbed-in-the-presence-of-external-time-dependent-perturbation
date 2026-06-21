# parameters_ua_u.py
# =====================================================================
# All parameters for the ultrasonic attenuation U-scan.
#
# KEY DIFFERENCE from the VSO-scan ultrasonic code:
#   - V_SO is FIXED  → eps_plus, eps_minus, and gE_table built ONCE
#   - U   is scanned → only Tc and Delta_eff change per iteration
#   - SC_params come from tc_vs_U/results/tc_vs_U.json
# =====================================================================

import numpy as np
from pathlib import Path

# ── Physical constants ────────────────────────────────────────────────
t     = 1.0
eta   = 1.0    # coherence factor sign: +1 (Case I) or -1 (Case II)
B     = 1.0
hbar  = 1.0
omega = 0.7    # phonon energy ℏω
kB    = 1.0

# ── Target density and fixed V_SO ─────────────────────────────────────
n_target = 1.8850
V_SO     = 0.40    # fixed for the entire U scan

# ── DOS broadening ────────────────────────────────────────────────────
sigma = 0.05

# ── k-grid (200 × 200, full BZ) ───────────────────────────────────────
Nk_ua = 200

# ── Energy grid ───────────────────────────────────────────────────────
NE         = 500
E_grid_min = -6.0
E_grid_max =  6.0

# ── Temperature sweep settings ────────────────────────────────────────
T_SCAN_POINTS   = 2000
T_SCAN_OVERHEAD = 1.4   # T_max = overhead * max(Tc over U_list)

# ── U values for the 6-panel detail figure (first, middle, last) ──────
# Set to None to auto-select from loaded SC_params
U_DETAIL_LIST = None   # e.g. [75.0, 100.51, 125.0]

# ── Fixed T/Tc fractions for the W/W_N vs U scan ─────────────────────
T_FRACS_DEFAULT = (0.3, 0.5, 0.7, 0.9)

# ── Paths ─────────────────────────────────────────────────────────────
# Where to find tc_vs_U results from the previous modular code
SC_PARAMS_JSON = Path("../tc_vs_U/results/tc_vs_U.json")
SC_PARAMS_NPZ  = Path("../tc_vs_U/results/Tc_vs_U.npz")

# Where to save ultrasonic U-scan results
UA_U_RESULTS_DIR = Path("results")
FIGURES_DIR      = Path("figures")