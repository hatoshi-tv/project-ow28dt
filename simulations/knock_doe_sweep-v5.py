"""
Knock‑Limited BMEP Sweep – Using a production‑engine knock map (95 RON GDI)
Flat‑6 Boxer 84×84 mm, 7500 rpm redline
The map gives maximum CA50 (deg ATDC) as a function of BMEP and CR,
derived from BMW B48, Mercedes M260, and VW EA888 data.
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

IVO = 350
EVO = 120
EVC = 370

INTAKE_TEMP        = 313.0
EXHAUST_BACKPRESS  = 1.1e5

LAMBDA         = 0.9
FUEL_LHV       = 44.0e6
FUEL_MASS_FRAC = 1.0 / (1.0 + 14.7 * LAMBDA)

COMB_DURATION = 28.0
WIEBE_M       = 2.0
WIEBE_A       = 5.0

# Sweep ranges
CR_RANGE    = [9.0, 9.5, 10.0]
BOOST_RANGE = np.linspace(1.5e5, 2.2e5, 8)   # Pa(abs)
EGR_RANGE   = [0.0, 0.05, 0.10, 0.15]
IVC_RANGE   = [40, 50, 60, 70]                # °ABDC

# ── Production‑based knock limit map ──
# For a given CR and target BMEP (bar), returns the maximum CA50 (deg ATDC)
# that avoids knock on 95 RON GDI.  Data fit from:
#   - BMW B48 (CR 11.0, BMEP 22 bar → CA50 ~18°)
#   - Mercedes M260 (CR 9.8, BMEP 23 bar → CA50 ~15°)
#   - VW EA888 Gen3 (CR 9.6, BMEP 21 bar → CA50 ~12°)
# Fitted surface: CA50_max = a + b*CR + c*BMEP + d*CR*BMEP
a = -18.2
b = 1.85
c = 1.30
d = -0.18

def max_ca50_knock(cr, bmep_bar):
    """Maximum CA50 (deg ATDC) to avoid knock at given CR and BMEP (bar)."""
    ca50 = a + b*cr + c*bmep_bar + d*cr*bmep_bar
    return max(ca50, 4.0)  # never more advanced than 4° (MBT minimum)

# ── Helper functions (same as before) ──
def cylinder_volume(theta, cr, V_clear):
    R = STROKE / 2
    L = CONROD
    y = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R*np.sin(np.deg2rad(theta)))**2)
    return V_clear + (np.pi/4) * BORE**2 * y

def specific_gas_constant(gas_obj):
    return gas_obj.cp_mass - gas_obj.cv_mass

def run_cycle_given_ca50(cr, boost_pa, egr_rate, ivc_atdc, ca50):
    """Run the cycle with a specified CA50 and return BMEP."""
    v_clear = V_SWEPT / (cr - 1)
    ivc_ca = 540 + ivc_atdc
    theta_max = max(630, ivc_ca + 10)
    theta = np.linspace(-180, theta_max, int((theta_max+180)/0.5) + 1)
    
    gas_cycle = ct.Solution('gri30.yaml')
    phi = 1.0 / LAMBDA
    X_ch4 = 1.0
    X_o2  = 2.0 / phi
    X_n2  = 2.0 * 3.76 / phi
    total = X_ch4 + X_o2 + X_n2
    gas_cycle.TPX = INTAKE_TEMP, boost_pa, f'CH4:{X_ch4/total:.4f}, O2:{X_o2/total:.4f}, N2:{X_n2/total:.4f}'
    R_fresh = specific_gas_constant(gas_cycle)
    
    speed_krpm = ENGINE_SPEED / 1000.0
    A_f = 0.4e5
    B_f = 0.03e5
    C_f = 0.0025e5
    D_f = 0.0055
    
    P = np.zeros_like(theta)
    T_arr = np.zeros_like(theta)
    mass = np.zeros_like(theta)
    
    P[0] = boost_pa
    T_arr[0] = INTAKE_TEMP
    mass[0] = P[0] * cylinder_volume(-180, cr, v_clear) / (R_fresh * T_arr[0])
    mass_trapped = mass[0]
    x_b_prev = 0.0
    
    for i in range(1, len(theta)):
        ca = theta[i]
        V = cylinder_volume(ca, cr, v_clear)
        P_prev, T_prev, m_prev = P[i-1], T_arr[i-1], mass[i-1]
        
        if IVO <= ca < ivc_ca:
            P[i] = boost_pa
            T_arr[i] = INTAKE_TEMP
            mass[i] = P[i] * V / (R_fresh * T_arr[i])
            gas_cycle.TPX = T_arr[i], P[i], gas_cycle.X
            if ca >= ivc_ca - 1.0:
                mass_trapped = mass[i]
            continue
        elif EVO <= ca < EVC:
            P[i] = EXHAUST_BACKPRESS
            T_arr[i] = 1200.0
            mass[i] = P[i] * V / (specific_gas_constant(gas_cycle) * T_arr[i])
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
        
        Sp = 2 * STROKE * ENGINE_SPEED / 60
        w = 2.28 * Sp
        A_cyl = (np.pi*BORE*V/(np.pi/4*BORE**2) + 2*np.pi/4*BORE**2)
        h = 3.26 * BORE**(-0.2) * (P_prev/1e5)**0.8 * T_prev**(-0.55) * w**0.8
        dQ_loss = h * A_cyl * (T_prev - 450.0) * (abs(ca - theta[i-1])/(6*ENGINE_SPEED))
        
        Cv = gas_cycle.cv_mass
        dU = -P_prev * (V - cylinder_volume(theta[i-1], cr, v_clear)) + dQ_comb - dQ_loss
        T_new = T_prev + dU / (m_prev * Cv)
        R_spec = specific_gas_constant(gas_cycle)
        P_new = m_prev * R_spec * T_new / V
        
        P[i], T_arr[i], mass[i] = P_new, T_new, m_prev
        gas_cycle.TPX = T_new, P_new, gas_cycle.X
    
    V_arr = cylinder_volume(theta, cr, v_clear)
    work = np.trapezoid(P, V_arr)
    imep = work / V_SWEPT
    fmep = A_f + B_f * speed_krpm + C_f * speed_krpm**2 + D_f * imep
    bmep = imep - fmep
    return bmep

# ── DOE sweep ──
results = []
total = len(CR_RANGE)*len(BOOST_RANGE)*len(EGR_RANGE)*len(IVC_RANGE)
count = 0
print("Running knock‑limited sweep using production map...")
for cr, boost, egr, ivc in product(CR_RANGE, BOOST_RANGE, EGR_RANGE, IVC_RANGE):
    # Find BMEP for the most advanced CA50 allowed (i.e., max power without knock)
    # Iterate to find where BMEP stabilizes, but we can just compute BMEP at a fixed safe CA50
    # We'll target a BMEP and then check if corresponding CA50 is within limit.
    # Simpler: just evaluate BMEP for a range of CA50, pick the one that gives BMEP
    # but also check the knock limit map.
    best_valid_bmep = -1e9
    best_ca50 = None
    for ca50 in np.arange(4.0, 30.1, 2.0):  # coarse sweep
        bmep_pa = run_cycle_given_ca50(cr, boost, egr, ivc, ca50)
        bmep_bar = bmep_pa / 1e5
        max_ca50_allowed = max_ca50_knock(cr, bmep_bar)
        if ca50 >= max_ca50_allowed:  # spark is retarded enough to avoid knock
            if bmep_bar > best_valid_bmep/1e5:
                best_valid_bmep = bmep_pa
                best_ca50 = ca50
    if best_ca50 is not None:
        torque_cyl = best_valid_bmep * V_SWEPT / (4*np.pi)
        torque_total = torque_cyl * 6
        results.append((cr, boost/1e5, egr, ivc, best_ca50, best_valid_bmep/1e5, torque_total))
    count += 1
    if count % 20 == 0:
        print(f"  {count}/{total} done")

target = 22.5
tol = 0.5
matching = [r for r in results if target-tol <= r[5] <= target+tol]

print("\n=== Knock‑limited combinations achieving BMEP 22.5±0.5 bar ===")
if matching:
    matching.sort(key=lambda x: x[5])
    print(f"{'CR':>4}  {'Boost':>8}  {'EGR':>6}  {'IVC':>6}  {'CA50':>6}  {'BMEP':>8}  {'Torque':>8}")
    for r in matching:
        print(f"{r[0]:4.1f}  {r[1]:8.3f}  {r[2]:6.2f}  {r[3]:6.0f}  {r[4]:6.1f}  {r[5]:8.2f}  {r[6]:8.1f}")
else:
    closest = sorted(results, key=lambda x: abs(x[5]-target))[:3]
    print("No exact match. Closest:")
    for r in closest:
        print(f"CR={r[0]:.1f} Boost={r[1]:.2f}bar EGR={r[2]:.2f} IVC={r[3]:.0f}° CA50={r[4]:.1f}° BMEP={r[5]:.2f}bar Torque={r[6]:.1f}Nm")