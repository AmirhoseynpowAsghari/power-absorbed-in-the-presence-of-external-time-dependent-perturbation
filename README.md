
# Power Absorbed in the Presence of an External Time-Dependent Perturbation

Numerical study of **BCS superconductivity with Rashba spin-orbit coupling** on a 2D square-lattice tight-binding model, and the resulting **ultrasonic attenuation** (power absorbed from a time-dependent acoustic perturbation) in the superconducting state.

The project is organized as four self-contained pipeline stages, each in its own folder under `project/`. Each stage loads its input from the JSON/NPZ results produced by the previous stage, so they must be run in order the first time.

```
project/
├── sc_params/      # Stage 1: Tc and gap vs spin-orbit coupling V_SO  (U fixed)
├── ultrasonic/      # Stage 2: ultrasonic attenuation W/W_N vs V_SO and T (uses sc_params output)
├── tc_vs_U/         # Stage 3: Tc and gap vs interaction strength U     (V_SO fixed)
└── ultrasonic_U/    # Stage 4: ultrasonic attenuation W/W_N vs U and T  (uses tc_vs_U output)
```

## Physical model

Electrons on a 2D square lattice with nearest-neighbor hopping `t`, an on-site/extended pairing interaction `U`, a `d`-wave–like pairing channel set by `Δ_t`, and Rashba spin-orbit coupling `V_SO` split the band into two helicity branches:

```
ε±(k) = -2t (cos kx + cos ky)  ∓  2 V_SO |sin k|
```

The superconducting state is solved self-consistently for three coupled equations (gap `Δ0`, anisotropic component `ΔS`, chemical potential `μ`) given a fixed electron filling `n`, producing a momentum-resolved gap

```
Δ_k = Δ0 - (ΔS / 4t) · ε_k
```

and a spin-orbit–renormalized effective gap `Δ_eff(0) = ⟨|Δ_k|⟩_k`, which is the gap magnitude actually used downstream (not the bare `Δ0`) when computing ultrasonic attenuation.

The ultrasonic absorption ratio `W/W_N` (superconducting vs normal-state absorbed power) is computed from a BCS coherence-factor integral over the quasiparticle density of states, for a phonon of energy `ℏω`, as a function of temperature and either `V_SO` or `U`.

## Pipeline / module breakdown

### 1. `sc_params/` — Tc and gap vs V_SO
- **Fixed:** `U/t = 75`, `Δ_t/t = 4.5`, `n = 1.885`
- **Scanned:** `V_SO` from 0 to 0.8 (50 points)
- Solves the gap equations (`gap_equations.py`) on an 80×80 k-grid (`kgrid.py`) via bisection in temperature to find `Tc` (`solvers.py`)
- Entry point: `main_tc.py` → saves `results/tc_vs_vso.json`, `results/Tc_vs_VSO.npz`, and `figures/Tc_vs_VSO.png`

### 2. `ultrasonic/` — Ultrasonic attenuation vs V_SO
- Loads `Tc(V_SO)` and `Δ_eff(V_SO)` from `sc_params/results/` via `sc_loader.py`
- Computes the density of states (`dos_ua.py`), the temperature-dependent gap `Δ(T)` and chemical potential (`physics_ua.py`), and the absorption ratio `W/W_N` (`absorption.py`)
- Produces two outputs via `main_ua.py`:
  - A detailed temperature sweep at three representative `V_SO` values (0, 0.408, 0.8)
  - A scan of `W/W_N` vs `V_SO` at fixed `T/Tc` fractions (0.3, 0.5, 0.7, 0.9)
- Outputs: `figures/W_WN_temperature_sweep.png`, `figures/W_WN_vs_VSO.png`

### 3. `tc_vs_U/` — Tc and gap vs U
- **Fixed:** `V_SO/t = 0.4`, `Δ_t/t = 4.5`, `n = 1.885`
- **Scanned:** `U` from 75 to 125 (50 points)
- Same self-consistency machinery as `sc_params/`, but the k-space dispersions are built once (`V_SO` fixed) and only the pairing kernel (`gap_term_u.py`) is rebuilt per `U`
- Entry point: `main_u.py` → saves `results/tc_vs_U.json`, `results/Tc_vs_U.npz`, and `figures/Tc_vs_U.png`

### 4. `ultrasonic_U/` — Ultrasonic attenuation vs U
- Mirrors `ultrasonic/`, but loads `Tc(U)` / `Δ_eff(U)` from `tc_vs_U/results/` instead, with `V_SO` held fixed at 0.4
- Entry point: `main_ua_u.py` → saves `figures/W_WN_U_temperature_sweep.png`, `figures/W_WN_vs_U.png`

