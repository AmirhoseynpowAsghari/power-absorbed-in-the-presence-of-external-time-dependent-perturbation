# README.md

```markdown
# Superconductivity with Rashba Spin-Orbit Coupling: 
# Tc Calculation and Ultrasonic Attenuation

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-orange)](https://numpy.org/)
[![Numba](https://img.shields.io/badge/Numba-0.57%2B-green)](https://numba.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Physical Model](#physical-model)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Module Descriptions](#module-descriptions)
- [Parameters](#parameters)
- [Output Files](#output-files)
- [Results](#results)
- [Dependencies](#dependencies)
- [License](#license)

---

## Overview

This project computes the **superconducting critical temperature (Tc)**
and **ultrasonic attenuation ratio (W/W_N)** for a two-dimensional
square-lattice superconductor with:

- **Rashba spin-orbit coupling (V_SO)**
- **On-site Hubbard interaction (U)**
- **Bond superconductivity (Delta_t)**
- **Fixed electron filling (n)**

The project is organized as a **two-stage pipeline**:

```
Stage 1: Tc Calculation
   ├── Scan over V_SO  → Tc(V_SO), Delta_eff(V_SO)
   └── Scan over U     → Tc(U),    Delta_eff(U)
            │
            │  results saved as JSON / NPZ
            ▼
Stage 2: Ultrasonic Attenuation
   ├── W/W_N vs T  for selected V_SO values
   ├── W/W_N vs V_SO at fixed T/Tc fractions
   ├── W/W_N vs T  for selected U values
   └── W/W_N vs U  at fixed T/Tc fractions
```

All intermediate results are saved as **JSON files** so each stage
can be re-run independently without repeating expensive calculations.

---

## Physical Model

### Hamiltonian

The system is described by a 2D square-lattice BCS Hamiltonian
with Rashba spin-orbit coupling:

```
H = sum_k  eps(k) c†_k c_k
  + sum_k  V_SO * g(k) * (c†_{k,up} c_{k,down} - h.c.)
  + U * sum_i n_{i,up} n_{i,down}
  + Delta_t * sum_<ij> (c†_{i,up} c†_{j,down} + h.c.)
```

### Single-Particle Dispersion

The Rashba SOC splits the band into two helicity branches:

```
eps_{k,±} = -2t(cos kx + cos ky) ∓ 2 V_SO |sin k|

where  |sin k| = sqrt(sin²kx + sin²ky)
```

### Gap Structure

The gap equation couples two order parameters:

```
Delta_ks = Delta0 - (DeltaS / 4t) * eps_ks
```

where:
- `Delta0`  — on-site pairing amplitude
- `DeltaS`  — bond pairing amplitude  
- `Delta_eff = <|Delta_ks|>_k` — the effective (renormalized) gap
  that enters the quasiparticle energy

```
E_ks = sqrt(Delta_ks² + xi_ks²),    xi_ks = eps_ks - mu
```

### Self-Consistency Equations

Three coupled equations are solved simultaneously:

```
r1: Delta0  + (1/2N) sum_k [ term(k) * Delta_ks * tanh(E_ks/2T) / (2E_ks) ] = 0
r2: DeltaS  + (1/2N) sum_k [ 8*Delta_t * Delta_ks * tanh(E_ks/2T) / (2E_ks) ] = 0
r3: (1/2N)  sum_k [ (xi_ks/E_ks) * tanh(E_ks/2T) ] - (1 - n) = 0
```

where `term(k) = U + 8*Delta_t*s_k + 4*(Delta_t/t)*V_SO*s'_±*|sin k|`

### Ultrasonic Attenuation

The absorption power ratio W/W_N is computed via:

```
W / W_N = [ integral g(E) g(E+hw) F(k) [f(E+hw) - f(E)] dE ]
          ─────────────────────────────────────────────────────
          [ same integral with Delta_eff = 0 ]
```

The coherence factor F(k) is:

```
F(k) = 1 + (|xi| |xi'|)/(E E') + eta * Delta²/(E E')

eta = +1  →  Case I  (phonon, charge)
eta = -1  →  Case II (spin fluctuations, magnetic)
```

---

## Project Structure

