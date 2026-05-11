"""
Knock‑Limited BMEP Sweep (Final Corrected) – Original Douaud & Eyzat constants
Flat‑6 Boxer 84×84 mm, 95 RON, 7500 rpm redline
Uses isentropic unburnt‑gas compression + Livengood‑Wu integral.
"""

import cantera as ct
import numpy as np
from itertools import product

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
# IVC = 540 + ivc_atdc (swept)

INTAKE_TEMP        = 313.0   # K
EXHAUST_BACKPRESS  = 1.1e5   # Pa

# Fuel & combustion
LAMBDA         = 0.9
FUEL_LHV       = 44.0e6       # J/kg
FUEL_MASS_FRAC = 1.0 / (1.0 + 14.7 * LAMBDA)   # approx

# Wiebe
COMB_DURATION = 28.0     # deg
WIEBE_M       = 2.0
WIEBE_A       = 5.0

# Sweep ranges
CR_RANGE    = [9.0, 9.5, 10.0]
BOOST_RANGE = np.linspace(1.5e5, 2.2e5, 8)   # Pa(abs)
EGR_RANGE   = [0.0, 0.05, 0.10, 0.15]
IVC_RANGE   = [40, 50, 60, 70]                # °ABDC

KNOCK_LIMIT = 1.0

# ── Original Douaud & Eyzat knock correlation ──
# τ [ms] = A_DE * p_bar^(-1.3) * phi^(-0.5) * exp(3800/T)
A_DE = 0.026    # ms * bar^1.3   (original constant for RON 95)

def ignition_delay_ms(T, P, phi):
    """Ignition delay (ms) for unburnt end‑gas at temperature T (K), pressure P (Pa)."""
    p_bar = P / 1e5
    tau = A_DE * p_bar**(-1.3) * phi**(-0.5) * np.exp(3800.0 / T)
    return tau  # ms

# ── Helper functions ──
def cylinder_volume(theta, cr, V_clear):
    R = STROKE / 2
    L = CONROD
    y = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R*np.sin(np.deg2rad(theta)))**2)
    return V_clear + (np.pi/4) * BORE**2 * y

def specific_gas_constant(gas_obj):
    return gas_obj.cp_mass - gas_obj.cv_mass

def run_cycle_with_knock(cr, boost_pa, egr_rate, ivc_atdc):
    v_clear = V_SWEPT / (cr - 1)
    ivc_ca = 540 + ivc_atdc
    
    theta_max = max(630, ivc_ca + 10)
    theta = np.linspace(-180, theta_max, int((theta_max+180)/0.5) + 1)
    
    # Fresh charge gas properties (CH4 surrogate for thermodynamics)
    gas_cycle = ct.Solution('gri30.yaml')
    phi = 1.0 / LAMBDA
    X_ch4 = 1.0
    X_o2  = 2.0 / phi
    X_n2  = 2.0 * 3.76 / phi
    total = X_ch4 + X_o2 + X_n2
    gas_cycle.TPX = INTAKE_TEMP, boost_pa, f'CH4:{X_ch4/total:.4f}, O2:{X_o2/total:.4f}, N2:{X_n2/total:.4f}'
    R_fresh = specific_gas_constant(gas_cycle)
    gamma_ivc = gas_cycle.cp_mass / gas_cycle.cv_mass
    
    # Friction
    speed_krpm = ENGINE_SPEED / 1000.0
    A_f = 0.4e5
    B_f = 0.03e5
    C_f = 0.0025e5
    D_f = 0.0055
    
    best_ca50 = None
    best_bmep = -1e9
    best_result = None
    best_knock_int = 0.0
    
    for ca50 in np.linspace(4.0, 45.0, 25):   # extended upper bound to capture knock limit
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
        
        T_ivc = None
        P_ivc = None
        
        for i in range(1, len(theta)):
            ca = theta[i]
            V = cylinder_volume(ca, cr, v_clear)
            P_prev, T_prev, m_prev = P[i-1], T[i-1], mass[i-1]
            
            if IVO <= ca < ivc_ca:
                P[i] = boost_pa
                T[i] = INTAKE_TEMP
                mass[i] = P[i] * V / (R_fresh * T[i])
                gas_cycle.TPX = T[i], P[i], gas_cycle.X
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
            
            # Heat transfer
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
            
            # Knock integral
            if ca > ivc_ca and not knock_flag and T_ivc is not None:
                T_unb = T_ivc * (P_new / P_ivc) ** ((gamma_ivc - 1) / gamma_ivc)
                tau_ms = ignition_delay_ms(T_unb, P_new, phi)
                dt_sec = abs(ca - theta[i-1]) / (6 * ENGINE_SPEED)
                knock_integral += dt_sec / (tau_ms / 1000.0)
                if knock_integral >= KNOCK_LIMIT:
                    knock_flag = True
                    break
            
        if knock_flag:
            continue
        else:
            V_arr = cylinder_volume(theta, cr, v_clear)
            work = np.trapezoid(P, V_arr)
            imep = work / V_SWEPT
            fmep = A_f + B_f * speed_krpm + C_f * speed_krpm**2 + D_f * imep
            bmep = imep - fmep
            if bmep > best_bmep:
                best_bmep = bmep
                best_ca50 = ca50
                best_knock_int = knock_integral
                best_result = (theta.copy(), P.copy(), T.copy(), imep, fmep)  # 5 items
    
    if best_ca50 is None:
        return None, None, None, None
    return best_ca50, best_knock_int, best_bmep, best_result

