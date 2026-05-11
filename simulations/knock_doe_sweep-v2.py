"""
Knock‑Limited BMEP Sweep v2 – Cantera chemical auto‑ignition model
Flat‑6 Boxer 84×84 mm, 95 RON surrogate (PRF95)
Uses isentropic unburnt‑gas compression + Livengood‑Wu integral.
"""

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import sys

# ── Geometry ──
BORE    = 0.084
STROKE  = 0.084
CONROD  = 0.144
V_SWEPT = np.pi/4 * BORE**2 * STROKE

ENGINE_SPEED = 4000   # rpm

# Valve timings (0° = TDC compression)
IVO = 350
EVO = 120
EVC = 370
# IVC will be swept (value in °ABDC, i.e. 540 + ivc)

INTAKE_TEMP        = 313.0   # K
EXHAUST_BACKPRESS  = 1.1e5   # Pa

# Fuel & combustion
LAMBDA        = 0.9
AFR_STOICH    = 14.7
FUEL_LHV      = 44.0e6   # J/kg
FUEL_MASS_FRAC = 1.0 / (1.0 + AFR_STOICH * LAMBDA)

# Wiebe
COMB_DURATION = 28.0     # deg
WIEBE_M       = 2.0
WIEBE_A       = 5.0

# Sweep ranges
CR_RANGE    = [9.0, 9.5, 10.0]
BOOST_RANGE = np.linspace(1.5e5, 2.2e5, 8)   # Pa(abs)
EGR_RANGE   = [0.0, 0.05, 0.10, 0.15]
IVC_RANGE   = [40, 50, 60, 70]                # °ABDC

# Knock parameters
KNOCK_INTEGRAL_LIMIT = 1.0

# ── Load PRF mechanism for 95 RON surrogate ──
try:
    gas_prf = ct.Solution('nheptane_iso.yaml')
except Exception as e:
    print("Error: 'nheptane_iso.yaml' not found.", file=sys.stderr)
    print("Download the file from https://github.com/Cantera/cantera/blob/main/data/nheptane_iso.yaml")
    print("and place it in your working directory.", file=sys.stderr)
    sys.exit(1)

# We'll use a PRF mixture: 95% iso‑octane, 5% n‑heptane by volume.
# The mechanism includes species: ic8h18 (iso-octane), nC7H16 (n-heptane).
# Set up a base mixture at lambda=0.9, phi = 1/lambda.
phi = 1.0 / LAMBDA
# Stoichiometric iso-octane: 2 C8H18 + 25 O2 -> 16 CO2 + 18 H2O, so O2/fuel = 12.5
# n-heptane: C7H16 + 11 O2 -> 7 CO2 + 8 H2O, O2/fuel = 11
# For PRF95 (0.95 ic8h18, 0.05 nC7H16 molar base):
# O2 required per mole fuel = 0.95*12.5 + 0.05*11 = 11.875 + 0.55 = 12.425
# Fuel mole fraction for equivalence ratio phi: X_fuel = 1, X_O2 = 12.425/phi, X_N2 = 12.425*3.76/phi
stoich_O2 = 12.425
X_fuel_ic8 = 0.95
X_fuel_nc7 = 0.05
X_O2 = stoich_O2 / phi
X_N2 = stoich_O2 * 3.76 / phi
total_moles = X_fuel_ic8 + X_fuel_nc7 + X_O2 + X_N2
comp_str = (f'ic8h18:{X_fuel_ic8/total_moles:.6f}, '
            f'nC7H16:{X_fuel_nc7/total_moles:.6f}, '
            f'O2:{X_O2/total_moles:.6f}, N2:{X_N2/total_moles:.6f}')

# ── Helper functions ──
def cylinder_volume(theta, cr, V_clear):
    """Volume at crank angle theta (deg) for given clearance volume."""
    R = STROKE / 2
    L = CONROD
    y = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R*np.sin(np.deg2rad(theta)))**2)
    return V_clear + (np.pi/4) * BORE**2 * y

def specific_gas_constant(gas_obj):
    return gas_obj.cp_mass - gas_obj.cv_mass

def unburned_temperature(T_ivc, P_ivc, P_current, gamma_ivc):
    """Isentropic compression of unburned mixture from IVC condition."""
    return T_ivc * (P_current / P_ivc) ** ((gamma_ivc - 1.0) / gamma_ivc)

