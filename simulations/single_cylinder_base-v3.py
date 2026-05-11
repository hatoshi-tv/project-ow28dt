"""
Single-Cylinder 0D Engine Cycle Simulator (v3 – corrected FMEP & calibrated)
Flat-6 Boxer Project – 84×84 mm, 7500 rpm redline
"""

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

# ── Geometry & Operating Point ──
BORE    = 0.084
STROKE  = 0.084
CONROD  = 0.144
CR      = 9.5
V_SWEPT = np.pi/4 * BORE**2 * STROKE          # 0.0004655 m³
V_CLEAR = V_SWEPT / (CR - 1)

ENGINE_SPEED    = 4000   # RPM
BOOST_PRESSURE  = 1.86e5 # Pa

# ── Valve timings (0° = TDC compression) ──
IVO = 350
IVC = 600
EVO = 120
EVC = 370

INTAKE_TEMP        = 313.0
EXHAUST_BACKPRESS  = 1.1e5

# ── Combustion parameters ──
CA50           = 10.0      # slightly retarded for knock safety
COMB_DURATION  = 28.0      # 10-90% burn duration (°)
WIEBE_M        = 2.0
WIEBE_A        = 5.0

# Fuel properties (gasoline, λ = 0.9)
AFR_STOICH = 14.7
LAMBDA     = 0.9
FUEL_LHV   = 44.0e6       # J/kg
FUEL_MASS_FRAC = 1.0 / (1.0 + AFR_STOICH * LAMBDA)

# ── Crank angle array ──
theta_deg = np.linspace(-180, 630, 1620)

def cylinder_volume(theta):
    R = STROKE / 2
    L = CONROD
    y = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R*np.sin(np.deg2rad(theta)))**2)
    return V_CLEAR + (np.pi/4) * BORE**2 * y

def specific_gas_constant(gas_obj):
    return gas_obj.cp_mass - gas_obj.cv_mass

