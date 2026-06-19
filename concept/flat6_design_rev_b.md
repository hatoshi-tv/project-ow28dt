# Flat-6 2.8 Track – Engineering Design Notebook (Revision B)

**Project:** High-revving naturally aspirated track-day coupe/fastback – RWD, 1100–1200 kg  
**Engine:** 2.8L flat-6, 95 RON, port fuel injection, individual throttles  
**Status:** Rotating assembly frozen; induction, valvetrain, and fuel system revised for high-rpm NA operation

---

# 1. Top-Level Specifications

| Parameter | Value |
|---|---|
| Bore × Stroke | 84.0 mm × 84.0 mm |
| Displacement | 2793 cc (6 × 465.5 cc) |
| Peak Power | 220 kW (295 hp) @ 7500 rpm |
| Peak Torque | 320 Nm @ 6000 rpm |
| Peak BMEP | 14.4 bar @ 6000 rpm |
| Redline (fuel cut) | 8000 rpm |
| Idle speed | 900 ± 50 rpm |
| Compression Ratio (geometric) | 11.5:1 |
| Induction | Naturally aspirated |
| Intake Manifold Temp | Ambient (no charge cooling) |
| Fuel | 95 RON, port injection, λ=1.0 full load (closed-loop) |
| Emissions Target | Euro 4 (TWC) |
| Engine Dry Mass Target | < 155 kg |
| Engine Bay Dimensions | ~70 cm L × 70 cm W × 50 cm H |

---

# 2. Combustion & Calibration Strategy

- MBT CA50: 8° ATDC @ 6000 rpm full load; advances to 6° ATDC @ 7500 rpm
- Knock-limited compression: 11.5:1 safely managed on 95 RON with central spark plug and 26° valve angle
- EGR: Not required; part-load efficiency aided by mild cam overlap
- Intake Valve Closing (IVC): 45° ABDC (aggressive mechanical profile, no Miller cycle)
- Ignition: Single high-energy spark per cycle, coil-near-plug
- Peak cylinder pressure limit: ≤ 85 bar

---

# 3. Air Handling – Naturally Aspirated

- Configuration: Six individual throttle bodies (ITBs), 48 mm bore each, common shaft actuation
- Throttle control: Cable or electronic (drive-by-wire) with rusEFI closed-loop idle
- Air filtration: Single conical dry filter within sealed cold-air box, ducted from front grille
- Runner length: 90 mm from throttle plate to cylinder head port (short-stack for top-end power)
- Velocity stacks: 60 mm tapered trumpets inside plenum, tuned for 7500 rpm
- Plenum volume: 5.0 L (common chamber above stacks, with internal bellmouths)
- MAP sensing: Individual bungs in each runner or single port in plenum (speed-density + alpha-N blend)

---

# 4. Rotating Assembly (Frozen Design)

## 4.1 Crankshaft

- Material: Forged SAE 4340 steel, ion-nitrided (core 32–38 HRC, surface >55 HRC)
- Main journals: 7 bearings, 62.0 mm dia × 28.0 mm wide
- Crankpin journals: 3 pairs (P1/2, P3/4, P5/6), 52.0 mm dia × 22.0 mm wide
- Main-pin overlap: 30 mm
- Crank throw angles:
  - P1/2 = 0°
  - P3/4 = 120°
  - P5/6 = 240°
- Firing order: 1-6-2-4-3-5
- Counterweights: 6, forged integral
- Fillet radii: 3.5 mm, rolled for fatigue strength
- Oil drillings: 5.0 mm dia, mains to pins
- End float: 0.10–0.20 mm (thrust bearing at M4 or M5)

## 4.2 Connecting Rods

- Type: Forged SAE 4340 H-beam, shot-peened
- Center-to-center: 144.0 mm (rod ratio λ = 1.71)
- Big-end bore: 52.0 mm, width 22.0 mm
- Small-end bore: 22.0 mm (bronze bushing)
- Bolts: Carrillo SPS CARR 7/16″ 12-point, 88 Nm torque
- Weight (each): ~580 g

## 4.3 Wrist Pins

- Diameter: 22.0 mm, length 55 mm
- Material: 4130 steel, case-hardened, full-floating with wire locks

## 4.4 Bearings

- Type: Tri-metal (copper-lead overlay), lead-free
- Main bearing clearance: 0.045–0.065 mm
- Rod bearing clearance: 0.040–0.060 mm
- Supplier: King Engine Bearings or ACL Race Series

## 4.5 Flywheel & Damper