> **Note on sign convention:** `parameters_tc.py` and `parameters_u.py` define `U` as a positive number (`U/t = 75`), while the generated figure titles label it `U = -75t`. The pairing interaction is treated as attractive in the gap equations regardless of the stored sign of the constant; results (finite, well-behaved `Tc` across the whole scan range) are consistent with attractive pairing. Keep this in mind if you modify `U_over_t`/`U_min`/`U_max`.

## Repository layout

```
project/
├── sc_params/
│   ├── parameters_tc.py     # physical & numerical parameters, V_SO scan range
│   ├── kgrid.py              # k-space grid, band dispersions, pairing kernel
│   ├── gap_equations.py      # self-consistency residuals, effective gap
│   ├── solvers.py            # Tc bisection solver
│   ├── scanning_tc.py        # V_SO scan loop
│   ├── plotting_tc.py        # Tc/gap/BCS-ratio figure
│   ├── io_utils_tc.py        # JSON/NPZ save & load
│   ├── main_tc.py            # entry point
│   ├── figures/               # Tc_vs_VSO.png
│   └── results/               # tc_vs_vso.json, Tc_vs_VSO.npz
│
├── ultrasonic/
│   ├── parameters_ua.py      # ultrasonic-specific constants, paths to sc_params output
│   ├── kgrid_ua.py           # finer (200×200) k-grid for DOS
│   ├── dos_ua.py              # density-of-states computation
│   ├── physics_ua.py          # Fermi function, BCS Δ(T), μ(T)
│   ├── absorption.py          # W(T) and W/W_N
│   ├── sc_loader.py            # loads Tc/Δ_eff from sc_params results
│   ├── scanning_ua.py          # temperature sweep + V_SO scan
│   ├── plotting_ua.py          # figures
│   ├── io_utils_ua.py          # JSON save & load
│   ├── main_ua.py              # entry point
│   ├── figures/                 # W_WN_temperature_sweep.png, W_WN_vs_VSO.png
│   └── results/                 # per-V_SO temperature sweeps, vso_scan.json
│
├── tc_vs_U/                     # analogous to sc_params/, scanning U instead of V_SO
│   └── ... (parameters_u.py, kgrid_u.py, gap_equations_u.py, gap_term_u.py,
│            solvers_u.py, scanning_u.py, plotting_u.py, io_utils_u.py, main_u.py)
│
└── ultrasonic_U/                # analogous to ultrasonic/, scanning U instead of V_SO
    └── ... (parameters_ua_u.py, kgrid_ua_u.py, dos_ua_u.py, physics_ua_u.py,
             absorption_u.py, sc_loader_u.py, scanning_ua_u.py, plotting_ua_u.py,
             io_utils_ua_u.py, main_ua_u.py)
```

## Requirements

- Python 3.9+
- `numpy`
- `scipy`
- `matplotlib`
- `numba`

Install with:

```bash
pip install numpy scipy matplotlib numba
```

## Usage

Run the four stages **in order**, since each `ultrasonic*` stage reads the JSON/NPZ results written by its corresponding `Tc` stage.

```bash
# Stage 1: Tc and gap vs V_SO
cd project/sc_params
python main_tc.py

# Stage 2: ultrasonic attenuation vs V_SO (reads ../sc_params/results/)
cd ../ultrasonic
python main_ua.py

# Stage 3: Tc and gap vs U
cd ../tc_vs_U
python main_u.py

# Stage 4: ultrasonic attenuation vs U (reads ../tc_vs_U/results/)
cd ../ultrasonic_U
python main_ua_u.py
```

Each `main_*.py` accepts a `recompute` flag (`True` by default): set it to `False` in the script (or when calling `main()` interactively) to skip the physics solve and simply re-plot from previously saved results.

## Outputs

| Stage | Figure | Description |
|---|---|---|
| `sc_params` | `Tc_vs_VSO.png` | `Tc`, zero-temperature `Δ_eff`, and BCS ratio `2Δ/k_BTc` vs `V_SO` |
| `ultrasonic` | `W_WN_temperature_sweep.png` | `W/W_N`, gap, and `μ` vs temperature at three `V_SO` values |
| `ultrasonic` | `W_WN_vs_VSO.png` | `W/W_N` vs `V_SO` at fixed `T/Tc` fractions |
| `tc_vs_U` | `Tc_vs_U.png` | `Tc`, zero-temperature `Δ_eff`, and BCS ratio vs `U` |
| `ultrasonic_U` | `W_WN_U_temperature_sweep.png` | `W/W_N`, gap, and `μ` vs temperature at three `U` values |
| `ultrasonic_U` | `W_WN_vs_U.png` | `W/W_N` vs `U` at fixed `T/Tc` fractions |

## License

No license file is currently included in this repository.