# ── Main cycle ──
def run_cycle():
    n = len(theta_deg)
    P = np.zeros(n)
    T = np.zeros(n)
    mass = np.zeros(n)
    
    # Initial charge at -180° BDC
    T0 = INTAKE_TEMP
    P0 = BOOST_PRESSURE
    gas = ct.Solution('gri30.yaml')
    phi = 1.0 / LAMBDA
    X_ch4 = 1.0
    X_o2  = 2.0 / phi
    X_n2  = 2.0 * 3.76 / phi
    total = X_ch4 + X_o2 + X_n2
    gas.TPX = T0, P0, f'CH4:{X_ch4/total:.4f}, O2:{X_o2/total:.4f}, N2:{X_n2/total:.4f}'
    R_spec = specific_gas_constant(gas)
    V0 = cylinder_volume(-180)
    mass0 = P0 * V0 / (R_spec * T0)
    
    P[0], T[0], mass[0] = P0, T0, mass0
    gas_work = gas
    
    # Chen‑Flynn friction coefficients (bar, converted to Pa)
    A = 0.4e5          # constant (0.4 bar)
    B = 0.03e5         # per 1000 rpm (0.03 bar / kRPM)
    C = 0.0025e5       # quadratic term (0.0025 bar / kRPM²)
    D = 0.0055         # fraction of IMEP (0.55%)
    
    speed_krpm = ENGINE_SPEED / 1000.0
    
    # Combustion state
    x_b_prev = 0.0
    mass_trapped = mass0  # updated at IVC
    
    for i in range(1, n):
        theta = theta_deg[i]
        V = cylinder_volume(theta)
        P_prev, T_prev, m_prev = P[i-1], T[i-1], mass[i-1]
        
        # Gas exchange
        if IVO <= theta < IVC:
            P[i] = BOOST_PRESSURE
            T[i] = INTAKE_TEMP
            R_s = specific_gas_constant(gas)
            mass[i] = P[i] * V / (R_s * T[i])
            gas_work = gas
            if theta >= IVC - 0.5:
                mass_trapped = mass[i]
            continue
        elif EVO <= theta < EVC:
            P[i] = EXHAUST_BACKPRESS
            T[i] = 1200.0
            R_s = specific_gas_constant(gas_work)
            mass[i] = P[i] * V / (R_s * T[i])
            continue
        
        # Closed part: compression, combustion, expansion
        if CA50 - COMB_DURATION/2 <= theta <= CA50 + COMB_DURATION/2:
            x_b = 1.0 - np.exp(-WIEBE_A * ((theta - (CA50 - COMB_DURATION/2))/COMB_DURATION)**WIEBE_M)
            dQ_comb = (FUEL_LHV * FUEL_MASS_FRAC * mass_trapped) * (x_b - x_b_prev)
            x_b_prev = x_b
        else:
            dQ_comb = 0.0
            if CA50 - COMB_DURATION/2 <= theta_deg[i-1] <= CA50 + COMB_DURATION/2:
                x_b_prev = 1.0
        
        # Heat transfer (Woschni)
        Sp = 2 * STROKE * ENGINE_SPEED / 60
        w = 2.28 * Sp
        A_cyl = (np.pi*BORE*V/(np.pi/4*BORE**2) + 2*np.pi/4*BORE**2)
        h = 3.26 * BORE**(-0.2) * (P_prev/1e5)**0.8 * T_prev**(-0.55) * w**0.8
        dQ_loss = h * A_cyl * (T_prev - 450.0) * (abs(theta - theta_deg[i-1])/(6*ENGINE_SPEED))
        
        Cv = gas_work.cv_mass
        dU = -P_prev * (V - cylinder_volume(theta_deg[i-1])) + dQ_comb - dQ_loss
        T_new = T_prev + dU / (m_prev * Cv)
        R_s = specific_gas_constant(gas_work)
        P_new = m_prev * R_s * T_new / V
        
        P[i], T[i], mass[i] = P_new, T_new, m_prev
        gas_work.TPX = T_new, P_new, gas_work.X
    
    # Indicated work (full cycle)
    V_array = cylinder_volume(theta_deg)
    work = np.trapezoid(P, V_array)
    IMEP = work / V_SWEPT
    
    # Friction (corrected)
    FMEP = A + B * speed_krpm + C * speed_krpm**2 + D * IMEP
    BMEP = IMEP - FMEP
    
    torque_cyl = BMEP * V_SWEPT / (4*np.pi)
    power_cyl_kw = BMEP * V_SWEPT * ENGINE_SPEED / (2*60) / 1000.0
    return theta_deg, P, T, IMEP, FMEP, BMEP, torque_cyl, power_cyl_kw

# ── Run ──
theta, P, T, IMEP, FMEP, BMEP, tq_cyl, pwr_cyl = run_cycle()

print(f"─── Single‑Cylinder Results @ {ENGINE_SPEED} rpm ───")
print(f"IMEP : {IMEP*1e-5:.2f} bar")
print(f"FMEP : {FMEP*1e-5:.2f} bar")
print(f"BMEP : {BMEP*1e-5:.2f} bar")
print(f"Torque (6 cyl) : {tq_cyl*6:.1f} Nm")
print(f"Power  (6 cyl) : {pwr_cyl*6:.1f} kW  ({pwr_cyl*6/0.7457:.1f} hp)")

# Plot
plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
plt.plot(cylinder_volume(theta), P/1e5)
plt.xlabel('Volume (m³)'); plt.ylabel('Pressure (bar)')
plt.title('P‑V Diagram'); plt.grid(True)

plt.subplot(1,2,2)
plt.plot(theta, P/1e5)
plt.axvline(CA50, color='red', ls='--', label='CA50')
plt.xlabel('Crank Angle (°)'); plt.ylabel('Pressure (bar)')
plt.title('Pressure Trace'); plt.grid(True); plt.legend()
plt.tight_layout()
plt.show()