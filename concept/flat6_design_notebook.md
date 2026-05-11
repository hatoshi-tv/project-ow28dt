# Flat-6 2.8 Rally – Engineering Design Notebook

**Project:** Daily-use automobile with rally genes – custom coupe/fastback, RWD/AWD, 1200-1350 kg  
**Engine:** Twin-turbocharged 2.8L flat-6, 95 RON, Euro 5  
**Status:** Rotating assembly frozen; piston design next  

---

## 1. Top-Level Specifications

| Parameter | Value |
|-----------|-------|
| Bore × Stroke | 84.0 mm × 84.0 mm |
| Displacement | 2793 cc (6 × 465.5 cc) |
| Peak Power | 340 kW (456 hp) @ 6500 rpm |
| Peak Torque | 500 Nm @ 4000–6500 rpm |
| Peak BMEP | 22.5 bar @ 4000 rpm |
| Redline (fuel cut) | 7500 rpm |
| Idle speed | 800 ± 50 rpm |
| Compression Ratio (geometric) | 9.5:1 |
| Boost Pressure (abs) | 1.75 bar @ 4000 rpm; 2.0 bar @ 6500 rpm |
| Intake Manifold Temp | ≤ 40 °C (after intercooler) |
| Fuel | 95 RON, direct injection, λ=0.9 full load |
| Emissions Target | Euro 5 (TWC + optional GPF) |
| Engine Dry Mass Target | < 200 kg (cost-conscious build ~185 kg) |
| Engine Bay Dimensions | ~70 cm L × 70 cm W × 50 cm H |

---

## 2. Combustion & Knock Strategy

- **Knock-limited CA50:** 18° ATDC @ 4000 rpm full load (12° ATDC @ 6500 rpm)
- **EGR:** Cooled high-pressure EGR, 10% rate @ 4000 rpm, 5% @ 6500 rpm
- **Intake Valve Closing (IVC):** 60° ABDC (Miller cycle)
- **Ignition:** Central spark plug, direct injection with multiple pulses per cycle
- **Peak cylinder pressure limit:** ≤ 120 bar

---

## 3. Air Handling & Turbocharging

- **Configuration:** One twin-scroll turbo per cylinder bank (two units)
- **Compressor flow target (each):** 0.17 kg/s @ PR 2.0–2.2
- **Candidate turbos:** BorgWarner K04 or Garrett GTX2860R (cost‑conscious choice)
- **Intercooler:** Air‑to‑water (water‑cooled, separate low‑temp circuit)
- **Anti‑lag:** No electric assist – mild 48V crank‑mounted MGU optional for transient fill

---

## 4. Rotating Assembly (Frozen Design)

### 4.1 Crankshaft
- **Material:** Forged SAE 4340 steel, ion‑nitrided (core 32‑38 HRC, surface >55 HRC)
- **Main journals:** 7 bearings, 62.0 mm dia × 28.0 mm wide
- **Crankpin journals:** 3 pairs (P1/2, P3/4, P5/6), 52.0 mm dia × 22.0 mm wide
- **Main‑pin overlap:** 30 mm
- **Crank throw angles:** P1/2 = 0°, P3/4 = 120°, P5/6 = 240°
- **Firing order:** 1‑6‑2‑4‑3‑5 (perfect inherent balance)
- **Counterweights:** 6, forged integral
- **Fillet radii:** 3.5 mm, rolled
- **Oil drillings:** 5.0 mm dia, mains to pins
- **End float:** 0.10–0.20 mm (thrust bearing at M4 or M5)

### 4.2 Connecting Rods
- **Type:** Forged SAE 4340 H‑beam, shot‑peened
- **Center‑to‑center:** 144.0 mm (rod ratio λ = 1.71)
- **Big‑end bore:** 52.0 mm, width 22.0 mm
- **Small‑end bore:** 22.0 mm (bronze bushing)
- **Bolts:** Carrillo SPS CARR 7/16″ 12‑point, 88 Nm torque
- **Supplier/Part:** Carrillo custom 5.669″ (144 mm) or Manley equivalent
- **Weight (each):** ~580 g

### 4.3 Wrist Pins
- **Diameter:** 22.0 mm, length 55 mm
- **Material:** 4130 steel, case‑hardened, full‑floating (wire locks)

