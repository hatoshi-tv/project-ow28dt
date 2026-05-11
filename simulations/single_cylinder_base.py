"""
Single-Cylinder 0D Engine Cycle Simulator
Flat-6 Boxer Project – 84×84 mm, 7500 rpm redline
Uses Cantera 'gri30.yaml' for real gas properties + a Wiebe combustion model.
"""

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

# ── Geometry & Operating Point (84 × 84 mm flat-6 single cylinder) ──
BORE    = 0.084          # m
STROKE  = 0.084          # m
CONROD  = 0.144          # m (lambda ≃ 1.71 for a boxer)
CR      = 9.5            # geometric compression ratio (will be swept)
V_SWEPT = np.pi/4 * BORE**2 * STROKE
V_CLEAR = V_SWEPT / (CR - 1)

ENGINE_SPEED    = 4000   # RPM (peak torque target)
BOOST_PRESSURE  = 1.86e5 # Pa (absolute) – initial guess for 22.5 bar BMEP

# Valve timings (degree ATDC compression: 0 = TDC compression)
IVO = -20   # intake opens 20° BTDC (overlap)
IVC = 240   # intake closes 60° ABDC → late Miller cycle
EVO = 480   # exhaust opens 60° BBDC
EVC = 10    # exhaust closes 10° ATDC

INTAKE_TEMP        = 313.0   # K (after intercooler)
EXHAUST_BACKPRESS  = 1.1e5   # Pa (low back‑pressure with twin‑scroll)

# Wiebe parameters
CA50           = 8.0       # deg ATDC (knock‑limited spark advance)
COMB_DURATION  = 30.0      # 10‑90 % burn duration (°)
WIEBE_M        = 2.0        # shape factor
WIEBE_A        = 5.0        # efficiency factor

EGR_RATE = 0.10            # 10 % external EGR

# ── Cantera gas object (GRI‑Mech 3.0 – brings H,C,O,N,Ar species) ──
gas = ct.Solution('gri30.yaml')
gas.TPX = INTAKE_TEMP, BOOST_PRESSURE, 'CH4:0.0, O2:0.21, N2:0.79'
# We'll update the composition to a stoichiometric air‑fuel mixture below.

# ── Crank angle array (0.5° resolution over 2 revs) ──
theta_deg = np.linspace(-180, 540, 1440)
theta_rad = np.deg2rad(theta_deg)

# ── Volume function ──
def cylinder_volume(theta):
    """Volume (m³) at crank angle theta (deg, 0 = TDC compression)."""
    R = STROKE / 2
    L = CONROD
    y = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R*np.sin(np.deg2rad(theta)))**2)
    return V_CLEAR + (np.pi/4) * BORE**2 * y

