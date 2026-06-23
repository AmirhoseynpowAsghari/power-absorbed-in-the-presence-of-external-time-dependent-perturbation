# io_utils_tc.py
# =====================================================================
# Save / load scan results as JSON  and  .npz
# =====================================================================

import json
import numpy as np
from pathlib import Path


# ── JSON encoder that handles numpy types ────────────────────────────
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating): 
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def _arrays_from_lists(data):
    """
    Recursively convert any list of numbers back to a numpy array
    after JSON loading.
    """
    ARRAY_KEYS = {'V_SO', 'Tc', 'Deff_T0', 'D0_T0', 'DS_T0', 'ratio'}
    if isinstance(data, dict):
        return {
            k: (np.array(v) if k in ARRAY_KEYS and isinstance(v, list) else v)
            for k, v in data.items()
        }
    return data


# ── JSON ──────────────────────────────────────────────────────────────
def save_json(results, meta=None, filepath="results/tc_vs_vso.json"):
    """
    Serialise scan results (and optional metadata) to JSON.

    Parameters
    ----------
    results  : dict – output of run_vso_scan()
    meta     : dict, optional – parameter metadata
    filepath : str or Path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'meta'   : meta or {},
        'results': results,
    }

    with filepath.open('w') as f:
        json.dump(payload, f, indent=2, allow_nan=True, cls=NumpyEncoder)

    size_kb = filepath.stat().st_size / 1024
    print(f"  ✓  JSON saved → {filepath}  ({size_kb:.1f} kB)")


def load_json(filepath="results/tc_vs_vso.json"):
    """
    Load JSON saved by :func:`save_json`.

    Returns
    -------
    results : dict (numpy arrays restored)
    meta    : dict
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Not found: {filepath}")

    with filepath.open() as f:
        payload = json.load(f)

    results = _arrays_from_lists(payload.get('results', {}))
    meta    = payload.get('meta', {})
    print(f"  ✓  JSON loaded ← {filepath}")
    return results, meta


# ── NumPy .npz ────────────────────────────────────────────────────────
def save_npz(results, meta=None, filepath="results/Tc_vs_VSO.npz"):
    """
    Save results to a compressed .npz archive.

    Metadata scalars are stored as zero-dimensional arrays so they
    are preserved exactly.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    save_dict = {
        'V_SO'    : results['V_SO'],
        'Tc'      : results['Tc'],
        'Deff_T0' : results['Deff_T0'],
        'D0_T0'   : results['D0_T0'],
        'DS_T0'   : results['DS_T0'],
        'ratio'   : results['ratio'],
    }

    if meta:
        for k, v in meta.items():
            save_dict[f'meta_{k}'] = np.array(v)

    np.savez_compressed(filepath, **save_dict)
    print(f"  ✓  .npz saved  → {filepath}")


def load_npz(filepath="results/Tc_vs_VSO.npz"):
    """
    Load a .npz file saved by :func:`save_npz`.

    Returns
    -------
    results : dict
    meta    : dict  (keys stripped of 'meta_' prefix)
    """
    filepath = Path(filepath)
    data = np.load(filepath)

    results = {
        k: data[k]
        for k in ('V_SO', 'Tc', 'Deff_T0', 'D0_T0', 'DS_T0', 'ratio')
        if k in data
    }
    meta = {
        k[5:]: data[k].item()
        for k in data.files
        if k.startswith('meta_')
    }
    print(f"  ✓  .npz loaded ← {filepath}")
    return results, meta