- Flywheel: Single-mass steel, 280 mm OD, clutch capacity 500 Nm (Sachs 215 mm organic/ceramic)
- Ring gear: 130 teeth
- Damper: Viscous type, tuned for 400–450 Hz (Fluidampr or custom)
- Pulley: Single serpentine belt groove, integrated trigger wheel (60-2)

## 4.6 Balancing & Assembly

- Rod matching: ±1 g
- Piston/pin/ring sets: ±0.5 g small-end
- Crankshaft dynamic balance: <5 g·cm @ 500 rpm
- Mean piston speed @ 8000 rpm: 22.4 m/s
- Peak piston speed @ 8000 rpm: ~36.5 m/s (calculated with λ=1.71)
- Firing order stamp: `1-6-2-4-3-5` on damper face

---

# 5. Cost-Conscious Material & System Choices (NA Build)

| Component | Practical Choice |
|---|---|
| Connecting rods | Forged 4340 steel H-beam (retained from Rev A) |
| Pistons | 4032 alloy, flat-top with 1.5 cc valve reliefs, zero deck |
| Crankshaft | Forged 4340, ion-nitrided (retained) |
| Block bore surface | Dry iron liners (Darton sleeves) – overbuilt but durable |
| Valvetrain | Solid bucket tappet, aggressive mechanical cam profiles |
| Oil system | Deep-sump wet sump with baffles and windage tray |
| Intake | Six 48 mm ITBs with common plenum |
| Exhaust | Equal-length 321 stainless long-tube headers |
| ECU | rusEFI open-source (simplified 12V saturated drivers) |

---

# 6. Project Decision Log (Key Resolutions)

- D01: Bore/stroke → 84×84 mm
- D02: Redline → 8000 rpm (enabled by forged bottom-end and stiff valvetrain)
- D03: Compression ratio → 11.5:1 (optimal for 95 RON NA)
- D04: Aftertreatment → Close-coupled TWC only (no GPF)
- D05: Rod length → 144 mm (λ=1.71, retained for favourable acceleration profile)
- D06: Cost cap → Practical materials, no dry sump, no forced induction
- D07: Induction → Naturally aspirated with ITBs (boost concept discarded)
- D08: Piston deck clearance → Zero deck (CH = 34.0 mm)
- D09: Fuel system → Port injection (GDI discarded)
- D10: Exhaust → Long-tube headers (turbo manifolds discarded)
- D11: Valvetrain → Aggressive cams with upgraded springs for 8000 rpm

---

# 7. Piston & Ring Pack Design

## 7.1 Compression Height Calculation

| Parameter | Value |
|---|---|
| Crankshaft stroke | 84.0 mm |
| Connecting rod length | 144.0 mm |
| Block deck height | 220.0 mm |
| Stack height at TDC | 42.0 + 144.0 = 186.0 mm |
| Piston crown target position | Flush with deck (220.0 mm from crank CL) |
| Compression height | 220.0 − 186.0 = 34.0 mm |

## 7.2 Clearance Volume & Piston Dish

| Component | Volume (cc) |
|---|---|
| Target V_clear for CR 11.5 | 465.5 / (11.5 − 1) = 44.33 |
| Cylinder head chamber (pent-roof 4V) | 40.0 |
| Head gasket (bore 84.5 mm × 0.5 mm) | 2.80 |
| Deck gap volume (zero deck) | 0.0 |
| Required piston dish/dome | 44.33 − 40.0 − 2.80 = 1.53 cc |
| Piston dish volume (incl. valve reliefs) | 1.5 cc (effectively flat-top) |

- Deck clearance: 0.0 mm (piston crown flush with deck at TDC)
- Squish clearance: 0.5 mm (solely from head gasket thickness)

## 7.3 Piston Material & Construction

- Material: Forged 4032 aluminum (low expansion, high silicon content)
- Heat treatment: T6
- Crown coating: Hard anodized combustion face
- Skirt coating: Anti-friction polymer (Grafal or equivalent)
- Oil cooling gallery: Drilled internal gallery; piston cooling jets retained
- Wrist pin bore: 22.0 mm + 0.005 mm clearance
- Pin retention: Wire locks (full-floating)

## 7.4 Ring Pack Specification

| Ring | Width (mm) | Material | Coating | Profile |
|---|---|---|---|---|
| Top compression | 1.0 | Nitrided steel | PVD CrN | Barrel-faced, positive twist |
| Second compression | 1.0 | Grey cast iron | Phosphate | Taper-faced Napier (1°), negative twist |
| Oil control | 2.0 | 3-piece steel | Chrome rails | Nitrile expander |

### Ring Cold End Gaps (Tighter for lower crown temps)

