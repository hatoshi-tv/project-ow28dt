"""
Single-Cylinder 0D Engine Cycle Simulator
Flat-6 Boxer Project – Custom GT-Power Alternative
Uses Cantera for real gas properties, Wiebe combustion, Woschni heat transfer,
and Chen-Flynn friction. Outputs IMEP, BMEP, torque, and P-V diagram.
"""

import cantera as ct
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Engine Geometry & Operating Point (84 × 84 mm flat-6 single cylinder)
# =============================================================================
BORE = 0.084          # m
STROKE = 0.084        # m
CONROD = 0.144        # m (lambda = 1.71 for boxer)
CR = 9.5              # geometric compression ratio (will be swept)
V_CLEARANCE = (np.pi/4 * BORE**2 * STROKE) / (CR - 1)  # clearance volume
V_SWEPT = np.pi/4 * BORE**2 * STROKE
ENGINE_SPEED = 4000   # RPM (peak torque target)
BOOST_PRESSURE = 1.86e5  # Pa (absolute) – initial guess for 22.5 bar BMEP

# Valve timings (deg ATDC intake stroke, using 0 = TDC compression start)
# Typical performance FI engine: intake open -20, close -200 (late IVC 60° ABDC)
IVO = -20   # intake opens 20° BTDC (overlap)
IVC = 240   # intake closes 60° ABDC (60° after BDC) -> Miller cycle
EVO = 480   # exhaust opens 60° BBDC (before BDC)
EVC = 10    # exhaust closes 10° ATDC (overlap)

# Operating conditions
INTAKE_TEMP = 313      # K (after intercooler)
INTAKE_PRESSURE = BOOST_PRESSURE
EXHAUST_BACKPRESSURE = 1.1e5  # Pa (assume low backpressure with twinscroll)

# Wiebe combustion parameters
CA50 = 8.0              # crank angle of 50% burn (deg ATDC – knock limited)
COMB_DURATION = 30     # 10-90% burn duration in CA degrees (fast for tumble)
WIEBE_M = 2.0           # shape factor (typical for SI)
WIEBE_A = 5.0           # efficiency factor (1 - exp(-A) ~ 0.99 at end)

# EGR fraction
EGR_RATE = 0.10         # 10% external EGR

# =============================================================================
# Cantera Gas Setup (air + fuel surrogate: iso-octane with N2/O2)
# =============================================================================
# We'll use a simple "gasoline" as iso-octane for now. For knock later, 
# we will switch to a detailed mechanism.
gas = ct.Solution('gri30.yaml', 'gri30')  # includes n-heptane/iso-octane?
# GRI30 doesn't have iso-octane. We'll create a custom mixture using 
# 'air' and 'ic8h18' from a different file. Use 'n-heptane' for now as surrogate.
try:
    gas = ct.Solution('h2o2.yaml')  # fallback, we need a simple one
    # Better: use Cantera's built-in "gasoline" surrogate from the 'fuel' database.
    # Let's build from scratch with ideal gas.
except:
    # Fallback: manually define properties if no mechanism.
    pass

# For simplicity and immediate execution, we'll use an ideal gas with 
# constant properties but compute mixture composition using Cantera's 
# elemental mole fractions. This is a reasonable approximation for the 
# thermodynamic cycle without knock chemistry.
fuel_species = 'c8h18' if 'c8h18' in ct.Species.list_from_file('nasa_gas.yaml') else 'ch4'
# Actually, we can use 'nC7H16' from GRI30? No, GRI30 has CH4, C2H6, etc.
# Let's use a simple approach: define air as O2:1, N2:3.76, and fuel as 
# iso-octane from the 'nasa_gas.yaml' database. Cantera ships with 
# 'nasa_gas.yaml' which contains many species.

# Load from nasa_gas.yaml (always available)
gas = ct.Solution('nasa_gas.yaml', 'air')
# Add fuel species (iso-octane)
if 'c8h18' in ct.Species.list_from_file('nasa_gas.yaml'):
    gas = ct.Solution('nasa_gas.yaml', 'c8h18:1, air:14.7')  # stoichiometric
else:
    # Use n-heptane as substitute
    gas = ct.Solution('nasa_gas.yaml', 'nC7H16:1, air:15.1')  # stoichiometric
    print("Using n-heptane surrogate for gasoline.")

