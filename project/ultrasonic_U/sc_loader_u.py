# sc_loader_u.py
# =====================================================================
# Load SC parameters (Tc, Delta_eff) from tc_vs_U output.
#
# Fallback chain:
#   1. JSON saved by tc_vs_U/io_utils_u.py   ← preferred
#   2. NPZ  saved by tc_vs_U/io_utils_u.py   ← fallback
#   3. Hardcoded dict                         ← last resort
#
# The dict returned has the format:
#   { U_float: {'Tc': ..., 'Delta0': ..., 'ratio_2D_kTc': ...} }
# =====================================================================

import json
import numpy as np
from pathlib import Path

from parameters_ua_u import SC_PARAMS_JSON, SC_PARAMS_NPZ


# ── Internal builder ──────────────────────────────────────────────────
def _build_sc_dict(U_arr, Tc_arr, Deff_arr, ratio_arr=None):
    """
    Convert parallel arrays → nested dict:
        { U_float: {'Tc': ..., 'Delta0': ..., 'ratio_2D_kTc': ...} }

    'Delta0' stores Delta_eff (the effective gap), matching how the
    ultrasonic W calculation uses it.
    """
    sc = {}
    for i, U in enumerate(U_arr):
        key = round(float(U), 2)
        Tc  = float(Tc_arr[i])
        D   = float(Deff_arr[i])
        r   = (float(ratio_arr[i]) if ratio_arr is not None
               else (2.0 * D / Tc if Tc > 1e-8 else 0.0))
        sc[key] = {'Tc': Tc, 'Delta0': D, 'ratio_2D_kTc': r}
    return sc


# ── JSON loader ───────────────────────────────────────────────────────
def _load_from_json(path):
    path = Path(path)
    with path.open() as f:
        payload = json.load(f)

    # Handle both {'results': {...}} and flat formats
    res      = payload.get('results', payload)
    U_arr    = np.array(res['U'])
    Tc_arr   = np.array(res['Tc'])
    Deff_arr = np.array(res['Deff_T0'])
    ratio    = np.array(res.get('ratio', []))

    return _build_sc_dict(U_arr, Tc_arr, Deff_arr,
                          ratio if len(ratio) else None)


# ── NPZ loader ────────────────────────────────────────────────────────
def _load_from_npz(path):
    path = Path(path)
    data = np.load(path)
    return _build_sc_dict(
        data['U'],
        data['Tc'],
        data['Delta_eff_T0'],
    )