```
project/
│
├── sc_params/                    ← STAGE 1a: Tc vs V_SO
│   ├── parameters_tc.py          # U=75t, Delta_t=4.5t, n=1.885
│   ├── kgrid.py                  # k-grid, rebuilt per V_SO
│   ├── gap_equations.py          # self-consistency residual
│   ├── solvers.py                # T=0 finder + Tc bisection
│   ├── scanning_tc.py            # V_SO scan loop
│   ├── plotting_tc.py            # 3-panel figure
│   ├── io_utils_tc.py            # JSON + NPZ save/load
│   ├── main_tc.py                # entry point
│   └── results/
│       ├── tc_vs_vso.json        ← READ by ultrasonic VSO code
│       └── Tc_vs_VSO.npz
│
├── tc_vs_U/                      ← STAGE 1b: Tc vs U
│   ├── parameters_u.py           # V_SO=0.4t fixed, U scanned
│   ├── kgrid_u.py                # k-grid built ONCE (V_SO fixed)
│   ├── gap_term_u.py             # only term(U) rebuilt per iteration
│   ├── gap_equations_u.py        # same residual as sc_params/
│   ├── solvers_u.py              # wider D0 initial guess for large U
│   ├── scanning_u.py             # U scan loop
│   ├── plotting_u.py             # 3-panel figure
│   ├── io_utils_u.py             # JSON + NPZ save/load
│   ├── main_u.py                 # entry point
│   └── results/
│       ├── tc_vs_U.json          ← READ by ultrasonic U code
│       └── Tc_vs_U.npz
│
├── ultrasonic/                   ← STAGE 2a: W/W_N vs V_SO
│   ├── parameters_ua.py          # omega=0.7t, eta=+1, Nk=200
│   ├── sc_loader.py              # loads tc_vs_vso.json
│   ├── kgrid_ua.py               # 200×200 full BZ grid
│   ├── dos_ua.py                 # Numba DOS (rebuilt per V_SO)
│   ├── physics_ua.py             # Fermi, Delta(T), mu solver
│   ├── absorption.py             # W and W/W_N
│   ├── scanning_ua.py            # T sweep + V_SO scan
│   ├── plotting_ua.py            # 6-panel + W/W_N vs V_SO
│   ├── io_utils_ua.py            # JSON save/load
│   ├── main_ua.py                # entry point
│   └── results/
│       ├── temp_sweep_VSO_*.json
│       ├── temp_sweep_manifest.json
│       └── vso_scan.json
│
└── ultrasonic_U/                 ← STAGE 2b: W/W_N vs U
    ├── parameters_ua_u.py        # V_SO=0.4t fixed
    ├── sc_loader_u.py            # loads tc_vs_U.json
    ├── kgrid_ua_u.py             # bands built ONCE (V_SO fixed)
    ├── dos_ua_u.py               # DOS built ONCE (V_SO fixed)
    ├── physics_ua_u.py           # uses fixed band arrays
    ├── absorption_u.py           # W and W/W_N
    ├── scanning_ua_u.py          # T sweep + U scan
    ├── plotting_ua_u.py          # 6-panel + W/W_N vs U
    ├── io_utils_ua_u.py          # JSON save/load
    ├── main_ua_u.py              # entry point
    └── results/
        ├── temp_sweep_U_*.json
        ├── temp_sweep_manifest.json
        └── u_scan.json
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     STAGE 1: Tc Calculation                 │
│                                                             │
│  sc_params/main_tc.py                                       │
│      V_SO = 0 → 0.8  (50 points)                           │
│      Fixed: U=75t, Delta_t=4.5t, n=1.885                   │
│      Output: tc_vs_vso.json  ──────────────────────────┐   │
│                                                         │   │
│  tc_vs_U/main_u.py                                      │   │
│      U = 75t → 125t  (50 points)                        │   │
│      Fixed: V_SO=0.4t, Delta_t=4.5t, n=1.885           │   │
│      Output: tc_vs_U.json  ─────────────────────────┐  │   │
└─────────────────────────────────────────────────────│──│───┘
                                                      │  │
┌─────────────────────────────────────────────────────│──│───┐
│                  STAGE 2: Ultrasonic Attenuation    │  │   │
│                                                     │  │   │
│  ultrasonic/main_ua.py  ←───────────────────────────│──┘   │
│      Loads Tc(V_SO), Delta_eff(V_SO)                │      │
│      Computes W/W_N vs T and vs V_SO                │      │
│      Output: vso_scan.json, figures/                │      │
│                                                     │      │
│  ultrasonic_U/main_ua_u.py  ←───────────────────────┘      │
│      Loads Tc(U), Delta_eff(U)                             │
│      DOS built ONCE (V_SO fixed)                           │
│      Computes W/W_N vs T and vs U                          │
│      Output: u_scan.json, figures/                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/sc-rashba-ultrasonic.git
cd sc-rashba-ultrasonic
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Quick Start

### Run the full pipeline in order:

```bash
# Stage 1a: compute Tc vs V_SO
cd sc_params
python main_tc.py

