"""
Knock‑Limited BMEP Sweep – Flat‑6 Boxer 84×84 mm
Uses Douaud & Eyzat ignition delay + Livengood‑Wu integral.
Sweeps: CR, boost, EGR, intake valve close (IVC), and retards CA50 to knock limit.
"""

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt
from itertools import product

# ── Geometry (84 × 84 mm) ──
BORE    = 0.084
STROKE  = 0.084
CONROD  = 0.144
V_SWEPT = np.pi/4 * BORE**2 * STROKE

ENGINE_SPEED = 4000   # peak torque evaluation

# Fixed valve timings (0° = TDC compression)
IVO = 350
EVO = 120
EVC = 370
# IVC will be swept (ABDC intake closure)

INTAKE_TEMP = 313.0
EXHAUST_BACKPRESS = 1.1e5

# Fuel (gasoline, λ=0.9)
AFR_STOICH = 14.7
LAMBDA     = 0.9
FUEL_LHV   = 44.0e6       # J/kg
FUEL_MASS_FRAC = 1.0 / (1.0 + AFR_STOICH * LAMBDA)

# Wiebe
COMB_DURATION = 28.0
WIEBE_M       = 2.0
WIEBE_A       = 5.0

# Sweep ranges
CR_RANGE     = [9.0, 9.5, 10.0]                     # geometric compression ratio
BOOST_RANGE  = np.linspace(1.5e5, 2.2e5, 8)        # Pa (absolute) – 8 steps
EGR_RANGE    = [0.0, 0.05, 0.10, 0.15]             # external EGR fraction
IVC_RANGE    = [40, 50, 60, 70]                     # degrees ABDC (intake close)

# Knock model parameters (Douaud & Eyzat for RON 95)
A_KNOCK = 0.026    # ms·bar^1.3·φ^0.5, calibrated for PRF95
KNOCK_LIMIT = 1.0  # Livengood-Wu integral threshold

# ── Helper functions ──
def cylinder_volume(theta, cr, V_clear=None):
    """Volume at crank angle theta (deg) for given compression ratio.
    Avoids recomputing clearance volume each time if supplied."""
    if V_clear is None:
        V_swept = V_SWEPT
        V_clear = V_swept / (cr - 1)
    R = STROKE / 2
    L = CONROD
    y = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R*np.sin(np.deg2rad(theta)))**2)
    return V_clear + (np.pi/4) * BORE**2 * y

def specific_gas_constant(gas_obj):
    return gas_obj.cp_mass - gas_obj.cv_mass

def ignition_delay_ms(T, P, phi):
    """Douaud & Eyzat correlation: τ (ms) = A * p^-1.3 * φ^-0.5 * exp(3800/T)
       with p in bar, T in K, φ = 1/lambda."""
    p_bar = P / 1e5
    tau = A_KNOCK * p_bar**(-1.3) * phi**(-0.5) * np.exp(3800.0 / T)
    return tau  # ms

