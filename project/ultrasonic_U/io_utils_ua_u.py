# io_utils_ua_u.py
# =====================================================================
# Save / load ultrasonic U-scan results as JSON
# =====================================================================

import json
import numpy as np
from pathlib import Path

from parameters_ua_u import UA_U_RESULTS_DIR


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):  return obj.tolist()
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.integer):  return int(obj)
        if isinstance(obj, np.bool_):    return bool(obj)
        return super().default(obj)


def _prepare(data):
    if isinstance(data, dict):
        return {str(k): _prepare(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_prepare(v) for v in data]
    if isinstance(data, np.ndarray):  return data.tolist()
    if isinstance(data, np.floating): return float(data)
    if isinstance(data, np.integer):  return int(data)
    return data


ARRAY_KEYS = {
    'T', 'T_over_Tc', 'Delta', 'mu', 'W', 'WN', 'ratio',
    'U_arr', 'U_values',
}


def _restore(data):
    if isinstance(data, dict):
        return {k: (np.array(v) if k in ARRAY_KEYS and isinstance(v, list)
                    else _restore(v))
                for k, v in data.items()}
    return data


# ── Temperature-sweep results ─────────────────────────────────────────
def save_temperature_sweep(all_results, directory=None):
    """One JSON file per U + a manifest."""
    directory = Path(directory) if directory else UA_U_RESULTS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    manifest  = {}

    for U, res in all_results.items():
        fname = directory / f"temp_sweep_U_{U:.2f}.json"
        with fname.open('w') as f:
            json.dump(_prepare(res), f, indent=2,
                      allow_nan=True, cls=_NumpyEncoder)
        manifest[str(U)] = str(fname)
        print(f"  ✓  {fname}")

    mpath = directory / "temp_sweep_manifest.json"
    with mpath.open('w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  ✓  Manifest → {mpath}")
    return manifest


def load_temperature_sweep(directory=None):
    """Load all files listed in the manifest."""
    directory = Path(directory) if directory else UA_U_RESULTS_DIR
    mpath     = directory / "temp_sweep_manifest.json"
    with mpath.open() as f:
        manifest = json.load(f)

    all_results = {}
    for U_str, fname in manifest.items():
        with Path(fname).open() as f:
            raw = json.load(f)
        all_results[float(U_str)] = _restore(raw)
    print(f"  ✓  Loaded {len(all_results)} U entries from {directory}")
    return all_results


# ── U-scan results ────────────────────────────────────────────────────
def save_u_scan(U_arr, results, T_fracs, filepath=None):
    filepath = Path(filepath) if filepath \
               else UA_U_RESULTS_DIR / "u_scan.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'U_arr' : U_arr,
        'T_fracs': list(T_fracs),
        'results': {str(frac): results[frac] for frac in T_fracs},
    }
    with filepath.open('w') as f:
        json.dump(_prepare(payload), f, indent=2,
                  allow_nan=True, cls=_NumpyEncoder)
    print(f"  ✓  U scan → {filepath}")


def load_u_scan(filepath=None):
    filepath = Path(filepath) if filepath \
               else UA_U_RESULTS_DIR / "u_scan.json"
    with filepath.open() as f:
        payload = json.load(f)

    U_arr   = np.array(payload['U_arr'])
    T_fracs = [float(f) for f in payload['T_fracs']]
    results = {}
    for frac_str, val in payload['results'].items():
        frac = float(frac_str)
        results[frac] = {k: np.array(v) if isinstance(v, list) else v
                         for k, v in val.items()}
    print(f"  ✓  U scan loaded ← {filepath}")
    return U_arr, results, T_fracs