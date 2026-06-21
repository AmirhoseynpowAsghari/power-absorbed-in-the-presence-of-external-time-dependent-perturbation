# sc_loader.py
# =====================================================================
# Load SC parameters (Tc, Delta_eff) from the Tc-vs-VSO output.
#
# This replaces the hardcoded SC_params dict in the original code.
# It can read from:
#   1. JSON saved by io_utils_tc.save_json()   ← preferred
#   2. NPZ  saved by io_utils_tc.save_npz()    ← fallback
#   3. Hardcoded fallback dict                 ← last resort
# =====================================================================

import json
import numpy as np
from pathlib import Path

from parameters_ua import SC_PARAMS_JSON, SC_PARAMS_NPZ


# ── Internal: build the SC_params dict from arrays ────────────────────
def _build_sc_dict(V_SO_arr, Tc_arr, Deff_arr, ratio_arr=None):
    """
    Convert parallel arrays → nested dict matching the original format:
        { vso: {'Tc': ..., 'Delta0': ..., 'ratio_2D_kTc': ...} }

    'Delta0' here stores Delta_eff (the effective gap), consistent with
    how the ultrasonic code uses it.
    """
    sc = {}
    for i, vso in enumerate(V_SO_arr):
        key = round(float(vso), 4)
        sc[key] = {
            'Tc'           : float(Tc_arr[i]),
            'Delta0'       : float(Deff_arr[i]),   # Deff stored as Delta0
            'ratio_2D_kTc' : float(ratio_arr[i]) if ratio_arr is not None
                             else float(2 * Deff_arr[i] / Tc_arr[i])
                             if Tc_arr[i] > 1e-8 else 0.0,
        }
    return sc


# ── Load from JSON ─────────────────────────────────────────────────────
def _load_from_json(path):
    path = Path(path)
    with path.open() as f:
        payload = json.load(f)

    res      = payload.get('results', payload)   # handle both formats
    V_SO_arr = np.array(res['V_SO'])
    Tc_arr   = np.array(res['Tc'])
    Deff_arr = np.array(res['Deff_T0'])
    ratio    = np.array(res.get('ratio', []))

    return _build_sc_dict(V_SO_arr, Tc_arr, Deff_arr,
                          ratio if len(ratio) else None)


# ── Load from NPZ ──────────────────────────────────────────────────────
def _load_from_npz(path):
    path = Path(path)
    data = np.load(path)
    V_SO_arr = data['V_SO']
    Tc_arr   = data['Tc']
    Deff_arr = data['Delta_eff_T0']
    return _build_sc_dict(V_SO_arr, Tc_arr, Deff_arr)