# Set the correct stoichiometry with EGR
# We want to operate slightly rich (lambda 0.85-0.9 at full load)
LAMBDA = 0.9
AFR_STOICH = 14.7  # approx
FUEL_MASS_FRAC = 1.0 / (1 + AFR_STOICH * LAMBDA)
AIR_MASS_FRAC = 1.0 - FUEL_MASS_FRAC

# For gas composition, we'll just use air+fuel at appropriate equivalence ratio
# Later we can add EGR by recirculating burnt gas composition.

# =============================================================================
# Crank Angle Setup
# =============================================================================
theta_deg = np.linspace(-180, 540, 1440)  # two revolutions, 0.5 deg step
theta_rad = np.deg2rad(theta_deg)

# =============================================================================
# Volume Function
# =============================================================================
def cylinder_volume(theta):
    """Return cylinder volume (m^3) at crank angle theta (deg, 0 = TDC compression)."""
    R = STROKE / 2
    L = CONROD
    term = R * (1 - np.cos(np.deg2rad(theta))) + L - np.sqrt(L**2 - (R * np.sin(np.deg2rad(theta)))**2)
    return V_CLEARANCE + (np.pi/4) * BORE**2 * term

# =============================================================================
# Gas Exchange Model (simplified: constant intake/exhaust pressure)
# =============================================================================
def apply_gas_exchange(theta, P_cyl, T_cyl, mass_cyl, gas_cyl):
    """Simple valve flow: if intake valve open, set P,T to intake conditions 
    if cylinder pressure lower, else keep closed."""
    # Intake stroke: IVO < theta < IVC (in intake stroke, after exhaust)
    if IVO <= theta < IVC:
        # Intake valve open: if during intake stroke (theta 0-180 after TDC intake)
        # We just reset to intake conditions if cylinder pressure lower
        if P_cyl < INTAKE_PRESSURE:
            P_cyl = INTAKE_PRESSURE
            T_cyl = INTAKE_TEMP
            mass_cyl = P_cyl * cylinder_volume(theta) / (gas_cyl.R * T_cyl)
            gas_cyl.TPX = T_cyl, P_cyl, 'air:1'  # fresh charge
    # Exhaust stroke: EVO < theta < EVC
    elif EVO <= theta < EVC:
        # Exhaust valve open: blowdown and displacement - simplified
        P_cyl = EXHAUST_BACKPRESSURE
        T_cyl = 1200  # approximate residual gas temperature
        mass_cyl = P_cyl * cylinder_volume(theta) / (gas_cyl.R * T_cyl)
        gas_cyl.TPX = T_cyl, P_cyl, 'air:1'  # burned gas (simplified)
    return P_cyl, T_cyl, mass_cyl, gas_cyl