# ── Hardcoded fallback ────────────────────────────────────────────────
def _hardcoded_fallback():
    print("  [sc_loader_u] WARNING: using hardcoded SC_params fallback.")
    return {
        75.00:  {'Tc': 0.616369, 'Delta0': 0.739310, 'ratio_2D_kTc': 2.399},
        76.02:  {'Tc': 0.602142, 'Delta0': 0.728079, 'ratio_2D_kTc': 2.418},
        77.04:  {'Tc': 0.587607, 'Delta0': 0.717019, 'ratio_2D_kTc': 2.440},
        78.06:  {'Tc': 0.573962, 'Delta0': 0.706123, 'ratio_2D_kTc': 2.461},
        79.08:  {'Tc': 0.560027, 'Delta0': 0.695409, 'ratio_2D_kTc': 2.483},
        80.10:  {'Tc': 0.546374, 'Delta0': 0.684846, 'ratio_2D_kTc': 2.507},
        81.12:  {'Tc': 0.533554, 'Delta0': 0.674424, 'ratio_2D_kTc': 2.528},
        82.14:  {'Tc': 0.520443, 'Delta0': 0.664160, 'ratio_2D_kTc': 2.552},
        83.16:  {'Tc': 0.507589, 'Delta0': 0.654029, 'ratio_2D_kTc': 2.577},
        84.18:  {'Tc': 0.495521, 'Delta0': 0.644022, 'ratio_2D_kTc': 2.599},
        85.20:  {'Tc': 0.483158, 'Delta0': 0.634147, 'ratio_2D_kTc': 2.625},
        86.22:  {'Tc': 0.471032, 'Delta0': 0.624391, 'ratio_2D_kTc': 2.651},
        87.24:  {'Tc': 0.459137, 'Delta0': 0.614745, 'ratio_2D_kTc': 2.678},
        88.27:  {'Tc': 0.447974, 'Delta0': 0.605212, 'ratio_2D_kTc': 2.702},
        89.29:  {'Tc': 0.436267, 'Delta0': 0.595781, 'ratio_2D_kTc': 2.731},
        90.31:  {'Tc': 0.425515, 'Delta0': 0.586448, 'ratio_2D_kTc': 2.756},
        91.33:  {'Tc': 0.413993, 'Delta0': 0.577210, 'ratio_2D_kTc': 2.789},
        92.35:  {'Tc': 0.403636, 'Delta0': 0.568059, 'ratio_2D_kTc': 2.815},
        93.37:  {'Tc': 0.393460, 'Delta0': 0.558993, 'ratio_2D_kTc': 2.841},
        94.39:  {'Tc': 0.382544, 'Delta0': 0.550010, 'ratio_2D_kTc': 2.876},
        95.41:  {'Tc': 0.372735, 'Delta0': 0.541103, 'ratio_2D_kTc': 2.903},
        96.43:  {'Tc': 0.363091, 'Delta0': 0.532265, 'ratio_2D_kTc': 2.932},
        97.45:  {'Tc': 0.352739, 'Delta0': 0.523497, 'ratio_2D_kTc': 2.968},
        98.47:  {'Tc': 0.343438, 'Delta0': 0.514796, 'ratio_2D_kTc': 2.998},
        99.49:  {'Tc': 0.334291, 'Delta0': 0.506153, 'ratio_2D_kTc': 3.028},
        100.51: {'Tc': 0.325296, 'Delta0': 0.497566, 'ratio_2D_kTc': 3.059},
        101.53: {'Tc': 0.315638, 'Delta0': 0.489038, 'ratio_2D_kTc': 3.099},
        102.55: {'Tc': 0.306955, 'Delta0': 0.480560, 'ratio_2D_kTc': 3.131},
        103.57: {'Tc': 0.298414, 'Delta0': 0.472125, 'ratio_2D_kTc': 3.164},
        104.59: {'Tc': 0.289240, 'Delta0': 0.463737, 'ratio_2D_kTc': 3.207},
        105.61: {'Tc': 0.280994, 'Delta0': 0.455394, 'ratio_2D_kTc': 3.241},
        106.63: {'Tc': 0.272883, 'Delta0': 0.447087, 'ratio_2D_kTc': 3.277},
        107.65: {'Tc': 0.264902, 'Delta0': 0.438815, 'ratio_2D_kTc': 3.313},
        108.67: {'Tc': 0.257054, 'Delta0': 0.430579, 'ratio_2D_kTc': 3.350},
        109.69: {'Tc': 0.248629, 'Delta0': 0.422374, 'ratio_2D_kTc': 3.398},
        110.71: {'Tc': 0.241049, 'Delta0': 0.414197, 'ratio_2D_kTc': 3.437},
        111.73: {'Tc': 0.233593, 'Delta0': 0.406044, 'ratio_2D_kTc': 3.477},
        112.76: {'Tc': 0.226261, 'Delta0': 0.397920, 'ratio_2D_kTc': 3.517},
        113.78: {'Tc': 0.219049, 'Delta0': 0.389816, 'ratio_2D_kTc': 3.559},
        114.80: {'Tc': 0.211320, 'Delta0': 0.381733, 'ratio_2D_kTc': 3.613},
        115.82: {'Tc': 0.204359, 'Delta0': 0.373668, 'ratio_2D_kTc': 3.657},
        116.84: {'Tc': 0.197516, 'Delta0': 0.365622, 'ratio_2D_kTc': 3.702},
        117.86: {'Tc': 0.190789, 'Delta0': 0.357592, 'ratio_2D_kTc': 3.749},
        118.88: {'Tc': 0.184177, 'Delta0': 0.349575, 'ratio_2D_kTc': 3.796},
        119.90: {'Tc': 0.177679, 'Delta0': 0.341571, 'ratio_2D_kTc': 3.845},
        120.92: {'Tc': 0.171294, 'Delta0': 0.333581, 'ratio_2D_kTc': 3.895},
        121.94: {'Tc': 0.164479, 'Delta0': 0.325603, 'ratio_2D_kTc': 3.959},
        122.96: {'Tc': 0.158332, 'Delta0': 0.317634, 'ratio_2D_kTc': 4.012},
        123.98: {'Tc': 0.152296, 'Delta0': 0.309676, 'ratio_2D_kTc': 4.067},
        125.00: {'Tc': 0.146373, 'Delta0': 0.301731, 'ratio_2D_kTc': 4.123},
    }


# ── Public API ─────────────────────────────────────────────────────────
def load_sc_params(json_path=None, npz_path=None, verbose=True):
    """
    Load SC parameters with automatic fallback chain:
        JSON → NPZ → hardcoded dict

    Returns
    -------
    sc_params : dict  { U_float: {'Tc', 'Delta0', 'ratio_2D_kTc'} }
    source    : str   – which source was used
    """
    json_path = Path(json_path) if json_path else SC_PARAMS_JSON
    npz_path  = Path(npz_path)  if npz_path  else SC_PARAMS_NPZ

    if json_path.exists():
        try:
            sc = _load_from_json(json_path)
            if verbose:
                print(f"  [sc_loader_u] SC params loaded from JSON: {json_path}")
                print(f"                {len(sc)} U points found.")
            return sc, 'json'
        except Exception as e:
            if verbose:
                print(f"  [sc_loader_u] JSON failed ({e}), trying NPZ …")

    if npz_path.exists():
        try:
            sc = _load_from_npz(npz_path)
            if verbose:
                print(f"  [sc_loader_u] SC params loaded from NPZ: {npz_path}")
                print(f"                {len(sc)} U points found.")
            return sc, 'npz'
        except Exception as e:
            if verbose:
                print(f"  [sc_loader_u] NPZ failed ({e}), using fallback …")

    return _hardcoded_fallback(), 'hardcoded'


def get_sc_params(U, sc_params):
    """
    Return (Tc, Delta0) for a given U from the loaded sc_params dict.

    Parameters
    ----------
    U         : float
    sc_params : dict

    Returns
    -------
    (Tc, Delta0) : (float, float)
    """
    key = round(float(U), 2)
    if key in sc_params:
        return sc_params[key]['Tc'], sc_params[key]['Delta0']
    raise ValueError(
        f"U = {U} not found in SC params. "
        f"Available: {sorted(sc_params.keys())}"
    )