"""
Synthetic Data Generator for Steel Plant Maintenance Wizard.
Generates realistic equipment, sensor, maintenance, and knowledge base data.
"""
import json
import os
import random
import math
from datetime import datetime, timedelta

random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "equipment_knowledge")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# 1. EQUIPMENT REGISTRY
# ═══════════════════════════════════════════════════════════════
EQUIPMENT = [
    {"id": "BF-CP-001", "name": "Blast Furnace Cooling Pump #1", "area": "Blast Furnace", "type": "Centrifugal Pump", "criticality": "critical", "install_date": "2018-03-15", "rated_hours": 60000},
    {"id": "BF-CP-002", "name": "Blast Furnace Cooling Pump #2", "area": "Blast Furnace", "type": "Centrifugal Pump", "criticality": "critical", "install_date": "2019-07-22", "rated_hours": 60000},
    {"id": "BF-BL-001", "name": "Hot Blast Blower", "area": "Blast Furnace", "type": "Turbo Blower", "criticality": "critical", "install_date": "2017-11-10", "rated_hours": 80000},
    {"id": "BF-HY-001", "name": "BF Hydraulic System", "area": "Blast Furnace", "type": "Hydraulic Power Unit", "criticality": "high", "install_date": "2020-01-05", "rated_hours": 50000},
    {"id": "BF-CV-001", "name": "Raw Material Conveyor Belt", "area": "Blast Furnace", "type": "Belt Conveyor", "criticality": "high", "install_date": "2021-06-18", "rated_hours": 45000},
    {"id": "SMS-LD-001", "name": "LD Converter Vessel #1", "area": "Steel Melting Shop", "type": "BOF Converter", "criticality": "critical", "install_date": "2016-09-01", "rated_hours": 100000},
    {"id": "SMS-CC-001", "name": "Continuous Caster #1", "area": "Steel Melting Shop", "type": "Continuous Casting Machine", "criticality": "critical", "install_date": "2018-12-20", "rated_hours": 70000},
    {"id": "SMS-LF-001", "name": "Ladle Furnace", "area": "Steel Melting Shop", "type": "Electric Arc Furnace", "criticality": "high", "install_date": "2019-04-14", "rated_hours": 65000},
    {"id": "SMS-CR-001", "name": "EOT Crane #1 (250T)", "area": "Steel Melting Shop", "type": "Overhead Crane", "criticality": "critical", "install_date": "2017-02-28", "rated_hours": 90000},
    {"id": "SMS-PU-001", "name": "Argon Stirring Pump", "area": "Steel Melting Shop", "type": "Gas Compressor", "criticality": "medium", "install_date": "2022-08-10", "rated_hours": 40000},
    {"id": "RM-DM-001", "name": "Rolling Mill Drive Motor", "area": "Rolling Mill", "type": "AC Motor (2000kW)", "criticality": "critical", "install_date": "2018-05-30", "rated_hours": 75000},
    {"id": "RM-GB-001", "name": "Mill Gearbox #1", "area": "Rolling Mill", "type": "Helical Gearbox", "criticality": "critical", "install_date": "2019-10-15", "rated_hours": 55000},
    {"id": "RM-RS-001", "name": "Roughing Stand", "area": "Rolling Mill", "type": "Rolling Stand", "criticality": "high", "install_date": "2020-03-22", "rated_hours": 50000},
    {"id": "RM-FS-001", "name": "Finishing Stand #1", "area": "Rolling Mill", "type": "Rolling Stand", "criticality": "high", "install_date": "2020-03-22", "rated_hours": 50000},
    {"id": "RM-CL-001", "name": "Cooling Bed System", "area": "Rolling Mill", "type": "Cooling System", "criticality": "medium", "install_date": "2021-01-10", "rated_hours": 45000},
    {"id": "CO-PU-001", "name": "Coke Oven Pusher Machine", "area": "Coke Oven", "type": "Pusher Machine", "criticality": "high", "install_date": "2019-08-05", "rated_hours": 60000},
    {"id": "CO-QC-001", "name": "Quenching Car", "area": "Coke Oven", "type": "Quenching Car", "criticality": "medium", "install_date": "2020-11-12", "rated_hours": 50000},
    {"id": "CO-GC-001", "name": "Gas Cleaning Plant", "area": "Coke Oven", "type": "Gas Treatment System", "criticality": "high", "install_date": "2018-04-20", "rated_hours": 70000},
    {"id": "SP-FM-001", "name": "Sinter Fan Main Blower", "area": "Sinter Plant", "type": "Centrifugal Fan", "criticality": "critical", "install_date": "2017-06-15", "rated_hours": 80000},
    {"id": "SP-IG-001", "name": "Ignition Furnace", "area": "Sinter Plant", "type": "Gas Furnace", "criticality": "high", "install_date": "2019-09-30", "rated_hours": 55000},
    {"id": "SP-CV-001", "name": "Sinter Mix Conveyor", "area": "Sinter Plant", "type": "Belt Conveyor", "criticality": "medium", "install_date": "2021-02-14", "rated_hours": 45000},
    {"id": "PP-TG-001", "name": "Steam Turbine Generator", "area": "Power Plant", "type": "Steam Turbine", "criticality": "critical", "install_date": "2016-01-20", "rated_hours": 100000},
    {"id": "PP-BL-001", "name": "Boiler Feed Pump", "area": "Power Plant", "type": "Multi-stage Pump", "criticality": "high", "install_date": "2018-07-08", "rated_hours": 60000},
    {"id": "PP-CT-001", "name": "Cooling Tower Fan", "area": "Power Plant", "type": "Axial Fan", "criticality": "medium", "install_date": "2020-05-25", "rated_hours": 50000},
    {"id": "PP-TR-001", "name": "Main Transformer (100MVA)", "area": "Power Plant", "type": "Power Transformer", "criticality": "critical", "install_date": "2015-11-30", "rated_hours": 120000},
]