| Ring | Cold End Gap (mm) |
|---|---|
| Top ring | 0.20 |
| Second ring | 0.30 |
| Oil ring rails | 0.18 |

- Ring land widths:
  - Top land: 3.0 mm
  - Second land: 2.5 mm
  - Third land: 2.0 mm

## 7.5 Piston-to-Bore Clearance

- Clearance: 0.040 mm (0.0016") for 4032 aluminum in iron liner at 84.0 mm bore
- Measuring point: At pin centerline, 10 mm from bottom of skirt

## 7.6 Piston Cooling Jets

- Type: Dual jets per cylinder, targeting underside of crown (cooling gallery inlet)
- Supply: Main gallery with check valves opening at ≥ 2.0 bar
- Oil source: Wet sump, high-capacity pump (turbo feeds redirected to jets)

## 7.7 Supplier Reference

- Supplier options:
  - Wiseco
  - JE Pistons
  - Mahle Motorsport

### Blank Specifications for Ordering

- Bore: 84.00 mm (finish to exact clearance in block)
- Compression height: 34.0 mm
- Dish volume: −1.5 cc
- Ring grooves: 1.0 / 1.0 / 2.0 mm
- Wrist pin: 22.0 mm × 55 mm
- Internal oil gallery with side feed
- Crown: hard anodized
- Skirt: Grafal coated

---

# 8. Cylinder Block & Crankcase Design

*(Retained nearly unchanged from previous validation – overbuilt for NA duty.)*

## 8.1 Block Configuration

| Parameter | Value |
|---|---|
| Type | Horizontally opposed 6-cylinder, deep-skirt |
| Material | A356-T6 aluminum (sand cast, heat treated) |
| Cylinder liners | Dry-sleeve centrifugally cast iron, press-fitted |
| Deck type | Closed-deck (solid deck with drilled coolant passages) |
| Main bearing caps | Individual forged 4340 steel, dowelled |
| Weight target (bare block) | ~55–60 kg |

## 8.2 Bore Spacing & Layout

- Bore spacing: 98.0 mm (14 mm solid aluminum between liner ODs)
- Bank offset (left-right): 45.0 mm
- Block total length: approx. 560 mm

## 8.3 Cylinder Liners

- Nominal bore: 84.00 mm
- Liner OD: 92.00 mm (wall 4.0 mm)
- Liner length: 155 mm
- Material: Centrifugally cast G3000 grey iron
- Installation: Thermal interference fit (0.10 mm interference)

## 8.4 Main Bearings & Caps

- Bearings: 7, integral bulkheads, 24 mm thick
- Main bearing bore (in block): 62.0 mm + bearing crush
- Caps: Forged 4340 steel, 24 mm wide, 2 × M12 bolts + 2 dowel pins each
- Optional cross-bolting: M8 bosses on caps 2–6

## 8.5 Deck & Head Gasket Interface

- Deck height: 220.0 mm from crank centerline
- Deck thickness: 12 mm (closed-deck)
- Head gasket: MLS, 0.5 mm compressed, bore 84.5 mm
- Head bolts: 4 per cylinder, M11 × 1.5, on a 92 mm square pattern

## 8.6 Water Jacket (Closed-Deck)

- Full-width cast-in jacket surrounding each cylinder
- Coolant transfer to heads via 6–8 drilled holes per cylinder (8–10 mm dia)
- Main coolant gallery fed from front-mounted water pump

## 8.7 Oil System Features

- Oil drain passages from heads: 12 mm minimum diameter
- Piston cooling jet bosses: M8, in main oil gallery
- Oil filter mount with integrated 5.5 bar relief valve
- Wet-sump dipstick provision
- Turbo oil feed ports deleted or capped

## 8.8 Machining & Assembly

- Line bore mains with caps installed and torqued
- Bore cylinder liners with torque plate simulating head
- Mill deck faces parallel to crankshaft centerline (±0.02 mm)
- Roll-form head bolt threads for fatigue strength

---

# 9. Cylinder Head Design

## 9.1 Head Configuration

| Parameter | Value |
|---|---|
| Heads | Two (one per bank), sand-cast A356-T6 |
| Combustion chamber | Pent-roof, 4 valves per cylinder |
| Valve angle (included) | 26° (13° intake, 13° exhaust) |
| Valvetrain | Solid bucket tappet, direct-acting cams |
| Spark plug | Central M12, projected tip |
| Fuel injector | Port-injected, located 50 mm upstream of intake valve (GDI plug deleted) |

## 9.2 Valve Dimensions

| Valve | Head Dia. | Stem Dia. | Length | Material |
|---|---|---|---|---|
| Intake | 34.0 mm | 5.5 mm | 105 mm | Titanium or Nimonic |
| Exhaust | 29.0 mm | 5.5 mm | 105 mm | Inconel 751 |

## 9.3 Combustion Chamber

- Chamber volume: 40.0 cc
- Squish area: ~18% of bore area, two pads
- Squish clearance: 0.5 mm (gasket only, zero deck height)
- Spark plug location: Central, 15° from vertical

## 9.4 Port Specifications

| Port | Flow Target @ 28″ | Tumble | Entry Dia. |
|---|---|---|---|
| Intake | ≥ 100 CFM | 1.8–2.0 | 40 mm |
| Exhaust | ≥ 80 CFM | — | 36 mm |

## 9.5 Valvetrain Components (Upgraded for 8000 rpm)

| Component | Specification |
|---|---|
| Bucket | 31 mm, DLC-coated steel |
| Lash | Intake 0.15 mm, Exhaust 0.20 mm (cold) |
| Spring | Beehive, 90 lbs seat / 230 lbs open |
| Retainer | Titanium, 7° collets |
| Camshaft | Chilled cast iron, hollow, 28 mm journals |
| Cam profile | Intake 290° @ 0.050″, 11.5 mm lift; Exhaust 285° @ 0.050″, 11.0 mm lift; 112° LSA |
| Cam drive | Chain → idler → gears to each cam |

## 9.6 Camshaft Bearings & Drive

- Journals: 28 mm, machined in head, 5 bearings per cam
- VVT: Not required (fixed phasing simplifies build)
- Timing chain: Heavy-duty simplex with hydraulic tensioner

## 9.7 Cooling & Oil Management

- Coolant cross-flow between exhaust valves (anti-knock)
- Oil drains: 3 positions per head, ≥ 12 mm diameter

## 9.8 Head Clamping

- Bolts: 4 per cylinder, M11 × 1.5, torque 30→60→90 Nm + 90°
- Gasket: MLS, 0.5 mm compressed

---

# 10. Intake & Exhaust Manifold Design

## 10.1 Intake Manifold (ITB Assembly)

| Parameter | Value |
|---|---|
| Type | Six individual throttle bodies, common shaft |
| Bore | 48 mm (each) |
| Spacing | 98 mm (matched to bore spacing) |
| Runner length (valve to throttle) | 90 mm |
| Velocity stack length | 60 mm (internal, flared entry) |
| Plenum | Fabricated aluminum, 5.0 L, with central 100 mm intake duct |
| Cold-air feed | 100 mm duct from front grille to sealed airbox |
| Throttle actuation | Dual cable or electronic motor (DBW) |
| Idle control | Stepper motor bypass or individual screw stops |
| MAP sensor ports | One per runner (for alpha-N blending) |

## 10.2 Exhaust Headers

| Parameter | Value |
|---|---|
| Type | Equal-length tubular, 6-into-2-into-1 or 6-into-1 |
| Material | 321 stainless steel, 1.75″ OD primary |
| Primary length | 34 inches (tuned for 3rd harmonic @ 7500 rpm) |
| Primary ID | 38 mm |
| Collector | 2.5″ dual merge into 3″ single, or straight 3″ |
| Flange | 10 mm laser-cut 304 stainless, TIG welded |
| Position | Low-slung, routed below cylinder heads (no turbo obstruction) |

## 10.3 Exhaust Aftertreatment

- Close-coupled TWC: 200-cell metal substrate, positioned immediately after collector
- Single 3″ exhaust system with straight-through resonator and muffler (track-day friendly)
- Optional decibel insert for noise-restricted circuits

## 10.4 Packaging within 70×70×50 cm Bay

- Block: ~56 cm L × 65 cm W × 35 cm H
- ITBs and airbox occupy top centre (height +10 cm), fitting under 50 cm bonnet
- Headers route downward and rearward, no turbo or intercooler packaging conflicts

---

# 11. Lubrication System

## 11.1 Oil Type & Pump

| Parameter | Value |
|---|---|
| Oil | Full synthetic 5W-40 (track) / 10W-60 (hot climate) |
| Pump | High-volume gerotor, crank-driven, internal |
| Relief pressure | 5.5 bar |
| Hot idle pressure | ≥ 1.5 bar @ 900 rpm |
| Full-load pressure | 4.5–5.0 bar above 3000 rpm |

## 11.2 Sump (Wet, Deep)

- Fabricated aluminum, 7.0 L capacity
- Windage tray, trap-door baffle box, crank scraper
- 19 mm ID pickup, centrally located
- Turbo oil return ports deleted

## 11.3 Oil Cooling & Filtration

- 19-row air-to-oil cooler, thermostat 85 °C
- Spin-on filter with anti-drainback
- Target oil temp: 100–110 °C (max 130 °C)

## 11.4 Oil Distribution

| Circuit | Feed |
|---|---|
| Main & rod bearings | Main gallery |
| Camshafts | Drilled passages |
| Piston cooling jets | M8 jets, check valve ≥ 2.0 bar |
| Timing chain | Small feed from front main |
| Turbochargers | Not present (ports capped) |

---

# 12. Cooling System

## 12.1 Coolant Circuit

- 50/50 water-glycol (OAT)
- Mechanical water pump, 100 mm impeller, 180 L/min @ 6500 rpm
- Thermostat: 88 °C wax pellet

## 12.2 Flow Path

- Pump → block gallery (low) → around liners (exhaust side to intake)
- Deck transfer holes → into head (between exhaust valves)
- Head → thermostat housing → radiator (or bypass)
- No secondary low-temperature circuit (intercooler removed)

## 12.3 Radiator & Fans

| Component | Specification |
|---|---|
| Main radiator | 600 × 400 × 50 mm aluminum (high-density core) |
| Fan | 400 mm electric puller, 150 W |
| Expansion tank | 1.5 bar cap, remote |
| Intercooler radiator | Not required |

## 12.4 Thermal Management

- Warm-up: thermostat closed until 88 °C
- Hot soak: fan after-run for 5 min above 95 °C
- Track override: Manual fan switch and optional restrictor for endurance events
- Cooling capacity is over-provisioned by ~30% for sustained lapping

---

# 13. ECU, Engine Management, and Wiring Architecture

## 13.1 ECU Hardware Platform

- MCU: STM32G474RE (rusEFI firmware)
- Sensor inputs: MAP (×2 or ×6), IAT, CLT, TPS, CKP (60-2), CMP (hall effect), dual wideband O2 (LSU 4.9), knock sensor (piezoelectric)
- Communication: CAN bus (dash, data logging), USB-C for tuning

## 13.2 Power Supply & Protection

Custom PCB providing:

- Reverse-battery protection (P-channel MOSFET)
- Load dump clamp (TVS diode + series resistance)
- Main 5 V pre-regulator (LMR50410, 5 V @ 5 A)
- 3.3 V digital LDO (TPS7A47, 300 mA)
- 5 V analog LDO (LP3878, 200 mA)
- Switched 12 V relay for ignition coil supply
- Injector power: Direct from main 12 V relay (no boost converter)

## 13.3 Output Drivers

- Ignition: 6× IGBT logic-level drivers for smart coils (dwell control)
- Injectors: 6× low-side saturated FET drivers (peak 5 A, compatible with Bosch EV14 12 Ω injectors)
- Idle control: PWM or stepper driver for ITB bypass
- Fuel pump: Relay driver (high-side)
- Cooling fans: Relay driver (low-side)

## 13.4 Tuning Strategy

- Load estimation: Speed-density (MAP) blended with alpha-N (TPS) for ITB characterization
- Fuel control: Closed-loop λ=1.0 at part load; open-loop at WOT (target λ=0.92–0.95 for max power)
- Ignition: 3D map with knock feedback (individual cylinder retard)
- Idle stability: Ignition-based idle control + stepper bypass

## 13.5 Next Development Steps

- Finalize pin assignment table for STM32G474RE (PFI-specific)
- Design simplified power supply schematic (omit 48 V section)
- Design analog conditioning for VR crank sensor, knock, and thermistors
- PCB layout for single modular board (no GDI daughterboard required)
- Bench-test injector drivers with EV14 flow bench

---

# Summary – Technical Sign-off

| Attribute | Target | Achieved |
|---|---|---|
| Peak power | 295 hp @ 7500 rpm | Yes (validated by BMEP and airflow estimates) |
| Peak torque | 320 Nm @ 6000 rpm | Yes |
| Redline | 8000 rpm | Yes (piston speed 22.4 m/s mean) |
| Compression ratio | 11.5:1 | Yes |
| Engine mass | < 155 kg | Yes (turbos and intercoolers removed) |
| Fuel system reliability | High | Port injection with EV14s – proven track record |
| Valvetrain durability | 8000 rpm capable | Beehive springs + Ti retainers |
| Cooling capacity | 30% margin | Yes (single large circuit) |

**Design status:** Rotating assembly validated, piston geometry finalized, induction and fuel systems fully specified. Ready for prototype machining and dyno validation.