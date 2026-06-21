# physics_ua.py
# =====================================================================
# Fermi function, BCS gap, electron density, mu solver
# =====================================================================

import numpy as np
from scipy.optimize import brentq

from parameters_ua import kB, t, n_target
from kgrid_ua      import cos_sum, sqrt_sin


def fermi_vec(E, T, mu):
    """Vectorised Fermi-Dirac distribution."""
    if T <= 1e-10:
        return np.where(E < mu, 1.0, 0.0)
    x = (E - mu) / (kB * T)
    return np.where(x >  500, 0.0,
           np.where(x < -500, 1.0,
                    1.0 / (np.exp(x) + 1.0)))


def Delta_T(T, Tc, Delta0):
    """
    BCS mean-field gap:   Delta(T) = Delta0 * sqrt(1 - (T/Tc)^2)
    Returns 0 for T >= Tc.
    """
    if T >= Tc:
        return 0.0
    return Delta0 * np.sqrt(1.0 - (T / Tc) ** 2)


def compute_electron_density(mu, Delta, T, VSO):
    """
    Electron density from the BCS number equation:

        n = 1 - (1/2) < (xi_+/E_+) tanh(E_+/2T)
                      + (xi_-/E_-) tanh(E_-/2T) >_k

    Uses the 200×200 k-grid from kgrid_ua.
    """
    eps_plus  = -2.0 * t * cos_sum - 2.0 * VSO * sqrt_sin
    eps_minus = -2.0 * t * cos_sum + 2.0 * VSO * sqrt_sin

    xi_plus  = eps_plus  - mu
    xi_minus = eps_minus - mu

    E_plus  = np.sqrt(xi_plus**2  + Delta**2)
    E_minus = np.sqrt(xi_minus**2 + Delta**2)

    if T < 1e-10:
        tanh_plus  = np.ones_like(E_plus)
        tanh_minus = np.ones_like(E_minus)
    else:
        tanh_plus  = np.tanh(E_plus  / (2.0 * kB * T))
        tanh_minus = np.tanh(E_minus / (2.0 * kB * T))

    term_plus  = (xi_plus  / E_plus)  * tanh_plus
    term_minus = (xi_minus / E_minus) * tanh_minus

    return 1.0 - 0.5 * (np.mean(term_plus) + np.mean(term_minus))


def find_mu(T, Delta, VSO, n_tgt=None, mu_bracket=(-25.0, 25.0)):
    """
    Find mu such that n(mu) == n_tgt using Brent's method.

    Parameters
    ----------
    T         : float
    Delta     : float
    VSO       : float
    n_tgt     : float, optional – defaults to parameters_ua.n_target
    mu_bracket: (float, float)

    Returns
    -------
    float – chemical potential
    """
    if n_tgt is None:
        n_tgt = n_target

    def residual(mu):
        return compute_electron_density(mu, Delta, T, VSO) - n_tgt

    try:
        return brentq(residual, *mu_bracket, xtol=1e-10)
    except ValueError:
        print(f"  [find_mu] WARNING: failed at T={T:.4f}, "
              f"Delta={Delta:.4f}, VSO={VSO}. Returning mu=0.")
        return 0.0