# Stage 1b: compute Tc vs U  (fixed V_SO = 0.4t)
cd ../tc_vs_U
python main_u.py

# Stage 2a: compute W/W_N vs V_SO
cd ../ultrasonic
python main_ua.py

# Stage 2b: compute W/W_N vs U
cd ../ultrasonic_U
python main_ua_u.py
```

### Skip recomputation (load saved JSON and plot only):

```python
# In any main_*.py, change the flag:
results = main(recompute=False)
```

### Point to a custom SC params file:

```python
# Use U-scan results as input to the ultrasonic code:
results, u_results = main(
    recompute=True,
    sc_json="../tc_vs_U/results/tc_vs_U.json"
)
```

---

## Module Descriptions

### Stage 1 — Tc Calculation (shared logic)

| Module | Description |
|--------|-------------|
| `parameters_*.py` | All physical and numerical constants. Single source of truth. |
| `kgrid*.py` | Builds the k-space mesh and helicity band dispersions. |
| `gap_equations*.py` | Three-component self-consistency residual `[r1, r2, r3]`. |
| `solvers*.py` | T=0 grid search + bisection Tc finder with warm starting. |
| `scanning*.py` | Outer loop over the scan variable (V_SO or U). |
| `plotting*.py` | Three-panel figures: Tc, Delta_eff, BCS ratio. |
| `io_utils*.py` | JSON and NPZ save/load with numpy array handling. |
| `main*.py` | Entry point with `recompute=True/False` toggle. |

### Stage 2 — Ultrasonic Attenuation

| Module | Description |
|--------|-------------|
| `sc_loader*.py` | Loads Tc and Delta_eff from Stage 1 JSON output. Fallback chain: JSON → NPZ → hardcoded dict. |
| `kgrid_ua*.py` | 200×200 full BZ grid `[-π,π]×[-π,π]`. |
| `dos_ua*.py` | Numba-parallel Gaussian-broadened DOS. Built once per V_SO (VSO scan) or once total (U scan). |
| `physics_ua*.py` | Fermi-Dirac, BCS gap Delta(T), self-consistent mu(T). |
| `absorption*.py` | Computes W and W_N with BCS coherence factor. |
| `scanning_ua*.py` | Temperature sweep and parameter scan loops. |
| `plotting_ua*.py` | Six-panel detail figure + single-panel W/W_N vs parameter. |
| `io_utils_ua*.py` | JSON save/load with per-VSO or per-U manifest files. |
| `main_ua*.py` | Entry point. Assigns `active_fracs` before use (avoids `UnboundLocalError`). |

---

## Parameters

### Physical Parameters

| Symbol | Value | Description |
|--------|-------|-------------|
| `t` | 1.0 | Hopping amplitude (energy unit) |
| `U` | 75t | On-site Hubbard interaction (Stage 1b scan: 75t → 125t) |
| `Delta_t` | 4.5t | Bond superconductivity amplitude |
| `V_SO` | 0.0 → 0.8t | Rashba spin-orbit coupling (Stage 1a scan) |
| `n` | 1.885 | Electron filling per site |
| `eta` | +1 | Coherence factor sign (+1: phonon, -1: magnetic) |
| `ℏω` | 0.7t | Phonon energy for ultrasonic probe |

### Numerical Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `Nk` (Tc) | 80 | k-grid points per dimension for Tc calculation |
| `Nk` (UA) | 200 | k-grid points per dimension for ultrasonic calculation |
| `NE` | 500 | Energy grid points for DOS integration |
| `sigma` | 0.05 | Gaussian broadening for DOS |
| `T_SCAN_POINTS` | 2000 | Temperature grid points for T sweep |
| `N_VSO_points` | 50 | Number of V_SO scan points |
| `N_U_points` | 50 | Number of U scan points |
| `BISECTION_ITER` | 35 | Maximum bisection steps for Tc finder |

---

## Output Files

### Stage 1 (Tc Calculation)

```
sc_params/results/
├── tc_vs_vso.json          # Tc, Delta_eff, ratio vs V_SO
└── Tc_vs_VSO.npz           # same data in compressed numpy format