# ── DOE sweep ──
results = []
total = len(CR_RANGE)*len(BOOST_RANGE)*len(EGR_RANGE)*len(IVC_RANGE)
count = 0
print("Running final knock sweep (A=0.026)...")
for cr, boost, egr, ivc in product(CR_RANGE, BOOST_RANGE, EGR_RANGE, IVC_RANGE):
    ca50, knock_int, bmep, best_result = run_cycle_with_knock(cr, boost, egr, ivc)
    if bmep is not None:
        theta_arr, P_arr, T_arr, imep, fmep = best_result  # unpack 5 items
        torque_cyl = bmep * V_SWEPT / (4*np.pi)
        results.append((cr, boost/1e5, egr, ivc, ca50, bmep/1e5, torque_cyl*6, knock_int))
    count += 1
    if count % 20 == 0:
        print(f"  {count}/{total} done")

# Filter for target
target = 22.5
tol = 0.5
matching = [r for r in results if target-tol <= r[5] <= target+tol]

print("\n=== Knock‑limited combinations achieving BMEP 22.5±0.5 bar ===")
if matching:
    matching.sort(key=lambda x: x[5])
    print(f"{'CR':>4}  {'Boost':>8}  {'EGR':>6}  {'IVC':>6}  {'CA50':>6}  {'BMEP':>8}  {'Torque':>8}  {'KnockInt':>8}")
    for r in matching:
        print(f"{r[0]:4.1f}  {r[1]:8.3f}  {r[2]:6.2f}  {r[3]:6.0f}  {r[4]:6.1f}  {r[5]:8.2f}  {r[6]:8.1f}  {r[7]:8.3f}")
else:
    closest = sorted(results, key=lambda x: abs(x[5]-target))[:3]
    print("No exact match. Closest:")
    for r in closest:
        print(f"CR={r[0]:.1f} Boost={r[1]:.2f}bar EGR={r[2]:.2f} IVC={r[3]:.0f}° CA50={r[4]:.1f}° BMEP={r[5]:.2f}bar Torque={r[6]:.1f}Nm KnockInt={r[7]:.3f}")

# Best knock‑limited BMEP overall
best = max(results, key=lambda x: x[5])
print(f"\nHighest knock‑limited BMEP: CR={best[0]:.1f} Boost={best[1]:.2f}bar EGR={best[2]:.2f} IVC={best[3]:.0f}° CA50={best[4]:.1f}° BMEP={best[5]:.2f}bar Torque={best[6]:.1f}Nm KnockInt={best[7]:.3f}")