# Failure modes per equipment type
FAILURE_MODES = {
    "Centrifugal Pump": [
        {"mode": "Bearing failure", "cause": "Lubrication breakdown / contamination", "symptom": "High vibration, elevated temperature at bearing housing", "mtbf_hours": 15000},
        {"mode": "Seal leakage", "cause": "Mechanical seal wear / thermal shock", "symptom": "Visible leakage, pressure drop", "mtbf_hours": 12000},
        {"mode": "Impeller erosion", "cause": "Cavitation / abrasive particles in fluid", "symptom": "Reduced flow rate, increased noise", "mtbf_hours": 20000},
        {"mode": "Motor winding failure", "cause": "Insulation degradation due to overheating", "symptom": "Current spikes, overheating", "mtbf_hours": 25000},
    ],
    "Turbo Blower": [
        {"mode": "Blade fatigue crack", "cause": "High-cycle fatigue / foreign object damage", "symptom": "Unusual vibration pattern, noise", "mtbf_hours": 30000},
        {"mode": "Bearing degradation", "cause": "Oil contamination / misalignment", "symptom": "High vibration, temperature rise", "mtbf_hours": 18000},
        {"mode": "Surge condition", "cause": "Operating below minimum flow", "symptom": "Pressure fluctuations, vibration spikes", "mtbf_hours": 10000},
    ],
    "Hydraulic Power Unit": [
        {"mode": "Hydraulic oil contamination", "cause": "Filter bypass / seal degradation", "symptom": "Erratic actuator movement, pressure drops", "mtbf_hours": 8000},
        {"mode": "Pump wear", "cause": "Abrasive particles / cavitation", "symptom": "Reduced pressure, increased noise", "mtbf_hours": 15000},
        {"mode": "Valve malfunction", "cause": "Spool sticking / solenoid failure", "symptom": "Inconsistent pressure, slow response", "mtbf_hours": 12000},
    ],
    "Belt Conveyor": [
        {"mode": "Belt misalignment", "cause": "Uneven loading / roller wear", "symptom": "Belt tracking issues, material spillage", "mtbf_hours": 5000},
        {"mode": "Roller bearing failure", "cause": "Dust ingress / lubrication failure", "symptom": "Squealing noise, belt drag", "mtbf_hours": 10000},
        {"mode": "Belt splice failure", "cause": "Material fatigue / impact damage", "symptom": "Belt separation, stoppage", "mtbf_hours": 15000},
    ],
    "BOF Converter": [
        {"mode": "Refractory lining erosion", "cause": "Thermal cycling / chemical attack", "symptom": "Shell temperature rise, reduced campaign life", "mtbf_hours": 2000},
        {"mode": "Trunnion bearing wear", "cause": "High load cycling", "symptom": "Vibration during tilting, noise", "mtbf_hours": 25000},
        {"mode": "Lance tip erosion", "cause": "High-temperature oxidation", "symptom": "Inconsistent blowing, temperature variation", "mtbf_hours": 1500},
    ],
    "Continuous Casting Machine": [
        {"mode": "Mould oscillation fault", "cause": "Hydraulic system degradation", "symptom": "Surface defects on slab, breakout risk", "mtbf_hours": 8000},
        {"mode": "Roller bearing failure", "cause": "Thermal stress / scale buildup", "symptom": "Slab surface marks, roller seizure", "mtbf_hours": 12000},
        {"mode": "Spray nozzle blockage", "cause": "Scale / debris accumulation", "symptom": "Uneven cooling, surface cracks", "mtbf_hours": 5000},
    ],
    "Electric Arc Furnace": [
        {"mode": "Electrode breakage", "cause": "Thermal shock / scrap impact", "symptom": "Production interruption, electrode consumption increase", "mtbf_hours": 3000},
        {"mode": "Refractory wear", "cause": "Slag attack / thermal cycling", "symptom": "Shell hot spots, increased energy consumption", "mtbf_hours": 4000},
    ],
    "Overhead Crane": [
        {"mode": "Wire rope fatigue", "cause": "Cyclic loading / corrosion", "symptom": "Visible wire breaks, elongation", "mtbf_hours": 20000},
        {"mode": "Brake system wear", "cause": "Frequent operation / heat", "symptom": "Increased stopping distance, slippage", "mtbf_hours": 15000},
        {"mode": "Gearbox failure", "cause": "Gear tooth fatigue / oil degradation", "symptom": "Noise, vibration, slow operation", "mtbf_hours": 25000},
    ],
    "Gas Compressor": [
        {"mode": "Valve plate failure", "cause": "Fatigue / contamination", "symptom": "Reduced discharge pressure, overheating", "mtbf_hours": 10000},
        {"mode": "Piston ring wear", "cause": "Normal wear / contamination", "symptom": "Reduced efficiency, oil carryover", "mtbf_hours": 12000},
    ],
    "AC Motor (2000kW)": [
        {"mode": "Stator winding insulation failure", "cause": "Thermal aging / voltage spikes", "symptom": "Partial discharge, current imbalance", "mtbf_hours": 30000},
        {"mode": "Bearing failure", "cause": "Lubrication issues / misalignment", "symptom": "High vibration, temperature rise", "mtbf_hours": 20000},
        {"mode": "Rotor bar cracking", "cause": "Thermal stress / starting cycles", "symptom": "Speed fluctuation, current harmonics", "mtbf_hours": 35000},
    ],
    "Helical Gearbox": [
        {"mode": "Gear tooth pitting", "cause": "Surface fatigue / oil contamination", "symptom": "Increasing vibration, metallic particles in oil", "mtbf_hours": 18000},
        {"mode": "Shaft misalignment", "cause": "Foundation settling / thermal expansion", "symptom": "Coupling wear, vibration", "mtbf_hours": 15000},
        {"mode": "Oil seal failure", "cause": "Seal aging / shaft wear", "symptom": "Oil leakage, contamination", "mtbf_hours": 10000},
    ],
    "Rolling Stand": [
        {"mode": "Roll bearing failure", "cause": "Overloading / contamination", "symptom": "Surface defects on product, vibration", "mtbf_hours": 12000},
        {"mode": "Chock wear", "cause": "Roll changing cycles", "symptom": "Roll misalignment, product dimension variation", "mtbf_hours": 15000},
    ],
    "Cooling System": [
        {"mode": "Nozzle blockage", "cause": "Scale / debris", "symptom": "Uneven cooling, product quality issues", "mtbf_hours": 5000},
        {"mode": "Pump cavitation", "cause": "Low NPSH / air ingress", "symptom": "Noise, reduced flow, vibration", "mtbf_hours": 10000},
    ],
    "Pusher Machine": [
        {"mode": "Ram head wear", "cause": "Abrasion / impact", "symptom": "Incomplete pushing, coke oven door damage", "mtbf_hours": 15000},
        {"mode": "Drive chain elongation", "cause": "Wear / overload", "symptom": "Positioning errors, jerky movement", "mtbf_hours": 12000},
    ],
    "Quenching Car": [
        {"mode": "Wheel bearing failure", "cause": "Water ingress / thermal cycling", "symptom": "Difficult movement, noise", "mtbf_hours": 10000},
        {"mode": "Structure deformation", "cause": "Thermal stress", "symptom": "Uneven quenching, alignment issues", "mtbf_hours": 20000},
    ],
    "Gas Treatment System": [
        {"mode": "Scrubber nozzle blockage", "cause": "Tar / dust buildup", "symptom": "Reduced gas cleaning efficiency, emissions", "mtbf_hours": 8000},
        {"mode": "Fan bearing failure", "cause": "Corrosive gas exposure", "symptom": "Vibration, temperature rise", "mtbf_hours": 15000},
    ],
    "Centrifugal Fan": [
        {"mode": "Impeller imbalance", "cause": "Dust buildup / erosion", "symptom": "High vibration, noise", "mtbf_hours": 12000},
        {"mode": "Bearing failure", "cause": "Misalignment / lubrication", "symptom": "Temperature rise, vibration", "mtbf_hours": 18000},
    ],
    "Gas Furnace": [
        {"mode": "Burner nozzle blockage", "cause": "Carbon buildup", "symptom": "Uneven heating, flame instability", "mtbf_hours": 6000},
        {"mode": "Refractory cracking", "cause": "Thermal shock", "symptom": "Heat loss, shell temperature rise", "mtbf_hours": 10000},
    ],
    "Steam Turbine": [
        {"mode": "Blade erosion", "cause": "Wet steam / foreign particles", "symptom": "Efficiency drop, vibration change", "mtbf_hours": 30000},
        {"mode": "Journal bearing wear", "cause": "Oil contamination / misalignment", "symptom": "Vibration, temperature increase", "mtbf_hours": 25000},
        {"mode": "Governor malfunction", "cause": "Actuator wear / signal drift", "symptom": "Speed fluctuation, load swings", "mtbf_hours": 20000},
    ],
    "Multi-stage Pump": [
        {"mode": "Impeller wear", "cause": "Cavitation / erosion", "symptom": "Reduced head, increased power consumption", "mtbf_hours": 15000},
        {"mode": "Mechanical seal failure", "cause": "Thermal cycling / dry running", "symptom": "Leakage, vibration", "mtbf_hours": 12000},
    ],
    "Axial Fan": [
        {"mode": "Blade pitch mechanism failure", "cause": "Actuator wear / linkage issues", "symptom": "Reduced airflow, current fluctuation", "mtbf_hours": 15000},
        {"mode": "Motor bearing failure", "cause": "Environmental exposure", "symptom": "Vibration, noise", "mtbf_hours": 18000},
    ],
    "Power Transformer": [
        {"mode": "Winding insulation degradation", "cause": "Thermal aging / moisture ingress", "symptom": "Dissolved gas in oil, partial discharge", "mtbf_hours": 50000},
        {"mode": "Tap changer failure", "cause": "Contact erosion / mechanism wear", "symptom": "Voltage regulation issues", "mtbf_hours": 30000},
        {"mode": "Bushing leakage", "cause": "Seal degradation / porcelain cracking", "symptom": "Oil leakage, partial discharge", "mtbf_hours": 40000},
    ],
}