# ── Hardcoded fallback (original SC_params from monolithic code) ───────
def _hardcoded_fallback():
    """
    Return the original hardcoded SC_params dict.
    Used only if neither JSON nor NPZ file is found.
    """
    print("  [sc_loader] WARNING: using hardcoded SC_params fallback.")
    return {
        0.0000: {'Tc': 0.500917, 'Delta0': 0.627212, 'ratio_2D_kTc': 2.504},
        0.0163: {'Tc': 0.501061, 'Delta0': 0.627393, 'ratio_2D_kTc': 2.504},
        0.0327: {'Tc': 0.501501, 'Delta0': 0.627944, 'ratio_2D_kTc': 2.504},
        0.0490: {'Tc': 0.502229, 'Delta0': 0.628855, 'ratio_2D_kTc': 2.504},
        0.0653: {'Tc': 0.503776, 'Delta0': 0.630134, 'ratio_2D_kTc': 2.502},
        0.0816: {'Tc': 0.505622, 'Delta0': 0.631782, 'ratio_2D_kTc': 2.499},
        0.0980: {'Tc': 0.507761, 'Delta0': 0.633794, 'ratio_2D_kTc': 2.496},
        0.1143: {'Tc': 0.510202, 'Delta0': 0.636178, 'ratio_2D_kTc': 2.494},
        0.1306: {'Tc': 0.512942, 'Delta0': 0.638929, 'ratio_2D_kTc': 2.491},
        0.1469: {'Tc': 0.516521, 'Delta0': 0.642052, 'ratio_2D_kTc': 2.486},
        0.1633: {'Tc': 0.519871, 'Delta0': 0.645546, 'ratio_2D_kTc': 2.483},
        0.1796: {'Tc': 0.524076, 'Delta0': 0.649421, 'ratio_2D_kTc': 2.478},
        0.1959: {'Tc': 0.528589, 'Delta0': 0.653661, 'ratio_2D_kTc': 2.473},
        0.2122: {'Tc': 0.533434, 'Delta0': 0.658293, 'ratio_2D_kTc': 2.468},
        0.2286: {'Tc': 0.538593, 'Delta0': 0.663292, 'ratio_2D_kTc': 2.463},
        0.2449: {'Tc': 0.544088, 'Delta0': 0.668685, 'ratio_2D_kTc': 2.458},
        0.2612: {'Tc': 0.549908, 'Delta0': 0.674453, 'ratio_2D_kTc': 2.453},
        0.2776: {'Tc': 0.556634, 'Delta0': 0.680611, 'ratio_2D_kTc': 2.445},
        0.2939: {'Tc': 0.563134, 'Delta0': 0.687156, 'ratio_2D_kTc': 2.440},
        0.3102: {'Tc': 0.570561, 'Delta0': 0.694097, 'ratio_2D_kTc': 2.433},
        0.3265: {'Tc': 0.577753, 'Delta0': 0.701422, 'ratio_2D_kTc': 2.428},
        0.3429: {'Tc': 0.585895, 'Delta0': 0.709150, 'ratio_2D_kTc': 2.421},
        0.3592: {'Tc': 0.594397, 'Delta0': 0.717265, 'ratio_2D_kTc': 2.413},
        0.3755: {'Tc': 0.602673, 'Delta0': 0.725790, 'ratio_2D_kTc': 2.409},
        0.3918: {'Tc': 0.611916, 'Delta0': 0.734704, 'ratio_2D_kTc': 2.401},
        0.4082: {'Tc': 0.621541, 'Delta0': 0.744024, 'ratio_2D_kTc': 2.394},
        0.4245: {'Tc': 0.630928, 'Delta0': 0.753754, 'ratio_2D_kTc': 2.389},
        0.4408: {'Tc': 0.641308, 'Delta0': 0.763868, 'ratio_2D_kTc': 2.382},
        0.4571: {'Tc': 0.652098, 'Delta0': 0.774409, 'ratio_2D_kTc': 2.375},
        0.4735: {'Tc': 0.662624, 'Delta0': 0.785352, 'ratio_2D_kTc': 2.370},
        0.4898: {'Tc': 0.674186, 'Delta0': 0.796691, 'ratio_2D_kTc': 2.363},
        0.5061: {'Tc': 0.685492, 'Delta0': 0.808456, 'ratio_2D_kTc': 2.359},
        0.5224: {'Tc': 0.697865, 'Delta0': 0.820624, 'ratio_2D_kTc': 2.352},
        0.5388: {'Tc': 0.709951, 'Delta0': 0.833200, 'ratio_2D_kTc': 2.347},
        0.5551: {'Tc': 0.723145, 'Delta0': 0.846197, 'ratio_2D_kTc': 2.340},
        0.5714: {'Tc': 0.736040, 'Delta0': 0.859606, 'ratio_2D_kTc': 2.336},
        0.5878: {'Tc': 0.749332, 'Delta0': 0.873426, 'ratio_2D_kTc': 2.331},
        0.6041: {'Tc': 0.763037, 'Delta0': 0.887673, 'ratio_2D_kTc': 2.327},
        0.6204: {'Tc': 0.777151, 'Delta0': 0.902340, 'ratio_2D_kTc': 2.322},
        0.6367: {'Tc': 0.791682, 'Delta0': 0.917432, 'ratio_2D_kTc': 2.318},
        0.6531: {'Tc': 0.806638, 'Delta0': 0.932959, 'ratio_2D_kTc': 2.313},
        0.6694: {'Tc': 0.821229, 'Delta0': 0.948918, 'ratio_2D_kTc': 2.311},
        0.6857: {'Tc': 0.837057, 'Delta0': 0.965345, 'ratio_2D_kTc': 2.307},
        0.7020: {'Tc': 0.852539, 'Delta0': 0.982253, 'ratio_2D_kTc': 2.304},
        0.7184: {'Tc': 0.868478, 'Delta0': 0.999656, 'ratio_2D_kTc': 2.302},
        0.7347: {'Tc': 0.884858, 'Delta0': 1.017532, 'ratio_2D_kTc': 2.300},
        0.7510: {'Tc': 0.901637, 'Delta0': 1.035832, 'ratio_2D_kTc': 2.298},
        0.7673: {'Tc': 0.918852, 'Delta0': 1.054597, 'ratio_2D_kTc': 2.295},
        0.7837: {'Tc': 0.936467, 'Delta0': 1.073786, 'ratio_2D_kTc': 2.293},
        0.8000: {'Tc': 0.953553, 'Delta0': 1.093377, 'ratio_2D_kTc': 2.293},
    }


# ── Public API ─────────────────────────────────────────────────────────
def load_sc_params(json_path=None, npz_path=None, verbose=True):
    """
    Load SC parameters with automatic fallback chain:
        JSON  →  NPZ  →  hardcoded dict

    Parameters
    ----------
    json_path : str or Path, optional – override default JSON path
    npz_path  : str or Path, optional – override default NPZ path
    verbose   : bool

    Returns
    -------
    sc_params : dict  { vso_float: {'Tc', 'Delta0', 'ratio_2D_kTc'} }
    source    : str   – which source was used
    """
    json_path = Path(json_path) if json_path else SC_PARAMS_JSON
    npz_path  = Path(npz_path)  if npz_path  else SC_PARAMS_NPZ

    # ── Try JSON first ────────────────────────────────────────────────
    if json_path.exists():
        try:
            sc = _load_from_json(json_path)
            if verbose:
                print(f"  [sc_loader] SC params loaded from JSON: {json_path}")
                print(f"             {len(sc)} V_SO points found.")
            return sc, 'json'
        except Exception as e:
            if verbose:
                print(f"  [sc_loader] JSON load failed ({e}), trying NPZ …")

    # ── Try NPZ ───────────────────────────────────────────────────────
    if npz_path.exists():
        try:
            sc = _load_from_npz(npz_path)
            if verbose:
                print(f"  [sc_loader] SC params loaded from NPZ: {npz_path}")
                print(f"             {len(sc)} V_SO points found.")
            return sc, 'npz'
        except Exception as e:
            if verbose:
                print(f"  [sc_loader] NPZ load failed ({e}), using fallback …")

    # ── Hardcoded fallback ────────────────────────────────────────────
    sc = _hardcoded_fallback()
    return sc, 'hardcoded'


def get_sc_params(vso, sc_params):
    """
    Return (Tc, Delta0) for a given V_SO from the loaded sc_params dict.

    Parameters
    ----------
    vso       : float
    sc_params : dict – output of load_sc_params()

    Returns
    -------
    (Tc, Delta0) : (float, float)
    """
    key = round(float(vso), 4)
    if key in sc_params:
        return sc_params[key]['Tc'], sc_params[key]['Delta0']
    raise ValueError(
        f"V_SO = {vso} not found in SC params. "
        f"Available: {sorted(sc_params.keys())}"
    )