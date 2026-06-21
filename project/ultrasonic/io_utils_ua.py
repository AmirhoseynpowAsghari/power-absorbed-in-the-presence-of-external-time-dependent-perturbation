# io_utils_ua.py
# =====================================================================
# Save / load ultrasonic attenuation results as JSON
# =====================================================================

import json
import numpy as np
from pathlib import Path

from parameters_ua import UA_RESULTS_DIR


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.integer):  return int(obj)
        if isinstance(obj, np.bool_):    return bool(obj)
        return super().default(obj)


def _to_python(data):
    """Recursively convert numpy objects; stringify float dict keys."""
    if isinstance(data, dict):
        return {str(k): _to_python(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_to_python(v) for v in data]
    if isinstance(data, np.ndarray):   return data.tolist()
    if isinstance(data, np.floating):  return float(data)
    if isinstance(data, np.integer):   return int(data)
    return data


ARRAY_KEYS = {
    'T', 'T_over_Tc', 'Delta', 'mu', 'W', 'WN', 'ratio',
    'E_grid', 'VSO_arr', 'VSO_values',
}


def _restore(data):
    """Restore numpy arrays after JSON loading."""
    if isinstance(data, dict):
        return {k: (np.array(v) if k in ARRAY_KEYS and isinstance(v, list)
                    else _restore(v))
                for k, v in data.items()}
    return data


# ── Temperature-sweep results ─────────────────────────────────────────
def save_temperature_sweep(all_results, directory=None):
    """
    Save temperature-sweep results.  One JSON file per VSO +
    a manifest file listing all of them.
    """
    directory = Path(directory) if directory else UA_RESULTS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    manifest  = {}

    for VSO, res in all_results.items():
        fname = directory / f"temp_sweep_VSO_{VSO:.4f}.json"
        with fname.open('w') as f:
            json.dump(_to_python(res), f, indent=2,
                      allow_nan=True, cls=_NumpyEncoder)
        manifest[str(VSO)] = str(fname)
        print(f"  ✓  {fname}")

    mpath = directory / "temp_sweep_manifest.json"
    with mpath.open('w') as f:
        json.dump(manifest, f, indent=2)
    print(f"  ✓  Manifest → {mpath}")
    return manifest


def load_temperature_sweep(directory=None):
    """Load all temperature-sweep files listed in the manifest."""
    directory = Path(directory) if directory else UA_RESULTS_DIR
    mpath     = directory / "temp_sweep_manifest.json"
    with mpath.open() as f:
        manifest = json.load(f)

    all_results = {}
    for vso_str, fname in manifest.items():
        with Path(fname).open() as f:
            raw = json.load(f)
        all_results[float(vso_str)] = _restore(raw)
    print(f"  ✓  Loaded {len(all_results)} VSO entries from {directory}")
    return all_results


# ── VSO-scan results ──────────────────────────────────────────────────
def save_vso_scan(VSO_arr, results, T_fracs,
                  filepath=None):
    filepath = Path(filepath) if filepath \
               else UA_RESULTS_DIR / "vso_scan.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'VSO_arr': VSO_arr,
        'T_fracs': list(T_fracs),
        'results': {str(frac): results[frac] for frac in T_fracs},
    }
    with filepath.open('w') as f:
        json.dump(_to_python(payload), f, indent=2,
                  allow_nan=True, cls=_NumpyEncoder)
    print(f"  ✓  VSO scan → {filepath}")


def load_vso_scan(filepath=None):
    filepath = Path(filepath) if filepath \
               else UA_RESULTS_DIR / "vso_scan.json"
    with filepath.open() as f:
        payload = json.load(f)

    VSO_arr = np.array(payload['VSO_arr'])
    T_fracs = [float(f) for f in payload['T_fracs']]
    results = {}
    for frac_str, val in payload['results'].items():
        frac = float(frac_str)
        results[frac] = {k: np.array(v) if isinstance(v, list) else v
                         for k, v in val.items()}
    print(f"  ✓  VSO scan loaded ← {filepath}")
    return VSO_arr, results, T_fracs