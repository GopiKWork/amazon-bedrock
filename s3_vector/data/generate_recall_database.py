#!/usr/bin/env python3
"""
Automotive Recall Database Generator
===================================

Generates a normalized recall database with realistic automotive recall information.

Usage:
    python generate_recall_database.py [--count N]

Options:
    --count N    Number of recalls to generate (default: 50)
"""

import json
import random
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple


class RecallDatabaseGenerator:
    def __init__(self):
        # Load dealer database to reference dealer IDs
        try:
            with open('normalized_dealer_database.json', 'r') as f:
                dealer_db = json.load(f)
                self.dealer_ids = list(dealer_db.keys())
        except FileNotFoundError:
            print("Warning: normalized_dealer_database.json not found. Using default dealer IDs.")
            self.dealer_ids = [f"DEALER-{i:03d}" for i in range(1, 21)]
        
        # Manufacturers and their VIN patterns
        self.manufacturers = {
            "Honda": {
                "models": ["Accord", "Civic", "CR-V", "Pilot", "Odyssey", "Fit", "HR-V", "Passport"],
                "vin_patterns": ["1HGBH41JXMN*", "1HGBH41JXMM*", "19XFC2F5*", "5FNYF4H*"]
            },
            "Toyota": {
                "models": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Sienna", "Tacoma", "4Runner"],
                "vin_patterns": ["4T1BF1FK*", "JTDKN3DP*", "2T3BFREV*", "5TDZA23C*"]
            },
            "Ford": {
                "models": ["F-150", "Escape", "Explorer", "Mustang", "Focus", "Fusion", "Edge", "Expedition"],
                "vin_patterns": ["1FTFW1ET*", "1FMCU0D*", "1FM5K8D*", "1FA6P8TH*"]
            },
            "BMW": {
                "models": ["3 Series", "X3", "X5", "5 Series", "7 Series", "X1", "X7", "Z4"],
                "vin_patterns": ["WBXHT910*", "WBXHT920*", "5UXCR6C0*", "WBA8E1C0*"]
            },
            "Mercedes": {
                "models": ["C-Class", "E-Class", "S-Class", "GLC", "GLE", "A-Class", "CLA", "GLS"],
                "vin_patterns": ["WDDGF4HB*", "W1KZF8DB*", "4JGDA5HB*", "WDC0G4HB*"]
            },
            "Chevrolet": {
                "models": ["Silverado", "Equinox", "Malibu", "Traverse", "Tahoe", "Suburban", "Camaro", "Corvette"],
                "vin_patterns": ["1GCRYDED*", "2GNAXSEV*", "1G1ZB5ST*", "1GNSKCKC*"]
            },
            "Nissan": {
                "models": ["Altima", "Sentra", "Rogue", "Pathfinder", "Murano", "Maxima", "Frontier", "Titan"],
                "vin_patterns": ["1N4AL3AP*", "3N1AB7AP*", "5N1AT2MT*", "5N1DR2MN*"]
            },
            "Hyundai": {
                "models": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Accent", "Veloster", "Genesis", "Palisade"],
                "vin_patterns": ["KMHD14LA*", "5NPE34AF*", "KM8J33A4*", "KM8SM4HF*"]
            }
        }
        
        # Recall categories and their typical issues
        self.recall_categories = {
            "engine": {
                "issues": [
                    ("Fuel pump may fail causing engine stall", "Replace fuel pump assembly", "High"),
                    ("Engine oil leak may cause fire risk", "Replace oil pan gasket", "Critical"),
                    ("Timing chain may break causing engine damage", "Replace timing chain and guides", "High"),
                    ("Coolant leak may cause overheating", "Replace radiator hose", "Medium"),
                    ("Air intake manifold may crack", "Replace intake manifold", "Medium"),
                    ("Engine mount may fail causing vibration", "Replace engine mount", "Low"),
                    ("Fuel injector may leak causing poor performance", "Replace fuel injectors", "Medium"),
                    ("Turbocharger may fail causing loss of power", "Replace turbocharger assembly", "High")
                ],
                "parts": ["FP-001", "OPG-001", "TC-001", "RH-001", "IM-001", "EM-001", "FI-001", "TCA-001"]
            },
            "brake": {
                "issues": [
                    ("Brake fluid leak may reduce braking effectiveness", "Replace brake master cylinder", "Critical"),
                    ("Brake pads may wear prematurely", "Replace brake pads and rotors", "High"),
                    ("ABS system may malfunction", "Update ABS software and replace module", "High"),
                    ("Brake pedal may feel spongy", "Bleed brake system and replace fluid", "Medium"),
                    ("Parking brake may not engage properly", "Adjust parking brake cable", "Medium"),
                    ("Brake caliper may seize", "Replace brake calipers", "High"),
                    ("Brake booster may fail", "Replace brake booster", "Critical"),
                    ("Brake lines may corrode", "Replace brake lines", "Critical")
                ],
                "parts": ["BMC-001", "BP-001", "ABS-001", "BF-001", "PBC-001", "BC-001", "BB-001", "BL-001"]
            },
            "electrical": {
                "issues": [
                    ("Wiring harness may short circuit causing fire", "Replace wiring harness", "Critical"),
                    ("Battery may overheat and leak", "Replace battery pack", "Critical"),
                    ("Alternator may fail causing loss of power", "Replace alternator", "High"),
                    ("Headlights may fail unexpectedly", "Replace headlight assembly", "Medium"),
                    ("ECU software may cause erratic behavior", "Update ECU software", "Medium"),
                    ("Starter may fail to engage", "Replace starter motor", "Medium"),
                    ("Power window switches may malfunction", "Replace window switch assembly", "Low"),
                    ("Radio may interfere with safety systems", "Update radio software", "Low")
                ],
                "parts": ["WH-001", "BAT-001", "ALT-001", "HL-001", "ECU-001", "STR-001", "PWS-001", "RAD-001"]
            },
            "transmission": {
                "issues": [
                    ("Transmission may slip or fail to shift", "Replace transmission valve body", "High"),
                    ("CVT belt may break causing loss of power", "Replace CVT belt and pulleys", "High"),
                    ("Clutch may not disengage properly", "Replace clutch assembly", "High"),
                    ("Transmission fluid may leak", "Replace transmission seals", "Medium"),
                    ("Shift solenoid may stick", "Replace shift solenoids", "Medium"),
                    ("Torque converter may fail", "Replace torque converter", "High"),
                    ("Transmission mount may break", "Replace transmission mount", "Medium"),
                    ("Final drive may make noise", "Replace final drive assembly", "High")
                ],
                "parts": ["TVB-001", "CVT-001", "CL-001", "TS-001", "SS-001", "TC-001", "TM-001", "FD-001"]
            },
            "suspension": {
                "issues": [
                    ("Suspension struts may leak causing poor handling", "Replace suspension struts", "Medium"),
                    ("Control arm bushings may wear prematurely", "Replace control arm bushings", "Medium"),
                    ("Ball joints may separate causing loss of control", "Replace ball joints", "Critical"),
                    ("Sway bar links may break", "Replace sway bar links", "Low"),
                    ("Shock absorbers may fail", "Replace shock absorbers", "Medium"),
                    ("Coil springs may break", "Replace coil springs", "High"),
                    ("Tie rod ends may wear causing steering issues", "Replace tie rod ends", "High"),
                    ("Stabilizer bar may crack", "Replace stabilizer bar", "Medium")
                ],
                "parts": ["SS-001", "CAB-001", "BJ-001", "SBL-001", "SA-001", "CS-001", "TRE-001", "SB-001"]
            }
        }
        
        self.severity_levels = ["Low", "Medium", "High", "Critical"]
        self.current_year = datetime.now().year

    def generate_recall_id(self, index: int) -> str:
        """Generate a recall ID."""
        year = random.randint(2020, self.current_year)
        return f"RECALL-{year}-{index:03d}"

    def generate_nhtsa_number(self, year: int, index: int) -> str:
        """Generate a realistic NHTSA recall number."""
        return f"NHTSA-{year % 100}V-{index:03d}"

    def generate_vin_patterns(self, manufacturer: str) -> List[str]:
        """Generate VIN patterns for a manufacturer."""
        patterns = self.manufacturers[manufacturer]["vin_patterns"]
        return random.sample(patterns, random.randint(1, min(3, len(patterns))))

    def select_models_and_years(self, manufacturer: str) -> Tuple[List[str], List[int]]:
        """Select models and years for a recall."""
        available_models = self.manufacturers[manufacturer]["models"]
        selected_models = random.sample(available_models, random.randint(1, min(3, len(available_models))))
        
        # Generate consecutive years (recalls often affect multiple model years)
        start_year = random.randint(2015, self.current_year - 2)
        num_years = random.randint(1, 4)
        years = list(range(start_year, min(start_year + num_years, self.current_year + 1)))
        
        return selected_models, years

    def calculate_affected_vehicles(self, models: List[str], years: List[int]) -> int:
        """Calculate realistic number of affected vehicles."""
        # Base numbers per model per year
        base_per_model_year = random.randint(5000, 50000)
        total = base_per_model_year * len(models) * len(years)
        
        # Add some randomness
        variation = random.uniform(0.7, 1.3)
        return int(total * variation)

    def select_recommended_dealers(self, manufacturer: str) -> List[str]:
        """Select dealers that specialize in the manufacturer."""
        # In a real system, we'd filter by manufacturer specialty
        # For now, randomly select 2-4 dealers
        num_dealers = random.randint(2, min(4, len(self.dealer_ids)))
        return random.sample(self.dealer_ids, num_dealers)

    def generate_recall(self, index: int) -> Dict[str, Any]:
        """Generate a single recall record."""
        recall_id = self.generate_recall_id(index)
        manufacturer = random.choice(list(self.manufacturers.keys()))
        category = random.choice(list(self.recall_categories.keys()))
        
        # Get issue details for the category
        category_data = self.recall_categories[category]
        issue_data = random.choice(category_data["issues"])
        description, remedy, severity = issue_data
        
        # Select parts needed
        available_parts = category_data["parts"]
        num_parts = random.randint(1, min(3, len(available_parts)))
        parts_needed = random.sample(available_parts, num_parts)
        
        # Generate other details
        vin_patterns = self.generate_vin_patterns(manufacturer)
        models, years = self.select_models_and_years(manufacturer)
        affected_vehicles = self.calculate_affected_vehicles(models, years)
        recommended_dealers = self.select_recommended_dealers(manufacturer)
        
        # Estimate repair time based on severity and complexity
        time_ranges = {
            "Low": (1, 2),
            "Medium": (2, 4),
            "High": (3, 6),
            "Critical": (4, 8)
        }
        min_time, max_time = time_ranges[severity]
        repair_time = f"{min_time}-{max_time} hours"
        
        # Generate NHTSA number
        recall_year = int(recall_id.split('-')[1])
        nhtsa_number = self.generate_nhtsa_number(recall_year, index)
        
        recall = {
            "vin_patterns": vin_patterns,
            "manufacturer": manufacturer,
            "models": models,
            "years": years,
            "description": description,
            "severity": severity,
            "remedy": remedy,
            "estimated_repair_time": repair_time,
            "recall_number": nhtsa_number,
            "affected_vehicles": affected_vehicles,
            "parts_needed": parts_needed,
            "recommended_dealers": recommended_dealers
        }
        
        return recall

    def generate_database(self, count: int = 50) -> Dict[str, Any]:
        """Generate the complete recall database."""
        print(f"Generating {count} recall records...")
        
        database = {}
        
        for i in range(1, count + 1):
            recall_id = self.generate_recall_id(i)
            recall = self.generate_recall(i)
            database[recall_id] = recall
            
            if i % 10 == 0:
                print(f"Generated {i}/{count} recalls...")
        
        return database

    def save_database(self, database: Dict[str, Any], filename: str = "normalized_recall_database.json"):
        """Save the database to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(database)} recalls to {filename}")
        
        # Print summary statistics
        manufacturers = {}
        severities = {}
        total_affected = 0
        
        for recall in database.values():
            manufacturer = recall['manufacturer']
            severity = recall['severity']
            
            manufacturers[manufacturer] = manufacturers.get(manufacturer, 0) + 1
            severities[severity] = severities.get(severity, 0) + 1
            total_affected += recall['affected_vehicles']
        
        print(f"📊 Summary:")
        print(f"   Total recalls: {len(database)}")
        print(f"   Total affected vehicles: {total_affected:,}")
        print(f"   Average per recall: {total_affected // len(database):,}")
        print(f"   Manufacturer distribution:")
        for manufacturer, count in sorted(manufacturers.items()):
            print(f"     {manufacturer}: {count} recalls")
        print(f"   Severity distribution:")
        for severity, count in sorted(severities.items()):
            print(f"     {severity}: {count} recalls")


def main():
    parser = argparse.ArgumentParser(description='Generate automotive recall database')
    parser.add_argument('--count', type=int, default=50, 
                       help='Number of recalls to generate (default: 50)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Count must be at least 1")
        return
    
    generator = RecallDatabaseGenerator()
    database = generator.generate_database(args.count)
    generator.save_database(database)


if __name__ == "__main__":
    main()