def autoignition_delay_ms(T, P, gas_mixture):
    """
    Compute ignition delay (ms) at constant volume for the given gas mixture
    using Cantera's reactor network. Returns the time to maximum dT/dt.
    """
    # Create a copy of the gas and set in a constant volume reactor
    gas = ct.Solution('nheptane_iso.yaml')
    gas.TPX = T, P, gas_mixture.X
    r = ct.IdealGasConstPressureReactor(gas)  # actually we need constant volume
    # Cantera: IdealGasReactor with constant volume (set volume fixed)
    # Better: use a ReactorNet with an IdealGasReactor, set volume=1, and use advance_to_steady_state?
    # For ignition delay, we typically use a batch reactor (constant internal energy/volume).
    # Use ct.Reactor with a constant volume (use IdealGasReactor, set volume). The reactor automatically integrates.
    # Simple method: set up a reactor network, run until max temperature rate.
    r = ct.IdealGasReactor(gas)
    net = ct.ReactorNet([r])
    
    # Advance in small steps until we see a sharp temperature rise
    t_max = 0.1  # 100 ms max
    dt = 1e-6
    t = 0.0
    T_prev = T
    max_dTdt = 0.0
    while t < t_max:
        t = net.step()
        if r.T > 3000:  # ignited
            break
        # find when temperature rate peaks
        # crude method: record time when T rises 200 K above initial
        if r.T - T > 200:
            return (t * 1000)  # ms
    # If did not ignite within t_max, return large delay
    return t_max * 1000

# ── Single cycle with knock ──
def run_cycle_with_knock(cr, boost_pa, egr_rate, ivc_atdc):
    v_clear = V_SWEPT / (cr - 1)
    ivc_ca = 540 + ivc_atdc   # intake valve close angle
    
    theta_max = max(630, ivc_ca + 10)
    theta = np.linspace(-180, theta_max, int((theta_max+180)/0.5) + 1)
    
    # Set up fresh charge gas state (using gri30 for cycle, not needed for knock)
    # We'll still use gri30 for cycle properties (easy), but we need PRF gas for knock.
    # For simplicity, we can stick with gri30 for the cycle, but we must compute ignition delay using the PRF mixture
    # at the unburned conditions. We can do that separately.
    gas_cycle = ct.Solution('gri30.yaml')
    # Use CH4 as surrogate for cycle, but the ignition delay will be from PRF mechanism.
    # Fresh charge composition for cycle (CH4 surrogate) still needed for gas properties.
    phi_ch4 = 1.0 / LAMBDA
    X_ch4 = 1.0
    X_o2_cycle  = 2.0 / phi_ch4
    X_n2_cycle  = 2.0 * 3.76 / phi_ch4
    total_cycle = X_ch4 + X_o2_cycle + X_n2_cycle
    gas_cycle.TPX = INTAKE_TEMP, boost_pa, f'CH4:{X_ch4/total_cycle:.4f}, O2:{X_o2_cycle/total_cycle:.4f}, N2:{X_n2_cycle/total_cycle:.4f}'
    R_fresh = specific_gas_constant(gas_cycle)
    gamma_ivc = gas_cycle.cp_mass / gas_cycle.cv_mass  # for isentropic compression
    
    # Prepare PRF mixture for ignition delay: same composition string as defined globally
    gas_prf_mix = ct.Solution('nheptane_iso.yaml')
    gas_prf_mix.TPX = INTAKE_TEMP, boost_pa, comp_str
    
    # Friction
    speed_krpm = ENGINE_SPEED / 1000.0
    A_f = 0.4e5
    B_f = 0.03e5
    C_f = 0.0025e5
    D_f = 0.0055
    
    # Spark sweep
    best_ca50 = None
    best_bmep = -1e9
    best_result = None
    
    for ca50 in np.linspace(4.0, 35.0, 20):
        P = np.zeros_like(theta)
        T = np.zeros_like(theta)
        mass = np.zeros_like(theta)
        
        P[0] = boost_pa
        T[0] = INTAKE_TEMP
        mass[0] = P[0] * cylinder_volume(-180, cr, v_clear) / (R_fresh * T[0])
        
        mass_trapped = mass[0]
        x_b_prev = 0.0
        knock_integral = 0.0
        knock_flag = False
        
        # Record state at IVC for unburned temperature model
        T_ivc = None
        P_ivc = None
        
        for i in range(1, len(theta)):
            ca = theta[i]
            V = cylinder_volume(ca, cr, v_clear)
            P_prev, T_prev, m_prev = P[i-1], T[i-1], mass[i-1]
            
            # Gas exchange
            if IVO <= ca < ivc_ca:
                P[i] = boost_pa
                T[i] = INTAKE_TEMP
                mass[i] = P[i] * V / (R_fresh * T[i])
                gas_cycle.TPX = T[i], P[i], gas_cycle.X  # fresh charge
                if ca >= ivc_ca - 1.0:
                    mass_trapped = mass[i]
                    T_ivc = T[i]
                    P_ivc = P[i]
                    gamma_ivc = gas_cycle.cp_mass / gas_cycle.cv_mass
                continue
            elif EVO <= ca < EVC:
                P[i] = EXHAUST_BACKPRESS
                T[i] = 1200.0
                mass[i] = P[i] * V / (specific_gas_constant(gas_cycle) * T[i])
                continue
            
            # Closed cycle
            if ca50 - COMB_DURATION/2 <= ca <= ca50 + COMB_DURATION/2:
                x_b = 1.0 - np.exp(-WIEBE_A * ((ca - (ca50 - COMB_DURATION/2))/COMB_DURATION)**WIEBE_M)
                dQ_comb = (FUEL_LHV * FUEL_MASS_FRAC * mass_trapped) * (x_b - x_b_prev)
                x_b_prev = x_b
            else:
                dQ_comb = 0.0
                if i>0 and (ca50 - COMB_DURATION/2 <= theta[i-1] <= ca50 + COMB_DURATION/2):
                    x_b_prev = 1.0
            
            # Heat transfer (Woschni)
            Sp = 2 * STROKE * ENGINE_SPEED / 60
            w = 2.28 * Sp
            A_cyl = (np.pi*BORE*V/(np.pi/4*BORE**2) + 2*np.pi/4*BORE**2)
            h = 3.26 * BORE**(-0.2) * (P_prev/1e5)**0.8 * T_prev**(-0.55) * w**0.8
            dQ_loss = h * A_cyl * (T_prev - 450.0) * (abs(ca - theta[i-1])/(6*ENGINE_SPEED))
            
            # First law
            Cv = gas_cycle.cv_mass
            dU = -P_prev * (V - cylinder_volume(theta[i-1], cr, v_clear)) + dQ_comb - dQ_loss
            T_new = T_prev + dU / (m_prev * Cv)
            R_spec = specific_gas_constant(gas_cycle)
            P_new = m_prev * R_spec * T_new / V
            
            P[i], T[i], mass[i] = P_new, T_new, m_prev
            gas_cycle.TPX = T_new, P_new, gas_cycle.X
            
            # Knock integral evaluation
            if ca > ivc_ca and not knock_flag and T_ivc is not None:
                # unburned temperature (end-gas) from isentropic compression of fresh charge
                T_unb = unburned_temperature(T_ivc, P_ivc, P_new, gamma_ivc)
                # ignition delay for PRF95 mixture at current P, T_unb
                tau_ms = autoignition_delay_ms(T_unb, P_new, gas_prf_mix)
                dt_sec = abs(ca - theta[i-1]) / (6 * ENGINE_SPEED)
                knock_integral += dt_sec / (tau_ms / 1000.0)
                if knock_integral >= KNOCK_INTEGRAL_LIMIT:
                    knock_flag = True
                    break  # knock occurs, stop cycle
            
        if knock_flag:
            # too advanced, skip
            continue
        else:
            # Compute BMEP
            V_arr = cylinder_volume(theta, cr, v_clear)
            work = np.trapezoid(P, V_arr)
            imep = work / V_SWEPT
            fmep = A_f + B_f * speed_krpm + C_f * speed_krpm**2 + D_f * imep
            bmep = imep - fmep
            if bmep > best_bmep:
                best_bmep = bmep
                best_ca50 = ca50
                best_result = (theta, P, T, imep, fmep, bmep)
    
    if best_ca50 is None:
        return None, None, None, None
    return best_ca50, best_bmep, best_result[0], best_result[1]