# Spare parts catalog
SPARE_PARTS = {
    "Centrifugal Pump": [
        {"name": "SKF 6316 Deep Groove Bearing", "part_no": "SP-BRG-001", "cost": 450, "lead_time_days": 7, "stock": 4},
        {"name": "Mechanical Seal Type A (65mm)", "part_no": "SP-SEL-001", "cost": 1200, "lead_time_days": 14, "stock": 2},
        {"name": "SS316 Impeller Assembly", "part_no": "SP-IMP-001", "cost": 3500, "lead_time_days": 30, "stock": 1},
        {"name": "Coupling Spider Element", "part_no": "SP-CPL-001", "cost": 180, "lead_time_days": 5, "stock": 6},
    ],
    "Turbo Blower": [
        {"name": "Tilting Pad Journal Bearing", "part_no": "SP-TPB-001", "cost": 8500, "lead_time_days": 45, "stock": 1},
        {"name": "Impeller Blade Set", "part_no": "SP-BLD-001", "cost": 15000, "lead_time_days": 60, "stock": 0},
        {"name": "Thrust Bearing Assembly", "part_no": "SP-THB-001", "cost": 6200, "lead_time_days": 30, "stock": 1},
    ],
    "AC Motor (2000kW)": [
        {"name": "Stator Winding Coil Set", "part_no": "SP-WND-001", "cost": 25000, "lead_time_days": 90, "stock": 0},
        {"name": "Rotor Bearing (NU 330)", "part_no": "SP-RBR-001", "cost": 2800, "lead_time_days": 14, "stock": 2},
        {"name": "Cooling Fan Assembly", "part_no": "SP-FAN-001", "cost": 1500, "lead_time_days": 21, "stock": 1},
    ],
    "Helical Gearbox": [
        {"name": "Gear Pair Set (Module 12)", "part_no": "SP-GPR-001", "cost": 18000, "lead_time_days": 75, "stock": 0},
        {"name": "Input Shaft Bearing", "part_no": "SP-ISB-001", "cost": 3200, "lead_time_days": 14, "stock": 2},
        {"name": "Viton Oil Seal Set", "part_no": "SP-OSL-001", "cost": 350, "lead_time_days": 7, "stock": 8},
        {"name": "Synthetic Gear Oil (ISO 320, 200L)", "part_no": "SP-OIL-001", "cost": 800, "lead_time_days": 3, "stock": 5},
    ],
    "Steam Turbine": [
        {"name": "HP Blade Row Assembly", "part_no": "SP-HPB-001", "cost": 45000, "lead_time_days": 120, "stock": 0},
        {"name": "Journal Bearing (White Metal)", "part_no": "SP-JBR-001", "cost": 12000, "lead_time_days": 45, "stock": 1},
        {"name": "Governor Actuator", "part_no": "SP-GOV-001", "cost": 8000, "lead_time_days": 30, "stock": 1},
    ],
}

