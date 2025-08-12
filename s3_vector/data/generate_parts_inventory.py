#!/usr/bin/env python3
"""
Automotive Parts Inventory Generator
===================================

Generates a normalized parts inventory with realistic automotive parts and dealer availability.

Usage:
    python generate_parts_inventory.py [--count N]

Options:
    --count N    Number of parts to generate (default: 50)
"""

import json
import random
import argparse
from typing import Dict, List, Any


class PartsInventoryGenerator:
    def __init__(self):
        # Load dealer database to reference dealer IDs
        try:
            with open('normalized_dealer_database.json', 'r') as f:
                dealer_db = json.load(f)
                self.dealer_ids = list(dealer_db.keys())
        except FileNotFoundError:
            print("Warning: normalized_dealer_database.json not found. Using default dealer IDs.")
            self.dealer_ids = [f"DEALER-{i:03d}" for i in range(1, 21)]  # Default 20 dealers
        
        # Part categories and their components
        self.part_categories = {
            "brake": {
                "parts": [
                    ("Brake Pads (Front)", "BP-F"),
                    ("Brake Pads (Rear)", "BP-R"), 
                    ("Brake Rotors (Front)", "BR-F"),
                    ("Brake Rotors (Rear)", "BR-R"),
                    ("Brake Calipers (Front)", "BC-F"),
                    ("Brake Calipers (Rear)", "BC-R"),
                    ("Brake Master Cylinder", "BMC"),
                    ("Brake Fluid", "BF"),
                    ("Brake Lines", "BL"),
                    ("Brake Booster", "BB")
                ],
                "vehicles": ["Honda Accord", "Honda Civic", "Toyota Camry", "Nissan Altima", "Ford Fusion"]
            },
            "engine": {
                "parts": [
                    ("Oil Filter", "OF"),
                    ("Air Filter", "AF"),
                    ("Fuel Filter", "FF"),
                    ("Spark Plugs", "SP"),
                    ("Ignition Coils", "IC"),
                    ("Timing Belt", "TB"),
                    ("Water Pump", "WP"),
                    ("Thermostat", "TH"),
                    ("Radiator", "RAD"),
                    ("Engine Mount", "EM")
                ],
                "vehicles": ["BMW X3", "BMW 3 Series", "Mercedes C-Class", "Audi Q3", "Lexus RX"]
            },
            "transmission": {
                "parts": [
                    ("Transmission Filter", "TF"),
                    ("Transmission Fluid", "TFL"),
                    ("Clutch Kit", "CK"),
                    ("CV Joint", "CVJ"),
                    ("Drive Belt", "DB"),
                    ("Transmission Mount", "TM"),
                    ("Torque Converter", "TC"),
                    ("Shift Solenoid", "SS"),
                    ("Transmission Cooler", "TCL"),
                    ("Axle Shaft", "AS")
                ],
                "vehicles": ["Ford F-150", "Chevrolet Silverado", "GMC Sierra", "Ram 1500", "Toyota Tundra"]
            },
            "suspension": {
                "parts": [
                    ("Shock Absorbers (Front)", "SA-F"),
                    ("Shock Absorbers (Rear)", "SA-R"),
                    ("Struts (Front)", "ST-F"),
                    ("Struts (Rear)", "ST-R"),
                    ("Control Arms", "CA"),
                    ("Ball Joints", "BJ"),
                    ("Sway Bar Links", "SBL"),
                    ("Coil Springs", "CS"),
                    ("Tie Rod Ends", "TRE"),
                    ("Stabilizer Bar", "SB")
                ],
                "vehicles": ["Tesla Model 3", "Tesla Model Y", "Hyundai Elantra", "Kia Forte", "Subaru Outback"]
            },
            "electrical": {
                "parts": [
                    ("Battery", "BAT"),
                    ("Alternator", "ALT"),
                    ("Starter", "STR"),
                    ("Headlight Bulbs", "HLB"),
                    ("Tail Light Bulbs", "TLB"),
                    ("Fuses", "FUS"),
                    ("Wiring Harness", "WH"),
                    ("ECU Module", "ECU"),
                    ("Sensors", "SEN"),
                    ("Relays", "REL")
                ],
                "vehicles": ["Mazda CX-5", "Volkswagen Jetta", "Volvo XC60", "Jaguar XE", "Land Rover Discovery"]
            }
        }

    def generate_part_id(self, category: str, part_code: str, index: int) -> str:
        """Generate a part ID."""
        return f"{part_code}-{index:03d}"

    def generate_part_inventory(self, part_id: str, part_name: str, category: str, vehicles: List[str]) -> Dict[str, Any]:
        """Generate inventory data for a single part."""
        # Select random dealers that carry this part (3-6 dealers)
        num_dealers = random.randint(3, min(6, len(self.dealer_ids)))
        selected_dealers = random.sample(self.dealer_ids, num_dealers)
        
        dealers_inventory = {}
        
        for dealer_id in selected_dealers:
            # Generate realistic inventory data
            quantity = random.choices(
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                weights=[5, 10, 15, 20, 20, 15, 8, 4, 2, 1, 1]  # More likely to have 1-5 items
            )[0]
            
            # Price varies by dealer (base price ± 20%)
            base_price = self.get_base_price(category, part_name)
            price_variation = random.uniform(0.8, 1.2)
            price = round(base_price * price_variation, 2)
            
            # Delivery days based on quantity and dealer
            if quantity == 0:
                delivery_days = random.randint(3, 7)  # Need to order
            elif quantity <= 2:
                delivery_days = random.randint(1, 3)  # Low stock
            else:
                delivery_days = 1  # In stock
            
            dealers_inventory[dealer_id] = {
                "quantity": quantity,
                "price": price,
                "delivery_days": delivery_days
            }
        
        # Select compatible vehicles (3-5 vehicles)
        compatible_vehicles = random.sample(vehicles, random.randint(3, min(5, len(vehicles))))
        
        return {
            "name": part_name,
            "category": category,
            "compatible_vehicles": compatible_vehicles,
            "dealers": dealers_inventory
        }

    def get_base_price(self, category: str, part_name: str) -> float:
        """Get base price for a part based on category and type."""
        price_ranges = {
            "brake": {
                "pads": (45, 120),
                "rotors": (80, 200),
                "calipers": (150, 400),
                "master cylinder": (200, 350),
                "fluid": (15, 30),
                "lines": (25, 80),
                "booster": (300, 600)
            },
            "engine": {
                "filter": (10, 40),
                "plugs": (8, 25),
                "coils": (80, 200),
                "belt": (30, 120),
                "pump": (150, 400),
                "thermostat": (20, 60),
                "radiator": (200, 500),
                "mount": (50, 150)
            },
            "transmission": {
                "filter": (25, 60),
                "fluid": (20, 40),
                "clutch": (300, 800),
                "joint": (100, 250),
                "belt": (20, 80),
                "mount": (80, 200),
                "converter": (400, 1000),
                "solenoid": (150, 350),
                "cooler": (200, 400),
                "shaft": (200, 500)
            },
            "suspension": {
                "shock": (80, 250),
                "struts": (120, 350),
                "arms": (100, 300),
                "joints": (40, 120),
                "links": (25, 80),
                "springs": (60, 200),
                "ends": (30, 100),
                "bar": (80, 250)
            },
            "electrical": {
                "battery": (100, 300),
                "alternator": (200, 500),
                "starter": (150, 400),
                "bulbs": (10, 50),
                "fuses": (5, 20),
                "harness": (50, 200),
                "module": (300, 1000),
                "sensors": (50, 200),
                "relays": (15, 50)
            }
        }
        
        # Find matching price range
        part_lower = part_name.lower()
        category_prices = price_ranges.get(category, {})
        
        for key, (min_price, max_price) in category_prices.items():
            if key in part_lower:
                return random.uniform(min_price, max_price)
        
        # Default price range if no match found
        return random.uniform(50, 200)

    def generate_inventory(self, count: int = 50) -> Dict[str, Any]:
        """Generate the complete parts inventory."""
        print(f"Generating {count} parts inventory records...")
        
        inventory = {}
        parts_generated = 0
        
        # Distribute parts across categories
        categories = list(self.part_categories.keys())
        parts_per_category = count // len(categories)
        remaining_parts = count % len(categories)
        
        for category_idx, category in enumerate(categories):
            category_data = self.part_categories[category]
            parts_list = category_data["parts"]
            vehicles = category_data["vehicles"]
            
            # Calculate how many parts to generate for this category
            category_count = parts_per_category
            if category_idx < remaining_parts:
                category_count += 1
            
            # Generate parts for this category
            for i in range(category_count):
                if i < len(parts_list):
                    part_name, part_code = parts_list[i]
                else:
                    # If we need more parts than available, cycle through
                    part_name, part_code = parts_list[i % len(parts_list)]
                    part_name = f"{part_name} (Variant {i // len(parts_list) + 1})"
                
                part_id = self.generate_part_id(category, part_code, parts_generated + 1)
                inventory[part_id] = self.generate_part_inventory(part_id, part_name, category, vehicles)
                parts_generated += 1
                
                if parts_generated % 10 == 0:
                    print(f"Generated {parts_generated}/{count} parts...")
        
        return inventory

    def save_inventory(self, inventory: Dict[str, Any], filename: str = "normalized_parts_inventory.json"):
        """Save the inventory to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(inventory)} parts to {filename}")
        
        # Print summary statistics
        categories = {}
        total_dealers = set()
        
        for part in inventory.values():
            category = part['category']
            categories[category] = categories.get(category, 0) + 1
            total_dealers.update(part['dealers'].keys())
        
        print(f"📊 Summary:")
        print(f"   Total parts: {len(inventory)}")
        print(f"   Dealers with inventory: {len(total_dealers)}")
        print(f"   Category distribution:")
        for category, count in sorted(categories.items()):
            print(f"     {category}: {count} parts")


def main():
    parser = argparse.ArgumentParser(description='Generate automotive parts inventory')
    parser.add_argument('--count', type=int, default=50, 
                       help='Number of parts to generate (default: 50)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Count must be at least 1")
        return
    
    generator = PartsInventoryGenerator()
    inventory = generator.generate_inventory(args.count)
    generator.save_inventory(inventory)


if __name__ == "__main__":
    main()