### 4.4 Bearings
- **Type:** Tri‑metal (copper‑lead overlay), lead‑free
- **Main bearing:** 62.0 × 28.0 × 2.0 mm, clearance 0.045–0.065 mm
- **Rod bearing:** 52.0 × 22.0 × 1.8 mm, clearance 0.040–0.060 mm
- **Supplier:** King Engine Bearings or ACL Race Series

### 4.5 Flywheel & Damper
- **Flywheel:** Single‑mass steel, 280 mm OD, clutch capacity 600 Nm (Sachs 215 mm)
- **Ring gear:** 130 teeth
- **Damper:** Viscous type, tuned for 380–420 Hz (Fluidampr or custom)
- **Pulley:** Single serpentine belt groove

### 4.6 Balancing & Assembly
- **Rod matching:** ±1 g
- **Piston/pin/ring sets:** ±0.5 g small‑end
- **Crankshaft dynamic balance:** <5 g·cm @ 500 rpm
- **Firing order stamp:** “1‑6‑2‑4‑3‑5” on damper

---

## 5. Cost‑Conscious Material/System Choices

| Component | Original “Ultimate” | Practical Choice |
|-----------|---------------------|------------------|
| Connecting rods | Titanium Ti‑6Al‑4V | Forged 4340 steel H‑beam |
| Pistons | 2618 alloy + DLC pin | 4032 alloy, anodized, standard pin |
| Crankshaft | Billet 4340 | Forged 4340, ion‑nitrided |
| Block bore surface | Nikasil plating | Dry iron liners (Darton sleeves) |
| Valvetrain | Finger follower + HLA | Solid bucket tappet, shim adjustment |
| Oil system | Dry sump | Deep‑sump wet sump with baffles |
| Turbochargers | Garrett G25‑550 + e‑motor | BorgWarner K04 / GTX2860R (no e‑assist) |
| ECU | Motec M182 | RusEFI open‑source |

---

## 6. Project Decision Log (Key Resolutions)

- D01: Bore/stroke → 84×84 mm (user choice)
- D02: Redline → 7500 rpm (compromise for durability)
- D03: Compression ratio → 9.5:1 (knock‑limited for 95 RON at 22.5 bar BMEP)
- D04: EGR & aftertreatment → Cooled HP‑EGR, close‑coupled TWC, GPF optional
- D05: Rod length → 144 mm (λ=1.71)
- D06: Cost cap → Practical materials, no dry sump, no e‑turbo

---

*Next section: Piston & ring pack design (compression height, crown, ring dimensions).*
---

## 7. Piston & Ring Pack Design (Frozen)

### 7.1 Compression Height Calculation

| Parameter | Value |
|-----------|-------|
| Crankshaft stroke | 84.0 mm |
| Connecting rod length | 144.0 mm |
| **Block deck height** | **220.0 mm** |
| Stack height at TDC | 42.0 + 144.0 = 186.0 mm |
| **Piston compression height** | 220.0 - 186.0 = **34.0 mm** |

> Contingency: if 34 mm proves too short for oil gallery, reduce rod length to 142 mm (CH becomes 36 mm, rod ratio drops to 1.69 – still acceptable).

### 7.2 Clearance Volume & Piston Dish

| Component | Volume (cc) |
|-----------|------------|
| Target V_clear (CR 9.5:1) | 54.76 |
| Cylinder head chamber (pent-roof 4V) | 40.0 |
| Head gasket (bore 84.5 mm × 0.5 mm compressed) | 2.80 |
| Required clearance from piston | 54.76 - 40.0 - 2.80 = **11.96 cc** |

- **Piston dish volume (incl. valve reliefs):** **12.0 cc** shallow bowl + reliefs.
- **Deck clearance:** Zero (piston crown flush with block deck at TDC).

### 7.3 Piston Material & Construction

- **Material:** Forged 4032 aluminum (low expansion, high silicon content)
- **Heat treatment:** T6
- **Crown coating:** Hard anodized combustion face
- **Skirt coating:** Anti-friction polymer (Grafal or equivalent)
- **Oil cooling gallery:** Drilled internal gallery, piston cooling jets feed from below
- **Wrist pin bore:** 22.0 mm + 0.005 mm clearance
- **Pin retention:** Wire locks (full-floating)

### 7.4 Ring Pack Specification