# Normal operating ranges per equipment type
SENSOR_RANGES = {
    "Centrifugal Pump":       {"vibration": (1.5, 4.5),   "temperature": (40, 65),  "pressure": (4.0, 8.0),  "current": (80, 120)},
    "Turbo Blower":           {"vibration": (2.0, 6.0),   "temperature": (50, 80),  "pressure": (1.5, 3.5),  "current": (200, 350)},
    "Hydraulic Power Unit":   {"vibration": (1.0, 3.5),   "temperature": (35, 55),  "pressure": (150, 250),  "current": (40, 80)},
    "Belt Conveyor":          {"vibration": (1.0, 3.0),   "temperature": (25, 50),  "pressure": (0, 0),      "current": (50, 100)},
    "BOF Converter":          {"vibration": (3.0, 8.0),   "temperature": (60, 120), "pressure": (2.0, 5.0),  "current": (150, 300)},
    "Continuous Casting Machine": {"vibration": (2.0, 5.0), "temperature": (45, 75), "pressure": (3.0, 7.0), "current": (100, 200)},
    "Electric Arc Furnace":   {"vibration": (3.0, 7.0),   "temperature": (55, 95),  "pressure": (1.0, 3.0),  "current": (500, 1200)},
    "Overhead Crane":         {"vibration": (1.5, 4.0),   "temperature": (30, 60),  "pressure": (0, 0),      "current": (100, 250)},
    "Gas Compressor":         {"vibration": (2.0, 5.0),   "temperature": (50, 85),  "pressure": (5.0, 12.0), "current": (60, 120)},
    "AC Motor (2000kW)":      {"vibration": (2.0, 5.5),   "temperature": (45, 75),  "pressure": (0, 0),      "current": (180, 280)},
    "Helical Gearbox":        {"vibration": (2.5, 6.0),   "temperature": (45, 70),  "pressure": (0, 0),      "current": (0, 0)},
    "Rolling Stand":          {"vibration": (3.0, 7.0),   "temperature": (40, 70),  "pressure": (100, 200),  "current": (150, 300)},
    "Cooling System":         {"vibration": (1.0, 3.0),   "temperature": (25, 45),  "pressure": (2.0, 6.0),  "current": (30, 60)},
    "Pusher Machine":         {"vibration": (3.0, 8.0),   "temperature": (35, 65),  "pressure": (100, 200),  "current": (100, 200)},
    "Quenching Car":          {"vibration": (2.0, 5.0),   "temperature": (30, 55),  "pressure": (0, 0),      "current": (60, 120)},
    "Gas Treatment System":   {"vibration": (1.5, 4.0),   "temperature": (35, 60),  "pressure": (0.5, 2.0),  "current": (80, 150)},
    "Centrifugal Fan":        {"vibration": (2.0, 5.5),   "temperature": (40, 65),  "pressure": (0.8, 2.5),  "current": (120, 220)},
    "Gas Furnace":            {"vibration": (1.0, 3.0),   "temperature": (800, 1200),"pressure": (0.5, 1.5), "current": (20, 50)},
    "Steam Turbine":          {"vibration": (1.5, 4.5),   "temperature": (50, 80),  "pressure": (30, 60),    "current": (300, 600)},
    "Multi-stage Pump":       {"vibration": (1.5, 4.0),   "temperature": (40, 65),  "pressure": (20, 50),    "current": (60, 120)},
    "Axial Fan":              {"vibration": (2.0, 5.0),   "temperature": (35, 55),  "pressure": (0.3, 1.0),  "current": (80, 160)},
    "Power Transformer":      {"vibration": (0.5, 2.0),   "temperature": (45, 75),  "pressure": (0, 0),      "current": (200, 500)},
}


def generate_sensor_data(equipment_list, days=90):
    """Generate sensor time-series with realistic degradation and anomalies."""
    now = datetime(2026, 6, 7)
    all_sensor_data = {}

    # Select equipment for degradation / anomalies
    degrading_ids = {"BF-CP-001", "RM-GB-001", "SMS-CC-001", "PP-TG-001", "SP-FM-001", "BF-BL-001"}
    anomaly_ids = {"RM-DM-001", "CO-PU-001", "SMS-CR-001", "PP-BL-001"}

    for eq in equipment_list:
        eid = eq["id"]
        etype = eq["type"]
        ranges = SENSOR_RANGES.get(etype, {"vibration": (1, 5), "temperature": (30, 60), "pressure": (1, 5), "current": (50, 150)})
        readings = []

        for day_offset in range(days, 0, -1):
            for hour in [0, 4, 8, 12, 16, 20]:
                ts = now - timedelta(days=day_offset, hours=24 - hour)
                progress = 1 - (day_offset / days)  # 0 → 1 over time

                # Base values with small noise
                vib_base = (ranges["vibration"][0] + ranges["vibration"][1]) / 2
                temp_base = (ranges["temperature"][0] + ranges["temperature"][1]) / 2
                pres_base = (ranges["pressure"][0] + ranges["pressure"][1]) / 2
                curr_base = (ranges["current"][0] + ranges["current"][1]) / 2

                noise_v = random.gauss(0, (ranges["vibration"][1] - ranges["vibration"][0]) * 0.08)
                noise_t = random.gauss(0, (ranges["temperature"][1] - ranges["temperature"][0]) * 0.06)
                noise_p = random.gauss(0, max(0.01, (ranges["pressure"][1] - ranges["pressure"][0]) * 0.05))
                noise_c = random.gauss(0, (ranges["current"][1] - ranges["current"][0]) * 0.07)

                vib = vib_base + noise_v
                temp = temp_base + noise_t
                pres = pres_base + noise_p
                curr = curr_base + noise_c

                # Degradation: gradual increase toward end of data
                if eid in degrading_ids:
                    deg_factor = progress ** 2
                    vib += deg_factor * (ranges["vibration"][1] - ranges["vibration"][0]) * 0.8
                    temp += deg_factor * (ranges["temperature"][1] - ranges["temperature"][0]) * 0.5
                    curr += deg_factor * (ranges["current"][1] - ranges["current"][0]) * 0.3

                # Anomaly spikes in last 10 days
                if eid in anomaly_ids and day_offset <= 10:
                    if random.random() < 0.25:
                        spike = random.choice(["vibration", "temperature", "current"])
                        if spike == "vibration":
                            vib += random.uniform(3, 8)
                        elif spike == "temperature":
                            temp += random.uniform(15, 35)
                        else:
                            curr += random.uniform(30, 80)

                # Diurnal pattern (slight)
                diurnal = math.sin(hour / 24 * 2 * math.pi) * 0.5

                readings.append({
                    "timestamp": ts.isoformat(),
                    "vibration": round(max(0, vib + diurnal * 0.3), 2),
                    "temperature": round(max(0, temp + diurnal * 2), 1),
                    "pressure": round(max(0, pres), 2),
                    "current": round(max(0, curr + diurnal * 3), 1),
                })

        all_sensor_data[eid] = readings
    return all_sensor_data