# =============================================================================
# Main Cycle Loop
# =============================================================================
def run_cycle():
    # Initialize arrays
    n = len(theta_deg)
    P = np.zeros(n)
    T = np.zeros(n)
    mass = np.zeros(n)
    
    # Start at beginning of compression stroke (-180 deg)
    T0 = INTAKE_TEMP
    P0 = INTAKE_PRESSURE
    gas_work = ct.Solution('nasa_gas.yaml', 'air')
    gas_work.TPX = T0, P0, 'air:1'
    mass0 = P0 * cylinder_volume(-180) / (gas_work.R * T0)
    
    P[0], T[0], mass[0] = P0, T0, mass0
    
    # Friction model (Chen-Flynn simplified)
    FMEP_const = 0.4e5  # bar -> Pa
    FMEP_speed = 0.005e5 * ENGINE_SPEED
    FMEP_bmep = 0.0
    
    # Combustion flag
    burn_start = 0
    burn_end = 0
    CA50_index = int(np.argmin(np.abs(theta_deg - CA50)))
    
    for i in range(1, n):
        theta = theta_deg[i]
        V = cylinder_volume(theta)
        dtheta = theta_deg[i] - theta_deg[i-1]
        
        # Previous state
        P_prev, T_prev, m_prev = P[i-1], T[i-1], mass[i-1]
        gas = ct.Solution('nasa_gas.yaml', 'air')
        gas.TPX = T_prev, P_prev, gas_work.X
        
        # Gas exchange override at start of each phase
        if (theta > IVO and theta < IVC) or (theta > EVO and theta < EVC):
            P[i], T[i], mass[i], gas_work = apply_gas_exchange(theta, P_prev, T_prev, m_prev, gas)
            continue
        
        # Compression / expansion with heat release and heat loss
        # Heat release from Wiebe function
        if theta >= CA50 - COMB_DURATION/2 and theta <= CA50 + COMB_DURATION/2:
            x_b = 1.0 - np.exp(-WIEBE_A * ((theta - (CA50 - COMB_DURATION/2))/COMB_DURATION)**WIEBE_M)
            dQ_comb = (LAMBDA * FUEL_MASS_FRAC * mass0 * 44e6) * (x_b - (0 if i==0 else x_b_prev))  # J
            x_b_prev = x_b
        else:
            dQ_comb = 0
        
        # Heat transfer (Woschni)
        # Mean piston speed (m/s)
        Sp = 2 * STROKE * ENGINE_SPEED / 60
        # Woschni correlation for gas velocity
        w = 2.28 * Sp  # during compression/expansion (simplified)
        if theta > CA50 - COMB_DURATION/2 and theta < CA50 + COMB_DURATION/2:
            # during combustion
            p_motored = P_prev * (V / cylinder_volume(theta_deg[i-1]))**(-1.35)  # approximate
            w = 2.28 * Sp + 3.24e-3 * (V * (P_prev - p_motored) / (cylinder_volume(theta_deg[i-1]) * T_prev))
        
        A_cyl = np.pi * BORE * (cylinder_volume(theta) / (np.pi/4 * BORE**2)) + 2 * np.pi/4 * BORE**2  # approx area
        h = 3.26 * BORE**(-0.2) * (P_prev*1e-5)**0.8 * T_prev**(-0.55) * w**0.8  # Woschni 1978
        T_wall = 450  # K (coolant)
        dQ_loss = h * A_cyl * (T_prev - T_wall) * (dtheta/6)  # W -> J (since dtheta in degrees, time step = dtheta/(6*RPM))
        
        # Energy balance (first law for closed system, ignoring composition change)
        dU = -P_prev * (V - cylinder_volume(theta_deg[i-1])) + dQ_comb - dQ_loss
        # New temperature
        Cv = gas.cv_mass
        T_new = T_prev + dU / (m_prev * Cv)
        # New pressure (ideal gas)
        P_new = m_prev * gas.R * T_new / V
        
        # Store
        P[i] = P_new
        T[i] = T_new
        mass[i] = m_prev
        gas_work.TPX = T_new, P_new, gas.X
    
    # Compute indicated work (closed cycle only)
    work = np.trapz(P, cylinder_volume(theta_deg))
    IMEP = work / V_SWEPT
    FMEP = FMEP_const + FMEP_speed  # simplified
    BMEP = IMEP - FMEP
    torque = BMEP * V_SWEPT / (4*np.pi)  # per cylinder, Nm
    power_kw = BMEP * V_SWEPT * ENGINE_SPEED / (2 * 60) / 1000  # kW per cylinder
    
    return theta_deg, P, T, IMEP, BMEP, torque, power_kw

# =============================================================================
# Run and Output
# =============================================================================
theta, P, T, IMEP, BMEP, torque_cyl, power_cyl = run_cycle()

print(f"--- Single-Cylinder Results @ {ENGINE_SPEED} RPM ---")
print(f"IMEP: {IMEP*1e-5:.2f} bar")
print(f"FMEP: {(0.4 + 0.005*ENGINE_SPEED):.2f} bar")
print(f"BMEP: {BMEP*1e-5:.2f} bar")
print(f"Torque (per cylinder): {torque_cyl:.1f} Nm")
print(f"Torque (6 cylinders): {torque_cyl*6:.1f} Nm")
print(f"Power (6 cylinders): {power_cyl*6:.1f} kW ({power_cyl*6/0.7457:.1f} hp)")

# Plot P-V diagram
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.plot(cylinder_volume(theta), P*1e-5)
plt.xlabel('Volume (m^3)')
plt.ylabel('Pressure (bar)')
plt.title('P-V Diagram')
plt.grid(True)

plt.subplot(1,2,2)
plt.plot(theta, P*1e-5)
plt.axvline(CA50, color='red', linestyle='--', label='CA50')
plt.xlabel('Crank Angle (deg)')
plt.ylabel('Pressure (bar)')
plt.title('Pressure Trace')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()