| Ring | Width (mm) | Material | Coating | Profile |
|------|------------|----------|---------|---------|
| Top compression | 1.0 | Nitrided steel | PVD CrN | Barrel-faced, positive twist |
| Second compression | 1.0 | Grey cast iron | Phosphate | Taper-faced Napier (1°), negative twist |
| Oil control | 2.0 | 3-piece steel | Chrome rails | Nitrile expander |

| Ring | Cold End Gap (mm) |
|------|--------------------|
| Top ring | 0.25 |
| Second ring | 0.35 |
| Oil ring rails | 0.20 |

**Ring land widths:** Top land 3.0 mm, second land 2.5 mm, third land 2.0 mm.

### 7.5 Piston-to-Bore Clearance

- **Clearance:** 0.045 mm (0.0018") for 4032 aluminum in iron liner at 84.0 mm bore.
- **Measuring point:** At pin centerline, 10 mm from bottom of skirt.

### 7.6 Piston Cooling Jets

- **Type:** Dual jets per cylinder, targeting underside of crown (cooling gallery inlet).
- **Supply:** Dedicated pressure stage or main gallery with check valves opening at ≥ 2 bar.
- **Oil source:** Wet sump, high-capacity pump.

### 7.7 Off-the-Shelf / Custom Supplier Reference

- **Supplier options:** Wiseco, JE Pistons, Mahle Motorsport
- **Blank specifications:**
  - Bore: 84.00 mm (finish to exact clearance in block)
  - Compression height: 34.0 mm
  - Dish volume: -12.0 cc
  - Ring grooves: 1.0 / 1.0 / 2.0 mm, lands as above
  - Wrist pin: 22.0 mm × 55 mm
  - Internal oil gallery with side feed
  - Crown: hard anodized; Skirt: Grafal coated

---

*Next section: Cylinder block design (bore spacing, head bolt pattern, water jacket, main bearing bulkheads).*
---

## 8. Cylinder Block & Crankcase Design

### 8.1 Block Configuration

| Parameter | Value |
|-----------|-------|
| Type | Horizontally opposed 6‑cylinder, deep‑skirt |
| Material | A356‑T6 aluminum (sand cast, heat treated) |
| Cylinder liners | Dry‑sleeve centrifugally cast iron, press‑fitted |
| Deck type | Closed‑deck (solid deck with drilled coolant passages) |
| Main bearing caps | Individual forged 4340 steel, dowelled |
| Weight target (bare block) | ~55‑60 kg |

### 8.2 Bore Spacing & Layout

- **Bore spacing:** 98.0 mm (14 mm solid aluminum between liner ODs)
- **Bank offset (left‑right):** 45.0 mm (provides clearance for opposing rod big‑ends on shared crankpin)
- **Block total length:** approx. 560 mm

### 8.3 Cylinder Liners

| Parameter | Value |
|-----------|-------|
| Nominal bore | 84.00 mm |
| Liner OD | 92.00 mm (wall 4.0 mm) |
| Liner length | 155 mm |
| Material | Centrifugally cast G3000 grey iron |
| Installation | Thermal interference fit (0.10 mm interference) |

### 8.4 Main Bearings & Caps

- **Bearings:** 7, integral bulkheads, 24 mm thick
- **Main bearing bore (in block):** 62.0 mm + bearing crush
- **Caps:** Forged 4340 steel, 24 mm wide, 2 × M12 bolts + 2 dowel pins each
- **Optional cross‑bolting:** M8 bosses on caps 2‑6 for added stiffness

### 8.5 Deck & Head Gasket Interface

- **Deck height:** 220.0 mm from crank centerline
- **Deck thickness:** 12 mm (closed‑deck)
- **Head gasket:** MLS, 0.5 mm compressed, bore 84.5 mm
- **Head bolts:** 4 per cylinder, M11 × 1.5, on a 92 mm square pattern

### 8.6 Water Jacket (Closed‑Deck)

- Full‑width cast‑in jacket surrounding each cylinder
- Coolant transfer to heads via 6‑8 drilled holes per cylinder (8‑10 mm dia) in deck face
- Main coolant gallery fed from front‑mounted water pump

### 8.7 Oil System Features

- Oil drain passages from heads: 12 mm minimum diameter
- Piston cooling jet bosses: M8, in main oil gallery
- Oil filter mount with integrated 5.5 bar relief valve
- Wet‑sump dipstick provision

### 8.8 Machining & Assembly

1. Line bore mains with caps installed and torqued
2. Bore cylinder liners with torque plate simulating head
3. Mill deck faces parallel to crankshaft centerline (±0.02 mm)
4. Roll‑form head bolt threads for fatigue strength

---

*Next section: Cylinder head design (port layout, valve sizes, combustion chamber, valvetrain).*
---

## 9. Cylinder Head Design

### 9.1 Head Configuration

| Parameter | Value |
|-----------|-------|
| Heads | Two (one per bank), sand‑cast A356‑T6 |
| Combustion chamber | Pent‑roof, 4 valves per cylinder |
| Valve angle (included) | 26° (13° intake, 13° exhaust) |
| Valvetrain | Solid bucket tappet, direct‑acting cams |
| Spark plug | Central M12, projected tip |
| Injector | Central GDI, side‑entry, 6‑hole nozzle |

### 9.2 Valve Dimensions

| Valve | Head Dia. | Stem Dia. | Length | Material |
|-------|-----------|-----------|--------|----------|
| Intake | 34.0 mm | 5.5 mm | 105 mm | Titanium or Nimonic |
| Exhaust | 29.0 mm | 5.5 mm | 105 mm | Inconel 751 |

### 9.3 Combustion Chamber

- **Chamber volume:** 40.0 cc
- **Squish area:** ~18% of bore area, two pads
- **Squish clearance:** 1.0 mm (0.5 mm gasket + 0.5 mm piston‑deck)
- **Injector angle:** 15° from vertical

### 9.4 Port Specifications

| Port | Flow Target | Tumble | Entry Dia. |
|------|-------------|--------|------------|
| Intake | ≥ 90 CFM @ 28″ | 1.5–1.8 | 42 mm |
| Exhaust | ≥ 75 CFM @ 28″ | — | 38 mm |

### 9.5 Valvetrain Components

| Component | Specification |
|-----------|---------------|
| Bucket | 31 mm, DLC‑coated steel |
| Lash | Intake 0.15 mm, Exhaust 0.20 mm (cold) |
| Spring | Beehive, 70‑75 lbs seat / 180‑190 lbs open |
| Retainer | Titanium, 7° collets |
| Camshaft | Chilled cast iron, hollow, 28 mm journals |

### 9.6 Camshaft Drive & Bearings

- **Drive:** Chain → idler → gears to each cam
- **Journals:** 28 mm, machined in head, 5 bearings per cam
- **VVT (optional):** Hydraulic vane, intake cam only

### 9.7 Cooling & Oil Management

- Coolant cross‑flow between exhaust valves (anti‑knock)
- Oil drains: 3 positions per head, ≥ 12 mm diameter

### 9.8 Head Clamping

- **Bolts:** 4 per cylinder, M11 × 1.5, torque 30→60→90 Nm + 90°
- **Gasket:** MLS, 0.5 mm compressed

---

*Next section: Intake & exhaust manifold conceptual layout.*
---

## 10. Intake & Exhaust Manifold Design

### 10.1 Exhaust Manifolds (Per Bank)

| Parameter | Value |
|-----------|-------|
| Type | Single‑scroll, 3‑into‑1, equal length |
| Material | 321 stainless steel |
| Runner length | 700 mm (tuned for 4000 rpm) |
| Runner ID | 38 mm |
| Collector | 14° merge cone to turbine flange |
| Turbine flange | T25 / KKK (turbo dependent) |

### 10.2 Turbocharger Mounting

- Low‑side mount, below each cylinder head
- Steel support bracket with thermal expansion allowance
- Oil feed: restricted (1.5 mm orifice) from main gallery
- Oil drain: AN‑10 gravity drain to sump

### 10.3 Wastegate & Boost Control

- Internal wastegate preferred; external 38 mm TiAL if not available
- Electronic boost solenoid, ECU‑controlled
- Target pressures: 1.75 bar(a) @ 4000 rpm, 2.0 bar(a) @ 6500 rpm

### 10.4 Exhaust Downpipe & Aftertreatment

| Component | Specification |
|-----------|---------------|
| Downpipe | 63 mm OD per bank, merge to 76 mm |
| TWC | 200‑cell metal substrate, <300 mm from turbine |
| GPF (optional) | Single unit in merged section |

### 10.5 Intake Manifold & Intercooler

- Cast aluminum plenum with integrated water‑to‑air intercooler
- Plenum volume: 4.0 L, runner length 280 mm, runner ID 42 mm
- Throttle body: 68 mm electronic, single
- Intercooler core: 25 mm thick, dual‑pass, fed by separate LT circuit

### 10.6 Pre‑Compressor Intake

- Conical dry filter in cold‑air box
- 63 mm aluminum pipe to turbo inlet
- Recirculating blow‑off valve

### 10.7 Packaging (70×70×50 cm Bay)

- Block: ~56 cm L × 65 cm W × 35 cm H
- Turbos and intake fit within 70 cm width, 50 cm height

---

*Next section: Lubrication & cooling system design.*
---

## 11. Lubrication System

### 11.1 Oil Type & Pump

| Parameter | Value |
|-----------|-------|
| Oil | Full synthetic 5W‑40 (street) / 10W‑60 (rally) |
| Pump | High‑volume gerotor, crank‑driven, internal |
| Relief pressure | 5.5 bar |
| Hot idle pressure | ≥ 1.5 bar @ 900 rpm |
| Full‑load pressure | 4.5–5.0 bar above 3000 rpm |

### 11.2 Sump (Wet, Deep)

- Fabricated aluminum, 7.0 L capacity
- Windage tray, trap‑door baffle box, crank scraper
- 19 mm ID pickup, centrally located

### 11.3 Oil Cooling & Filtration

- 19‑row air‑to‑oil cooler, thermostat 85 °C
- Spin‑on filter with anti‑drainback
- Target oil temp: 100–110 °C (max 130 °C)

### 11.4 Oil Distribution

| Circuit | Feed |
|---------|------|
| Main & rod bearings | Main gallery |
| Camshafts | Drilled passages |
| Piston cooling jets | M8 jets, check valve ≥ 2.5 bar |
| Turbochargers | 1.5 mm orifice restrictors |
| Timing chain | Small feed from front main |

---

## 12. Cooling System

### 12.1 Coolant Circuit

- 50/50 water‑glycol (OAT)
- Mechanical water pump, 100 mm impeller, 180 L/min @ 6500 rpm
- Thermostat: 88 °C wax pellet

### 12.2 Flow Path

1. Pump → block gallery (low) → around liners (exhaust side to intake)
2. Deck transfer holes → into head (between exhaust valves)
3. Head → thermostat housing → radiator (or bypass)
4. Separate LT circuit for intercooler

### 12.3 Radiator & Fans

| Component | Specification |
|-----------|---------------|
| Main radiator | 600 × 400 × 50 mm aluminum |
| Fan | 400 mm electric puller, 150 W |
| Expansion tank | 1.5 bar cap, remote |
| Intercooler radiator | 300 × 300 × 30 mm, electric pump |

### 12.4 Thermal Management

- Warm‑up: thermostat closed until 88 °C
- Hot soak: fan after‑run for 5 min above 95 °C
- Rally override: manual fan switch, restrictor option

---

*Next section: ECU, engine management, and wiring architecture.*

### 13.5 First Subsystem – Power Supply & Protection

The power supply board will be the first custom PCB. It provides:

- **Reverse‑battery protection:** P‑channel MOSFET, low‑loss
- **Load dump clamp:** TVS diode + series resistance
- **Main 5 V pre‑regulator:** synchronous buck converter (e.g., LMR50410), 5 V @ 5 A
- **3.3 V digital LDO:** TPS7A47, low noise, 300 mA
- **5 V analog LDO:** LP3878, 200 mA
- **48 V boost for GDI:** LT8331 or similar, feeding an electrolytic capacitor bank (1000‑2000 µF) to supply injector peak current
- **Ignition coil supply:** switched 12 V via relay (controlled by ECU)

Outputs are cleanly separated rails on headers/pin headers to the processor and I/O boards.

### 13.6 Next ECU Steps

1. Finalize pin assignment table for STM32G474RE (assign all engine sensors and actuators to specific HRTIM channels, ADC inputs, and GPIO).
2. Create detailed power supply schematic.
3. Design analog input conditioning circuits (VR, knock, wideband, temperature sensors).
4. Design output drivers (ignition IGBTs, GDI peak‑and‑hold).
5. PCB layout for each modular board.

---