def generate_maintenance_logs(equipment_list, count=600):
    """Generate historical maintenance log entries."""
    logs = []
    action_types = ["Preventive Maintenance", "Corrective Maintenance", "Breakdown Repair",
                     "Inspection", "Condition-Based Maintenance", "Emergency Repair",
                     "Overhaul", "Lubrication", "Calibration", "Alignment"]

    technicians = [
        "Rajesh Kumar", "Amit Singh", "Pradeep Verma", "Suresh Patel", "Vikram Sharma",
        "Anil Mehta", "Ramesh Gupta", "Deepak Tiwari", "Manoj Yadav", "Sanjay Mishra",
        "Ravi Prasad", "Gaurav Joshi", "Nitin Pandey", "Ashok Reddy", "Kiran Deshmukh"
    ]

    for i in range(count):
        eq = random.choice(equipment_list)
        etype = eq["type"]
        modes = FAILURE_MODES.get(etype, [{"mode": "General wear", "cause": "Normal usage", "symptom": "Performance degradation"}])
        failure = random.choice(modes)
        action = random.choice(action_types)
        days_ago = random.randint(1, 730)
        log_date = datetime(2026, 6, 7) - timedelta(days=days_ago)

        downtime = 0
        if action in ["Breakdown Repair", "Emergency Repair"]:
            downtime = random.uniform(4, 72)
        elif action in ["Corrective Maintenance", "Overhaul"]:
            downtime = random.uniform(2, 24)
        elif action == "Preventive Maintenance":
            downtime = random.uniform(1, 8)

        logs.append({
            "id": f"ML-{i+1:04d}",
            "date": log_date.strftime("%Y-%m-%d"),
            "equipment_id": eq["id"],
            "equipment_name": eq["name"],
            "area": eq["area"],
            "action_type": action,
            "failure_mode": failure["mode"] if action not in ["Inspection", "Lubrication", "Calibration"] else "N/A",
            "root_cause": failure["cause"] if action not in ["Inspection", "Lubrication", "Calibration"] else "Scheduled activity",
            "symptoms_observed": failure["symptom"] if action not in ["Inspection", "Lubrication", "Calibration"] else "Routine check",
            "actions_taken": f"Performed {action.lower()} on {eq['name']}. {failure['mode']} addressed.",
            "downtime_hours": round(downtime, 1),
            "technician": random.choice(technicians),
            "parts_used": [],
            "status": "completed",
            "notes": f"Equipment returned to service after {action.lower()}. Monitored for 2 hours post-repair."
        })

    logs.sort(key=lambda x: x["date"], reverse=True)
    return logs


def generate_failure_reports(equipment_list, count=80):
    """Generate detailed failure/incident reports."""
    reports = []
    severity_levels = ["Minor", "Moderate", "Major", "Critical"]
    investigation_status = ["Completed", "In Progress", "Pending Review"]

    for i in range(count):
        eq = random.choice([e for e in equipment_list if e["criticality"] in ["critical", "high"]])
        etype = eq["type"]
        modes = FAILURE_MODES.get(etype, [{"mode": "Unknown failure", "cause": "Under investigation", "symptom": "Unexpected stoppage"}])
        failure = random.choice(modes)
        days_ago = random.randint(1, 365)
        report_date = datetime(2026, 6, 7) - timedelta(days=days_ago)
        severity = random.choice(severity_levels)
        downtime = random.uniform(2, 96) if severity in ["Major", "Critical"] else random.uniform(0.5, 12)
        production_loss = round(downtime * random.uniform(50, 500), 0)

        reports.append({
            "id": f"FR-{i+1:04d}",
            "date": report_date.strftime("%Y-%m-%d"),
            "equipment_id": eq["id"],
            "equipment_name": eq["name"],
            "area": eq["area"],
            "severity": severity,
            "failure_mode": failure["mode"],
            "root_cause": failure["cause"],
            "symptoms": failure["symptom"],
            "sequence_of_events": f"At approximately {random.randint(0,23):02d}:{random.randint(0,59):02d}, {failure['symptom'].lower()} was detected on {eq['name']}. Maintenance team was alerted. {failure['mode']} was confirmed after inspection.",
            "immediate_actions": f"Equipment was shut down safely. Area was secured. Emergency maintenance was initiated for {failure['mode'].lower()}.",
            "corrective_actions": f"Replaced affected components. Performed root cause analysis - {failure['cause'].lower()}. Implemented preventive measures.",
            "downtime_hours": round(downtime, 1),
            "production_loss_tonnes": production_loss,
            "investigation_status": random.choice(investigation_status),
            "lessons_learned": f"Regular monitoring of {failure['symptom'].split(',')[0].lower()} recommended. Review maintenance schedule for {eq['type']}.",
            "preventive_recommendations": [
                f"Increase inspection frequency for {eq['type']} components",
                f"Install additional sensors for early detection of {failure['mode'].lower()}",
                f"Review and update SOP for {eq['type']} maintenance"
            ]
        })

    reports.sort(key=lambda x: x["date"], reverse=True)
    return reports


