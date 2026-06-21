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