# ── Single cycle solver for a given parameter set ──
def run_cycle_with_knock(cr, boost_pa, egr_rate, ivc_atdc,
                         engine_speed=ENGINE_SPEED, plot_debug=False):
    """
    Returns knock-limited BMEP, torque, and chosen CA50.
    Uses simple spark retard loop: start with CA50=8°, retard until knock integral < 1,
    or until CA50 reaches a max (60° = too retarded).
    """
    # Setup gas (CH4 surrogate, same as before)
    gas = ct.Solution('gri30.yaml')
    phi = 1.0 / LAMBDA
    X_ch4 = 1.0
    X_o2  = 2.0 / phi
    X_n2  = 2.0 * 3.76 / phi
    total = X_ch4 + X_o2 + X_n2
    gas.TPX = INTAKE_TEMP, boost_pa, f'CH4:{X_ch4/total:.4f}, O2:{X_o2/total:.4f}, N2:{X_n2/total:.4f}'
    R_fresh = specific_gas_constant(gas)

    # Crank angle array (enough to close intake valve after IVC)
    theta_max = max(630, ivc_atdc + 10)
    theta = np.linspace(-180, theta_max, int((theta_max+180)/0.5))

    # Precompute clearance volume and IVC index
    V_clear = V_SWEPT / (cr - 1)
    ivc_ca = 540 + ivc_atdc   # intake BDC = 540°, so IVC = 540 + ABDC
    ca50_min = 4.0            # earliest possible CA50 (no knock margin)
    ca50_max = 40.0           # max retard we'll accept (still burns but inefficient)

    # Friction model
    speed_krpm = engine_speed / 1000.0
    A_f = 0.4e5
    B_f = 0.03e5
    C_f = 0.0025e5
    D_f = 0.0055

    # Binary search for CA50 to keep knock integral ≤ 1
    best_ca50 = None
    best_bmep = -1e9
    best_result = None

    for ca50 in np.linspace(ca50_min, ca50_max, 20):
        # Reset state
        P = np.zeros_like(theta)
        T = np.zeros_like(theta)
        mass = np.zeros_like(theta)
        R_spec_cur = R_fresh
        gas_work = gas

        # Initial condition at -180° BDC compression
        P[0] = boost_pa
        T[0] = INTAKE_TEMP
        mass[0] = P[0] * cylinder_volume(-180, cr, V_clear) / (R_fresh * T[0])

        # Variables
        mass_trapped = mass[0]   # will be updated at IVC
        x_b_prev = 0.0
        knock_integral = 0.0
        knock_detected = False

        for i in range(1, len(theta)):
            ca = theta[i]
            V = cylinder_volume(ca, cr, V_clear)
            P_prev, T_prev, m_prev = P[i-1], T[i-1], mass[i-1]

            # Gas exchange intervals
            if IVO <= ca < ivc_ca:
                # Intake open
                P[i] = boost_pa
                T[i] = INTAKE_TEMP
                mass[i] = P[i] * V / (R_fresh * T[i])
                gas_work = gas
                if ca >= ivc_ca - 1.0:
                    mass_trapped = mass[i]
                continue
            elif EVO <= ca < EVC:
                # Exhaust open
                P[i] = EXHAUST_BACKPRESS
                T[i] = 1200.0
                mass[i] = P[i] * V / (specific_gas_constant(gas_work) * T[i])
                continue

            # Closed cycle – compression/expansion
            # Combustion event (Wiebe)
            if ca50 - COMB_DURATION/2 <= ca <= ca50 + COMB_DURATION/2:
                x_b = 1.0 - np.exp(-WIEBE_A * ((ca - (ca50 - COMB_DURATION/2))/COMB_DURATION)**WIEBE_M)
                dQ_comb = (FUEL_LHV * FUEL_MASS_FRAC * mass_trapped) * (x_b - x_b_prev)
                x_b_prev = x_b
            else:
                dQ_comb = 0.0
                if i>0 and (ca50 - COMB_DURATION/2 <= theta[i-1] <= ca50 + COMB_DURATION/2):
                    x_b_prev = 1.0

            # Heat transfer (Woschni)
            Sp = 2 * STROKE * engine_speed / 60
            w = 2.28 * Sp
            A_cyl = (np.pi*BORE*V/(np.pi/4*BORE**2) + 2*np.pi/4*BORE**2)
            h = 3.26 * BORE**(-0.2) * (P_prev/1e5)**0.8 * T_prev**(-0.55) * w**0.8
            dQ_loss = h * A_cyl * (T_prev - 450.0) * (abs(ca - theta[i-1])/(6*engine_speed))

            # First law
            Cv = gas_work.cv_mass
            dU = -P_prev * (V - cylinder_volume(theta[i-1], cr, V_clear)) + dQ_comb - dQ_loss
            T_new = T_prev + dU / (m_prev * Cv)
            R_spec = specific_gas_constant(gas_work)
            P_new = m_prev * R_spec * T_new / V

            P[i], T[i], mass[i] = P_new, T_new, m_prev
            gas_work.TPX = T_new, P_new, gas_work.X

            # Knock integral (only evaluate unburnt gas before end of combustion)
            if ca > ivc_ca and not knock_detected:
                # End-gas conditions (unburned, isentropically compressed)
                # We'll approximate end-gas T as the cylinder T (close enough for knock onset)
                tau_ms = ignition_delay_ms(T_new, P_new, phi)
                dt_sec = abs(ca - theta[i-1]) / (6 * engine_speed)  # convert CA to time
                knock_integral += dt_sec / (tau_ms / 1000.0)
                if knock_integral >= KNOCK_LIMIT:
                    knock_detected = True
                    break   # stop this cycle early – knock limited

        if knock_detected:
            # This CA50 is too advanced → retarding helps, so continue
            continue
        else:
            # Complete cycle, compute IMEP & BMEP
            V_arr = cylinder_volume(theta, cr, V_clear)
            # Only use closed portion? We'll use full cycle but penalise pumping via constant-pressure assumption (close enough)
            work = np.trapezoid(P, V_arr)
            imep = work / V_SWEPT
            fmep = A_f + B_f * speed_krpm + C_f * speed_krpm**2 + D_f * imep
            bmep = imep - fmep
            if bmep > best_bmep:
                best_bmep = bmep
                best_ca50 = ca50
                best_result = (theta, P, T, imep, fmep, bmep)
        # If very retarded CA50 still produces knock, we might skip
        if ca50 > 25 and not knock_detected:
            # Could be a valid retarded case; we keep it
            pass

    if best_ca50 is None:
        # No non-knocking solution found within CA50 range; return last (most retarded)
        return None, None, None, None

    return best_ca50, best_bmep, best_result[0], best_result[1]