def compute_equipment_status(equipment_list, sensor_data):
    """Compute health score and status for each equipment based on latest sensor data."""
    enriched = []
    for eq in equipment_list:
        eid = eq["id"]
        etype = eq["type"]
        ranges = SENSOR_RANGES.get(etype, {"vibration": (1, 5), "temperature": (30, 60), "pressure": (1, 5), "current": (50, 150)})

        recent = sensor_data.get(eid, [])[-30:]  # Last 5 days
        if not recent:
            eq["health_score"] = 85.0
            eq["status"] = "operational"
            eq["risk_level"] = "low"
            enriched.append(eq)
            continue

        # Compute health based on how close readings are to limits
        health_scores = []
        for r in recent:
            scores = []
            for sensor in ["vibration", "temperature", "current"]:
                val = r.get(sensor, 0)
                low, high = ranges.get(sensor, (0, 100))
                if high == low:
                    continue
                mid = (low + high) / 2
                rng = (high - low) / 2
                deviation = abs(val - mid) / rng if rng > 0 else 0
                score = max(0, 100 - deviation * 50)
                scores.append(score)
            if scores:
                health_scores.append(sum(scores) / len(scores))

        avg_health = sum(health_scores) / len(health_scores) if health_scores else 85
        avg_health = max(0, min(100, avg_health))

        if avg_health >= 80:
            status, risk = "operational", "low"
        elif avg_health >= 60:
            status, risk = "warning", "medium"
        elif avg_health >= 40:
            status, risk = "degraded", "high"
        else:
            status, risk = "critical", "critical"

        eq["health_score"] = round(avg_health, 1)
        eq["status"] = status
        eq["risk_level"] = risk
        eq["last_maintenance"] = (datetime(2026, 6, 7) - timedelta(days=random.randint(5, 90))).strftime("%Y-%m-%d")
        enriched.append(eq)

    return enriched