tc_vs_U/results/
├── tc_vs_U.json            # Tc, Delta_eff, ratio vs U
└── Tc_vs_U.npz
```

### Stage 2 (Ultrasonic Attenuation)

```
ultrasonic/results/
├── temp_sweep_manifest.json        # index of per-VSO files
├── temp_sweep_VSO_0.0000.json      # T, Delta, mu, W, WN, ratio vs T
├── temp_sweep_VSO_0.4082.json
├── temp_sweep_VSO_0.8000.json
└── vso_scan.json                   # W/W_N vs V_SO at fixed T/Tc

ultrasonic_U/results/
├── temp_sweep_manifest.json
├── temp_sweep_U_75.00.json
├── temp_sweep_U_100.51.json
├── temp_sweep_U_125.00.json
└── u_scan.json                     # W/W_N vs U at fixed T/Tc
```

### Figures

```
sc_params/figures/
└── Tc_vs_VSO.png           # Tc, Delta_eff, BCS ratio vs V_SO

tc_vs_U/figures/
└── Tc_vs_U.png             # Tc, Delta_eff, BCS ratio vs U

ultrasonic/figures/
├── W_WN_temperature_sweep.png    # 6-panel: W/W_N, Delta, mu vs T
└── W_WN_vs_VSO.png              # W/W_N vs V_SO at T/Tc = 0.3,0.5,0.7,0.9

ultrasonic_U/figures/
├── W_WN_U_temperature_sweep.png  # 6-panel: W/W_N, Delta, mu vs T
└── W_WN_vs_U.png                # W/W_N vs U at T/Tc = 0.3,0.5,0.7,0.9
```

---

## Results

### Tc vs V_SO (fixed U = 75t, n = 1.885)

- Tc **increases monotonically** with V_SO
- Delta_eff increases with V_SO
- BCS ratio 2*Delta_eff / kB*Tc decreases slightly with V_SO
  (approaches the weak-coupling BCS value 3.528)

### Tc vs U (fixed V_SO = 0.4t, n = 1.885)

- Tc **decreases** as U increases (stronger repulsion suppresses SC)
- Delta_eff decreases with U
- BCS ratio **increases** above 3.528 at large U
  (strong-coupling / non-BCS regime)

### W/W_N vs T

- W/W_N = 1 for T > Tc (normal state)
- W/W_N drops below 1 for T < Tc (pair-breaking suppressed)
- No coherence peak (eta = +1, phonon case)
- Pair-breaking threshold: W = 0 at T = 0 when ℏω < 2*Delta_eff

### W/W_N vs V_SO

- At fixed T/Tc, W/W_N shows **non-monotonic** behavior vs V_SO
- Larger SOC changes the coherence factor structure

### W/W_N vs U

- W/W_N decreases as U increases at fixed T/Tc
- Larger U → larger BCS ratio → stronger pair-breaking threshold

---

## Dependencies

```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
numba>=0.57
```

Install with:

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
numba>=0.57
```

---

## License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for details.

---

## Citation

If you use this code in your research, please cite:

```bibtex
@software{sc_rashba_ultrasonic,
  author    = {Your Name},
  title     = {Superconductivity with Rashba Spin-Orbit Coupling:
               Tc Calculation and Ultrasonic Attenuation},
  year      = {2024},
  publisher = {GitHub},
  url       = {https://github.com/yourusername/sc-rashba-ultrasonic}
}
```

---

## Contact

For questions or issues, please open a GitHub issue or contact:
**your.email@university.edu**
```

---

## `requirements.txt`

```
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
numba>=0.57
```

---

## `LICENSE`

```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