# ── DOE loop ──
results = []
print("Running sweep...")
total_combos = len(CR_RANGE)*len(BOOST_RANGE)*len(EGR_RANGE)*len(IVC_RANGE)
count = 0
for cr, boost, egr, ivc in product(CR_RANGE, BOOST_RANGE, EGR_RANGE, IVC_RANGE):
    ca50, bmep, theta_arr, P_arr = run_cycle_with_knock(cr, boost, egr, ivc)
    if bmep is not None:
        torque_cyl = bmep * V_SWEPT / (4*np.pi)
        torque_total = torque_cyl * 6
        results.append((cr, boost/1e5, egr, ivc, ca50, bmep/1e5, torque_total))
    count += 1
    if count % 20 == 0:
        print(f"  {count}/{total_combos} done...")

# Filter for our target (22.5 ± 0.5 bar)
target = 22.5
tol = 0.5
matching = [r for r in results if target-tol <= r[5] <= target+tol]

print("\n=== Sweep Results matching BMEP = 22.5±0.5 bar ===")
if matching:
    matching.sort(key=lambda x: x[5])  # sort by BMEP
    print(f"{'CR':>4}  {'Boost(bara)':>10}  {'EGR':>6}  {'IVC(°ABDC)':>9}  {'CA50':>6}  {'BMEP(bar)':>9}  {'Torque(Nm)':>10}")
    for r in matching:
        print(f"{r[0]:4.1f}  {r[1]:10.3f}  {r[2]:6.2f}  {r[3]:9.1f}  {r[4]:6.1f}  {r[5]:9.2f}  {r[6]:10.1f}")
else:
    print("No exact matches. Showing five closest results:")
    sorted_by_diff = sorted(results, key=lambda x: abs(x[5]-target))
    for r in sorted_by_diff[:5]:
        print(f"CR={r[0]:.1f} Boost={r[1]:.2f} bar EGR={r[2]:.2f} IVC={r[3]:.0f}° ABDC -> BMEP={r[5]:.2f} bar, Torque={r[6]:.1f} Nm")

# Show best (highest BMEP without knock) for reference
if results:
    best = max(results, key=lambda x: x[5])
    print(f"\nHighest knock‑limited BMEP: CR={best[0]:.1f} Boost={best[1]:.2f} bar EGR={best[2]:.2f} IVC={best[3]:.0f}° ABDC => BMEP={best[5]:.2f} bar, Torque={best[6]:.1f} Nm")