def generate_knowledge_base():
    """Generate equipment manuals and SOPs for the knowledge base."""

    docs = {}

    # General maintenance manual
    docs["general_maintenance_manual.md"] = """# Industrial Equipment Maintenance Manual — Tata Steel

## 1. Introduction
This manual provides comprehensive maintenance guidelines for industrial equipment operated in steel manufacturing environments. It covers preventive, predictive, and corrective maintenance procedures.

## 2. Maintenance Philosophy
- **Preventive Maintenance (PM)**: Time-based scheduled maintenance to prevent failures
- **Predictive Maintenance (PdM)**: Condition-based maintenance using sensor data and analytics
- **Corrective Maintenance (CM)**: Repair after failure detection
- **Reliability-Centered Maintenance (RCM)**: Risk-based maintenance optimization

## 3. Safety Protocols
- Always follow LOTO (Lock Out Tag Out) procedures before maintenance
- Wear appropriate PPE: safety helmet, goggles, steel-toe boots, heat-resistant gloves
- Obtain hot work permit for any welding/cutting near gas lines
- Ensure gas testing before entering confined spaces
- Two-person rule for all critical equipment maintenance

## 4. Vibration Analysis Guidelines
| Severity | Vibration (mm/s RMS) | Action |
|----------|---------------------|--------|
| Good | 0 - 2.8 | Normal operation |
| Acceptable | 2.8 - 7.1 | Schedule inspection |
| Warning | 7.1 - 18.0 | Plan maintenance within 1 week |
| Critical | > 18.0 | Immediate shutdown and repair |

## 5. Temperature Monitoring
- Bearing temperature should not exceed rated + 30°C
- Motor winding temperature limit: Class F (155°C), Class H (180°C)
- Gearbox oil temperature should stay below 80°C
- Any sudden rise > 10°C/hour requires investigation

## 6. Oil Analysis Intervals
- Hydraulic systems: Monthly
- Gearboxes: Quarterly
- Turbines: Monthly
- Check for: Water content, particle count, viscosity, metal particles

## 7. Lubrication Standards
- Use manufacturer-recommended lubricants only
- Grease replenishment: Every 2000 operating hours for standard bearings
- Oil change: Per OEM recommendation or based on oil analysis results
- Never mix different grease types
"""

    # Pump maintenance SOP
    docs["sop_centrifugal_pump_maintenance.md"] = """# SOP: Centrifugal Pump Maintenance
## Document ID: SOP-PUMP-001 | Rev: 3.2 | Date: 2025-01-15

### 1. Scope
Applies to all centrifugal pumps in Blast Furnace cooling circuit, SMS water systems, and utility pumps.

### 2. Tools Required
- Vibration analyzer (SKF Microlog)
- Infrared thermometer / thermal camera
- Bearing puller set
- Alignment laser tool (Fixturlaser)
- Torque wrench set
- Dial indicator set

### 3. Preventive Maintenance Schedule
| Task | Frequency | Duration |
|------|-----------|----------|
| Vibration check | Weekly | 15 min |
| Bearing temperature check | Daily | 5 min |
| Seal inspection | Weekly | 10 min |
| Coupling inspection | Monthly | 30 min |
| Bearing greasing | 2000 hrs | 20 min |
| Full alignment check | Quarterly | 2 hrs |
| Performance test | Quarterly | 1 hr |
| Complete overhaul | 15000 hrs | 16 hrs |

### 4. Bearing Replacement Procedure
1. Isolate pump electrically and mechanically (LOTO)
2. Drain and disconnect piping
3. Remove coupling guard and coupling hub
4. Remove bearing housing end cover
5. Use bearing puller to extract old bearing
6. Inspect shaft for wear/damage (max 0.025mm runout)
7. Clean housing bore and shaft journal
8. Heat new bearing to 80°C for installation (induction heater)
9. Press bearing onto shaft — ensure proper seating
10. Apply correct grease fill (30-40% of cavity volume)
11. Reassemble in reverse order
12. Perform laser alignment (max 0.05mm offset, 0.05mm/100mm angular)
13. Run test for 2 hours, monitor vibration and temperature

### 5. Troubleshooting Guide
| Symptom | Possible Cause | Action |
|---------|---------------|--------|
| High vibration | Misalignment, bearing wear, impeller imbalance | Check alignment, replace bearing, balance impeller |
| Overheating | Low oil/grease, bearing failure, overload | Check lubrication, inspect bearing, verify load |
| Low discharge | Impeller wear, air leak, valve issue | Inspect impeller, check suction line, verify valve positions |
| Noise | Cavitation, bearing damage, loose parts | Check NPSH, replace bearing, tighten fasteners |
| Seal leakage | Worn seal faces, thermal damage | Replace mechanical seal, check cooling |

### 6. Acceptance Criteria After Maintenance
- Vibration: < 4.5 mm/s RMS
- Bearing temperature: < 70°C (ambient + 40°C max)
- No visible leakage
- Flow rate within ±5% of rated
- Current draw within ±10% of rated
"""

    docs["sop_gearbox_maintenance.md"] = """# SOP: Industrial Gearbox Maintenance
## Document ID: SOP-GBX-001 | Rev: 2.1 | Date: 2025-03-20

### 1. Scope
Covers all helical and planetary gearboxes in Rolling Mill, Sinter Plant, and Coke Oven areas.

### 2. Oil Analysis Program
#### Parameters to Monitor:
- **Viscosity**: Should remain within ±10% of ISO grade
- **Water Content**: Max 200 ppm (alarm at 100 ppm)
- **Particle Count**: ISO 4406 — target 18/16/13
- **Iron (Fe)**: < 100 ppm normal, > 200 ppm warning, > 500 ppm critical
- **Copper (Cu)**: < 50 ppm normal (indicates bearing cage wear)
- **Silicon (Si)**: > 25 ppm indicates external contamination

### 3. Vibration Monitoring Points
- Input shaft bearing (horizontal, vertical, axial)
- Output shaft bearing (horizontal, vertical, axial)
- Gear mesh frequency monitoring
- Use envelope analysis for early bearing fault detection

### 4. Gear Inspection Criteria
| Condition | Action |
|-----------|--------|
| Light pitting (< 10% of tooth face) | Monitor, increase oil analysis frequency |
| Moderate pitting (10-25%) | Plan replacement within 3 months |
| Severe pitting (> 25%) | Replace gear set at next opportunity |
| Tooth root crack detected | Immediate replacement required |
| Scuffing/scoring marks | Check oil condition, reduce load if possible |

### 5. Alignment Procedure
1. Record current alignment readings
2. Loosen foundation bolts
3. Place precision shims as calculated
4. Use reverse dial indicator or laser alignment
5. Acceptable tolerance: 0.05mm offset, 0.05mm/100mm angular
6. Torque all bolts to specification
7. Recheck after 24 hours of operation (thermal growth)
"""

    docs["sop_motor_maintenance.md"] = """# SOP: High-Voltage Motor Maintenance
## Document ID: SOP-MOT-001 | Rev: 4.0 | Date: 2025-02-10

### 1. Scope
All AC motors above 500 kW in Rolling Mill, Blast Furnace, and Power Plant areas.

### 2. Insulation Resistance Testing
- Use 5000V DC megger for motors > 1000V
- Minimum acceptable IR at 40°C: 100 MΩ
- Polarization Index (PI): Must be > 2.0
- Test frequency: Quarterly for critical motors, Semi-annually for others
- Trend downward PI indicates insulation deterioration

### 3. Vibration Limits (ISO 10816-3)
| Zone | Vibration (mm/s RMS) | Status |
|------|---------------------|--------|
| A | 0 - 3.5 | New/good condition |
| B | 3.5 - 7.1 | Acceptable for long-term operation |
| C | 7.1 - 11.0 | Restricted operation, plan maintenance |
| D | > 11.0 | Damage occurring, immediate action |

### 4. Motor Current Signature Analysis (MCSA)
- Monitor for broken rotor bars: sidebands at f ± 2sf
- Detect eccentricity: f ± fr harmonics
- Check for stator faults: negative sequence current
- Record baseline during commissioning

### 5. Bearing Maintenance
- Grease type: Polyurea-based (e.g., SKF LGHP 2)
- Regreasing interval: Calculate per SKF DialSet
- Do NOT over-grease — can cause overheating
- Replace bearings at: 40,000 operating hours or on detected fault
"""

    docs["sop_steam_turbine.md"] = """# SOP: Steam Turbine Maintenance
## Document ID: SOP-STG-001 | Rev: 2.5 | Date: 2025-04-01

### 1. Scope
Applies to all steam turbine generators in Power Plant area.

### 2. Daily Monitoring Checklist
- [ ] Bearing vibration (all journals) — record in logbook
- [ ] Bearing temperature (all journals + thrust)
- [ ] Lube oil pressure, temperature, level
- [ ] Steam inlet pressure and temperature
- [ ] Exhaust pressure and temperature
- [ ] Generator load and power factor
- [ ] Governor response check

### 3. Critical Alarm Setpoints
| Parameter | Alert | Trip |
|-----------|-------|------|
| Journal bearing vibration | 5.0 mm/s | 7.5 mm/s |
| Bearing metal temperature | 100°C | 115°C |
| Lube oil pressure | 1.2 bar | 0.8 bar |
| Axial displacement | 0.3 mm | 0.5 mm |
| Over-speed | 103% | 110% |

### 4. Major Overhaul Tasks (every 5 years or 40,000 hours)
1. Open upper casing — inspect all blade rows
2. Measure blade tip clearances (radial and axial)
3. NDT inspection of all blades (DP, UT, MPI)
4. Inspect/replace journal bearings (white metal inspection)
5. Inspect thrust bearing pads
6. Check shaft runout (max 0.03mm)
7. Inspect gland seals — replace carbon rings if worn
8. Overhaul governor and trip system
9. Hydro test all pressure components
10. Reassemble with new gaskets and seals

### 5. Lube Oil System
- Oil type: ISO VG 32 turbine oil
- Change interval: Based on oil analysis (typically 3-5 years)
- Online purification: Centrifugal separator running 24/7
- Target oil condition: < 50 ppm water, NAS 6 cleanliness
"""

    docs["failure_mode_database.md"] = """# Equipment Failure Mode Database — Steel Plant

## Blast Furnace Equipment

### Cooling Water Pump Failures
1. **Bearing seizure** — Root cause: Lubrication starvation due to blocked grease line. Impact: 8-12 hours downtime. Prevention: Automated greasing system, vibration monitoring.
2. **Impeller cavitation damage** — Root cause: Low NPSH due to strainer blockage. Impact: Gradual performance decline. Prevention: Regular strainer cleaning, suction pressure monitoring.
3. **Shaft fatigue fracture** — Root cause: Resonance at operating speed due to foundation degradation. Impact: Catastrophic, 72+ hours. Prevention: Annual vibration survey, foundation inspection.

### Hot Blast System Failures
1. **Blower surge** — Root cause: Sudden load change or blocked tuyere. Impact: Process disruption. Prevention: Anti-surge controller, flow monitoring.
2. **Hot blast valve failure** — Root cause: Thermal cycling fatigue. Impact: Blast furnace irregularity. Prevention: Regular thermal imaging, valve exercising.

## Rolling Mill Equipment

### Drive Train Failures
1. **Gearbox tooth breakage** — Root cause: Overload during cobble, material fatigue. Impact: 48-96 hours, critical. Prevention: Overload protection, oil analysis, vibration monitoring.
2. **Universal joint failure** — Root cause: Misalignment, lubrication failure. Impact: 12-24 hours. Prevention: Alignment checks after roll change, grease quality monitoring.
3. **Motor winding burnout** — Root cause: Cooling system failure, overload protection not functioning. Impact: 2-4 weeks (rewind). Prevention: RTD monitoring, protection relay testing.

## Continuous Caster

### Mould Area Failures
1. **Breakout** — Root cause: Mould level fluctuation, inadequate cooling, copper plate wear. Impact: 8-24 hours, safety risk, production loss. Prevention: Breakout prediction system, mould maintenance schedule.
2. **Oscillation mechanism failure** — Root cause: Hydraulic cylinder seal failure, linkage wear. Impact: 4-8 hours. Prevention: Hydraulic oil analysis, mechanism inspection.

## Power Plant

### Turbine Failures
1. **Blade failure** — Root cause: Foreign object damage, creep, SCC. Impact: Weeks to months. Prevention: Steam purity control, regular NDT, online vibration monitoring.
2. **Governor hunting** — Root cause: Actuator wear, PID tuning drift. Impact: Load swings, potential trip. Prevention: Annual governor overhaul, control system audit.
"""

    docs["spare_parts_management.md"] = """# Spare Parts Management Guidelines

## Criticality-Based Stocking Strategy

### Insurance Spares (Critical)
Items that protect against catastrophic failure with long lead times:
- Turbine rotor assembly
- Large motor stator winding
- Main transformer winding
- Gearbox gear sets (custom manufactured)

**Policy**: Maintain minimum 1 unit in stock regardless of cost.

### Operational Spares (High)
Items needed for routine maintenance with moderate lead times:
- Bearings (standard sizes)
- Mechanical seals
- Coupling elements
- Filter elements
- V-belts and timing belts

**Policy**: Maintain stock based on consumption rate + safety stock.

### Consumable Spares (Medium/Low)
Items consumed regularly:
- Lubricants and greases
- Gaskets and O-rings
- Fasteners
- Packing materials

**Policy**: Reorder point based on usage rate.

## Lead Time Reference
| Item Category | Typical Lead Time | Emergency Lead Time |
|--------------|------------------|-------------------|
| Standard bearings | 1-2 weeks | 2-3 days |
| Mechanical seals | 2-4 weeks | 1 week |
| Motor windings | 8-12 weeks | 3-4 weeks |
| Custom gears | 10-16 weeks | 6-8 weeks |
| Turbine blades | 16-24 weeks | 8-12 weeks |
| Transformer parts | 12-20 weeks | 6-10 weeks |

## Vendor Contact for Emergency Procurement
- Bearings: SKF India (24-hour emergency line)
- Seals: John Crane / EagleBurgmann
- Motors: ABB / Siemens India
- Gearboxes: Flender / SEW Eurodrive
"""

    for filename, content in docs.items():
        filepath = os.path.join(KNOWLEDGE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())

    return list(docs.keys())