# ── Main cycle loop ──
def run_cycle():
    n = len(theta_deg)
    P = np.zeros(n)
    T = np.zeros(n)
    mass = np.zeros(n)
    
    # Initial state at start of compression (‑180°)
    T0 = INTAKE_TEMP
    P0 = BOOST_PRESSURE
    gas_init = ct.Solution('gri30.yaml')
    # Fresh charge: lean/stoich mixture of CH4 and air (gasoline surrogate)
    phi = 1.0 / 0.9           # equivalence ratio for λ=0.9
    # Stoichiometric CH4 + 2(O2 + 3.76 N2) → CO2 + 2H2O + 7.52 N2
    X_ch4 = 1.0
    X_o2  = 2.0 / phi
    X_n2  = 2.0 * 3.76 / phi
    total = X_ch4 + X_o2 + X_n2
    gas_init.TPX = T0, P0, f'CH4:{X_ch4/total:.4f}, O2:{X_o2/total:.4f}, N2:{X_n2/total:.4f}'
    mass0 = P0 * cylinder_volume(-180) / (gas_init.R * T0)
    
    P[0], T[0], mass[0] = P0, T0, mass0
    gas_work = gas_init
    
    # Friction (Chen‑Flynn simplified)
    FMEP_const = 0.4e5  # bar → Pa
    FMEP_speed = 0.005e5 * ENGINE_SPEED
    
    for i in range(1, n):
        theta = theta_deg[i]
        V = cylinder_volume(theta)
        P_prev, T_prev, m_prev = P[i-1], T[i-1], mass[i-1]
        
        # Gas exchange: simply reset to intake/exhaust conditions
        if (IVO <= theta < IVC):
            P[i] = BOOST_PRESSURE
            T[i] = INTAKE_TEMP
            mass[i] = P[i] * V / (gas_init.R * T[i])
            gas_work = gas_init
            continue
        elif (EVO <= theta < EVC):
            P[i] = EXHAUST_BACKPRESS
            T[i] = 1200.0
            mass[i] = P[i] * V / (gas_work.R * T[i])
            continue
        
        # Heat release (Wiebe)
        if (CA50 - COMB_DURATION/2 <= theta <= CA50 + COMB_DURATION/2):
            x_b = 1.0 - np.exp(-WIEBE_A * ((theta - (CA50 - COMB_DURATION/2))/COMB_DURATION)**WIEBE_M)
            dQ_comb = (gas_init.R * T0 * m_prev) * (x_b - (0 if i==0 else x_b_prev))  # scaled
            x_b_prev = x_b
        else:
            dQ_comb = 0.0
            if (CA50 - COMB_DURATION/2 <= theta_deg[i-1] <= CA50 + COMB_DURATION/2):
                x_b_prev = 1.0
        
        # Heat transfer (Woschni 1978, simplified)
        Sp = 2 * STROKE * ENGINE_SPEED / 60
        w = 2.28 * Sp
        A_cyl = (np.pi*BORE*cylinder_volume(theta)/(np.pi/4*BORE**2) + 2*np.pi/4*BORE**2)
        h = 3.26 * BORE**(-0.2) * (P_prev/1e5)**0.8 * T_prev**(-0.55) * w**0.8
        dQ_loss = h * A_cyl * (T_prev - 450.0) * (abs(theta-theta_deg[i-1])/(6*ENGINE_SPEED))
        
        # First law (closed system)
        Cv = gas_work.cv_mass
        dU = -P_prev * (V - cylinder_volume(theta_deg[i-1])) + dQ_comb - dQ_loss
        T_new = T_prev + dU / (m_prev * Cv)
        P_new = m_prev * gas_work.R * T_new / V
        
        P[i], T[i], mass[i] = P_new, T_new, m_prev
        gas_work.TPX = T_new, P_new, gas_work.X
    
    # Indicated work (closed cycle only)
    work = np.trapz(P, cylinder_volume(theta_deg))
    IMEP = work / V_SWEPT
    FMEP = FMEP_const + FMEP_speed
    BMEP = IMEP - FMEP
    torque_cyl = BMEP * V_SWEPT / (4*np.pi)         # Nm / cylinder
    power_cyl_kw = BMEP * V_SWEPT * ENGINE_SPEED / (2*60) / 1000   # kW / cyl
    
    return theta_deg, P, T, IMEP, BMEP, torque_cyl, power_cyl_kw

# ── Execute and display ──
theta, P, T, IMEP, BMEP, tq_cyl, pwr_cyl = run_cycle()

print(f"─── Single‑Cylinder Results @ {ENGINE_SPEED} rpm ───")
print(f"IMEP : {IMEP*1e-5:.2f} bar")
print(f"FMEP : {0.4+0.005*ENGINE_SPEED:.2f} bar")
print(f"BMEP : {BMEP*1e-5:.2f} bar")
print(f"Torque (6 cyl) : {tq_cyl*6:.1f} Nm")
print(f"Power  (6 cyl) : {pwr_cyl*6:.1f} kW  ({pwr_cyl*6/0.7457:.1f} hp)")

# P‑V diagram
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