# ── DOE loop ──
results = []
total = len(CR_RANGE)*len(BOOST_RANGE)*len(EGR_RANGE)*len(IVC_RANGE)
count = 0
print("Running rigorous knock sweep...")
for cr, boost, egr, ivc in product(CR_RANGE, BOOST_RANGE, EGR_RANGE, IVC_RANGE):
    ca50, bmep, theta_arr, P_arr = run_cycle_with_knock(cr, boost, egr, ivc)
    if bmep is not None:
        torque_cyl = bmep * V_SWEPT / (4*np.pi)
        torque_total = torque_cyl * 6
        results.append((cr, boost/1e5, egr, ivc, ca50, bmep/1e5, torque_total))
    count += 1
    if count % 20 == 0:
        print(f"  {count}/{total} done, last max BMEP: {bmep/1e5:.2f} bar" if bmep else f"  {count}/{total}")

target = 22.5
tol = 0.5
matching = [r for r in results if target-tol <= r[5] <= target+tol]
print("\n=== Matching knock‑limited BMEP = 22.5±0.5 bar ===")
if matching:
    matching.sort(key=lambda x: x[5])
    print(f"{'CR':>4}  {'Boost':>8}  {'EGR':>6}  {'IVC':>6}  {'CA50':>6}  {'BMEP':>8}  {'Torque':>8}")
    for r in matching:
        print(f"{r[0]:4.1f}  {r[1]:8.3f}  {r[2]:6.2f}  {r[3]:6.0f}  {r[4]:6.1f}  {r[5]:8.2f}  {r[6]:8.1f}")
else:
    best_match = min(results, key=lambda x: abs(x[5]-target))
    print(f"Closest: CR={best_match[0]:.1f} Boost={best_match[1]:.2f}bar EGR={best_match[2]:.2f} IVC={best_match[3]:.0f}° CA50={best_match[4]:.1f}° BMEP={best_match[5]:.2f} bar Torque={best_match[6]:.1f} Nm")