def main():
    print("🏭 Generating Synthetic Steel Plant Data...")

    # 1. Generate knowledge base
    print("  📚 Creating knowledge base documents...")
    kb_files = generate_knowledge_base()
    print(f"     Created {len(kb_files)} knowledge documents")

    # 2. Generate sensor data
    print("  📊 Generating 90-day sensor time-series...")
    sensor_data = generate_sensor_data(EQUIPMENT)
    print(f"     Generated data for {len(sensor_data)} equipment items")

    # 3. Compute equipment status
    print("  🔧 Computing equipment health scores...")
    enriched_equipment = compute_equipment_status(EQUIPMENT, sensor_data)

    # 4. Generate maintenance logs
    print("  📝 Generating maintenance logs...")
    maintenance_logs = generate_maintenance_logs(EQUIPMENT)
    print(f"     Created {len(maintenance_logs)} log entries")

    # 5. Generate failure reports
    print("  📋 Generating failure reports...")
    failure_reports = generate_failure_reports(EQUIPMENT)
    print(f"     Created {len(failure_reports)} failure reports")

    # 6. Save everything
    print("  💾 Saving data files...")

    with open(os.path.join(OUTPUT_DIR, "equipment.json"), "w") as f:
        json.dump(enriched_equipment, f, indent=2)

    # Save only last 7 days of sensor data for API (full data too large)
    recent_sensor = {}
    for eid, readings in sensor_data.items():
        recent_sensor[eid] = readings[-42:]  # 7 days * 6 readings/day

    with open(os.path.join(OUTPUT_DIR, "sensor_data.json"), "w") as f:
        json.dump(recent_sensor, f, indent=2)

    # Save full sensor data for ML training
    with open(os.path.join(OUTPUT_DIR, "sensor_data_full.json"), "w") as f:
        json.dump(sensor_data, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "maintenance_logs.json"), "w") as f:
        json.dump(maintenance_logs, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "failure_reports.json"), "w") as f:
        json.dump(failure_reports, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "spare_parts.json"), "w") as f:
        json.dump(SPARE_PARTS, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "failure_modes.json"), "w") as f:
        json.dump(FAILURE_MODES, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "sensor_ranges.json"), "w") as f:
        json.dump(SENSOR_RANGES, f, indent=2)

    print("\n✅ Data generation complete!")
    print(f"   Equipment: {len(enriched_equipment)} items")
    print(f"   Sensor readings: ~{sum(len(v) for v in sensor_data.values())} data points")
    print(f"   Maintenance logs: {len(maintenance_logs)}")
    print(f"   Failure reports: {len(failure_reports)}")
    print(f"   Knowledge docs: {len(kb_files)}")


if __name__ == "__main__":
    main()
