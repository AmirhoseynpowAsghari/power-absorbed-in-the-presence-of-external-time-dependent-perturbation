# io_utils_u.py
# =====================================================================
# Save / load Tc-vs-U results as JSON and .npz
#
# The JSON output is designed to be readable by the ultrasonic
# attenuation code's sc_loader.py — same format as tc_vs_vso.json.
# =====================================================================

import json
import numpy as np
from pathlib import Path

from parameters_u import RESULTS_DIR, JSON_PATH, NPZ_PATH


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):  return obj.tolist()
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.integer):  return int(obj)
        if isinstance(obj, np.bool_):    return bool(obj)
        return super().default(obj)


def _prepare(data):
    """Recursively convert numpy types for JSON serialisation."""
    if isinstance(data, dict):
        return {str(k): _prepare(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_prepare(v) for v in data]
    if isinstance(data, np.ndarray):  return data.tolist()
    if isinstance(data, np.floating): return float(data)
    if isinstance(data, np.integer):  return int(data)
    return data


ARRAY_KEYS = {'U', 'Tc', 'Deff_T0', 'D0_T0', 'DS_T0', 'ratio'}


def _restore(data):
    """Restore numpy arrays after JSON loading."""
    if isinstance(data, dict):
        return {
            k: (np.array(v) if k in ARRAY_KEYS and isinstance(v, list)
                else _restore(v))
            for k, v in data.items()
        }
    return data


# ── JSON ──────────────────────────────────────────────────────────────
def save_json(results, meta=None, filepath=None):
    """
    Save U-scan results to JSON.

    Format mirrors tc_vs_vso.json so the ultrasonic sc_loader
    can read it with minimal changes.

    Parameters
    ----------
    results  : dict – output of run_u_scan()
    meta     : dict, optional
    filepath : Path, optional
    """
    filepath = Path(filepath) if filepath else JSON_PATH
    filepath.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'meta'   : _prepare(meta or {}),
        'results': _prepare(results),
    }

    with filepath.open('w') as f:
        json.dump(payload, f, indent=2, allow_nan=True,
                  cls=_NumpyEncoder)

    kb = filepath.stat().st_size / 1024
    print(f"  ✓  JSON saved → {filepath}  ({kb:.1f} kB)")


def load_json(filepath=None):
    """
    Load JSON saved by save_json().

    Returns
    -------
    results : dict (numpy arrays restored)
    meta    : dict
    """
    filepath = Path(filepath) if filepath else JSON_PATH
    if not filepath.exists():
        raise FileNotFoundError(f"Not found: {filepath}")

    with filepath.open() as f:
        payload = json.load(f)

    results = _restore(payload.get('results', {}))
    meta    = payload.get('meta', {})
    print(f"  ✓  JSON loaded ← {filepath}")
    return results, meta


# ── NPZ ───────────────────────────────────────────────────────────────
def save_npz(results, meta=None, filepath=None):
    """
    Save results to compressed .npz  (matches original monolithic output).
    """
    filepath = Path(filepath) if filepath else NPZ_PATH
    filepath.parent.mkdir(parents=True, exist_ok=True)

    save_dict = {
        'U'           : results['U'],
        'Tc'          : results['Tc'],
        'Delta_eff_T0': results['Deff_T0'],
        'D0_T0'       : results['D0_T0'],
        'DS_T0'       : results['DS_T0'],
        'ratio'       : results['ratio'],
    }
    if meta:
        for k, v in meta.items():
            save_dict[f'meta_{k}'] = np.array(v)

    np.savez_compressed(filepath, **save_dict)
    print(f"  ✓  NPZ saved  → {filepath}")


def load_npz(filepath=None):
    """Load .npz saved by save_npz()."""
    filepath = Path(filepath) if filepath else NPZ_PATH
    data = np.load(filepath)

    results = {
        'U'       : data['U'],
        'Tc'      : data['Tc'],
        'Deff_T0' : data['Delta_eff_T0'],
        'D0_T0'   : data.get('D0_T0', np.array([])),
        'DS_T0'   : data.get('DS_T0', np.array([])),
        'ratio'   : data.get('ratio', np.array([])),
    }
    meta = {k[5:]: data[k].item()
            for k in data.files if k.startswith('meta_')}
    print(f"  ✓  NPZ loaded ← {filepath}")
    return results, meta