#!/usr/bin/env python3
"""
Automotive Parts Catalog Generator
==================================

Generates a parts catalog organized by category with OEM and aftermarket options.

Usage:
    python generate_parts_catalog.py [--count N]

Options:
    --count N    Number of parts to generate (default: 50)
"""

import json
import random
import argparse
from typing import Dict, List, Any


class PartsCatalogGenerator:
    def __init__(self):
        # Part categories with detailed specifications
        self.part_categories = {
            "brake": {
                "parts": [
                    {
                        "name": "Brake Pads (Front)",
                        "code": "BP-F",
                        "oem_price_range": (60, 150),
                        "am_price_range": (25, 80),
                        "vehicles": ["Honda Accord", "Honda Civic", "Toyota Camry", "Nissan Altima", "Ford Fusion", "Chevrolet Malibu"]
                    },
                    {
                        "name": "Brake Pads (Rear)",
                        "code": "BP-R", 
                        "oem_price_range": (50, 120),
                        "am_price_range": (20, 70),
                        "vehicles": ["Honda Accord", "Honda Civic", "Toyota Camry", "Nissan Altima", "Ford Fusion", "Chevrolet Malibu"]
                    },
                    {
                        "name": "Brake Rotors (Front)",
                        "code": "BR-F",
                        "oem_price_range": (80, 250),
                        "am_price_range": (40, 120),
                        "vehicles": ["BMW X3", "BMW 3 Series", "Mercedes C-Class", "Audi Q3", "Lexus RX", "Acura MDX"]
                    },
                    {
                        "name": "Brake Rotors (Rear)",
                        "code": "BR-R",
                        "oem_price_range": (70, 200),
                        "am_price_range": (35, 100),
                        "vehicles": ["BMW X3", "BMW 3 Series", "Mercedes C-Class", "Audi Q3", "Lexus RX", "Acura MDX"]
                    },
                    {
                        "name": "Brake Calipers (Front)",
                        "code": "BC-F",
                        "oem_price_range": (200, 500),
                        "am_price_range": (100, 250),
                        "vehicles": ["Ford F-150", "Chevrolet Silverado", "GMC Sierra", "Ram 1500", "Toyota Tundra"]
                    },
                    {
                        "name": "Brake Master Cylinder",
                        "code": "BMC",
                        "oem_price_range": (150, 400),
                        "am_price_range": (75, 200),
                        "vehicles": ["Hyundai Elantra", "Kia Forte", "Mazda CX-5", "Subaru Outback", "Volkswagen Jetta"]
                    }
                ]
            },
            "engine": {
                "parts": [
                    {
                        "name": "Oil Filter",
                        "code": "OF",
                        "oem_price_range": (8, 25),
                        "am_price_range": (3, 12),
                        "vehicles": ["Honda Civic", "Toyota Corolla", "Nissan Sentra", "Ford Focus", "Chevrolet Cruze"]
                    },
                    {
                        "name": "Air Filter",
                        "code": "AF",
                        "oem_price_range": (15, 40),
                        "am_price_range": (8, 20),
                        "vehicles": ["Honda Accord", "Toyota Camry", "Nissan Altima", "Ford Fusion", "Chevrolet Malibu"]
                    },
                    {
                        "name": "Spark Plugs (Set of 4)",
                        "code": "SP",
                        "oem_price_range": (25, 80),
                        "am_price_range": (12, 40),
                        "vehicles": ["Honda Civic", "Toyota Corolla", "Mazda3", "Hyundai Elantra", "Kia Forte"]
                    },
                    {
                        "name": "Ignition Coils",
                        "code": "IC",
                        "oem_price_range": (80, 200),
                        "am_price_range": (40, 100),
                        "vehicles": ["BMW 3 Series", "Mercedes C-Class", "Audi A4", "Lexus IS", "Acura TLX"]
                    },
                    {
                        "name": "Timing Belt",
                        "code": "TB",
                        "oem_price_range": (50, 150),
                        "am_price_range": (25, 75),
                        "vehicles": ["Honda Accord", "Toyota Camry", "Subaru Outback", "Volkswagen Jetta", "Volvo XC60"]
                    },
                    {
                        "name": "Water Pump",
                        "code": "WP",
                        "oem_price_range": (150, 400),
                        "am_price_range": (75, 200),
                        "vehicles": ["Ford F-150", "Chevrolet Silverado", "Toyota Tundra", "Nissan Titan", "Ram 1500"]
                    }
                ]
            },
            "transmission": {
                "parts": [
                    {
                        "name": "Transmission Filter",
                        "code": "TF",
                        "oem_price_range": (25, 60),
                        "am_price_range": (12, 30),
                        "vehicles": ["Honda Accord", "Toyota Camry", "Ford Fusion", "Chevrolet Malibu", "Nissan Altima"]
                    },
                    {
                        "name": "Transmission Fluid (Quart)",
                        "code": "TFL",
                        "oem_price_range": (15, 35),
                        "am_price_range": (8, 18),
                        "vehicles": ["Honda Civic", "Toyota Corolla", "Ford Focus", "Chevrolet Cruze", "Nissan Sentra"]
                    },
                    {
                        "name": "Clutch Kit",
                        "code": "CK",
                        "oem_price_range": (400, 1000),
                        "am_price_range": (200, 500),
                        "vehicles": ["Honda Civic Si", "Subaru WRX", "Mazda MX-5", "Ford Mustang", "Volkswagen GTI"]
                    },
                    {
                        "name": "CV Joint",
                        "code": "CVJ",
                        "oem_price_range": (100, 300),
                        "am_price_range": (50, 150),
                        "vehicles": ["Honda CR-V", "Toyota RAV4", "Mazda CX-5", "Subaru Forester", "Hyundai Tucson"]
                    }
                ]
            },
            "suspension": {
                "parts": [
                    {
                        "name": "Shock Absorbers (Front)",
                        "code": "SA-F",
                        "oem_price_range": (100, 300),
                        "am_price_range": (50, 150),
                        "vehicles": ["Ford F-150", "Chevrolet Silverado", "Toyota Tundra", "Ram 1500", "GMC Sierra"]
                    },
                    {
                        "name": "Struts (Front)",
                        "code": "ST-F",
                        "oem_price_range": (150, 400),
                        "am_price_range": (75, 200),
                        "vehicles": ["Honda Accord", "Toyota Camry", "Nissan Altima", "Ford Fusion", "Chevrolet Malibu"]
                    },
                    {
                        "name": "Control Arms",
                        "code": "CA",
                        "oem_price_range": (120, 350),
                        "am_price_range": (60, 175),
                        "vehicles": ["BMW 3 Series", "Mercedes C-Class", "Audi A4", "Lexus IS", "Acura TLX"]
                    },
                    {
                        "name": "Ball Joints",
                        "code": "BJ",
                        "oem_price_range": (50, 150),
                        "am_price_range": (25, 75),
                        "vehicles": ["Honda CR-V", "Toyota RAV4", "Ford Escape", "Chevrolet Equinox", "Nissan Rogue"]
                    }
                ]
            },
            "electrical": {
                "parts": [
                    {
                        "name": "Battery",
                        "code": "BAT",
                        "oem_price_range": (120, 300),
                        "am_price_range": (60, 150),
                        "vehicles": ["Honda Accord", "Toyota Camry", "Ford Fusion", "Chevrolet Malibu", "Nissan Altima"]
                    },
                    {
                        "name": "Alternator",
                        "code": "ALT",
                        "oem_price_range": (250, 600),
                        "am_price_range": (125, 300),
                        "vehicles": ["Ford F-150", "Chevrolet Silverado", "Toyota Tundra", "Ram 1500", "GMC Sierra"]
                    },
                    {
                        "name": "Starter",
                        "code": "STR",
                        "oem_price_range": (200, 500),
                        "am_price_range": (100, 250),
                        "vehicles": ["Honda Civic", "Toyota Corolla", "Nissan Sentra", "Ford Focus", "Chevrolet Cruze"]
                    },
                    {
                        "name": "Headlight Assembly",
                        "code": "HLA",
                        "oem_price_range": (150, 500),
                        "am_price_range": (75, 250),
                        "vehicles": ["BMW X3", "Mercedes GLC", "Audi Q5", "Lexus RX", "Acura MDX"]
                    }
                ]
            }
        }

    def generate_part_id(self, category: str, code: str, index: int) -> str:
        """Generate a part ID."""
        return f"{code}-{index:03d}"

    def generate_oem_part_number(self, code: str, index: int) -> str:
        """Generate OEM part number."""
        return f"{code}-{index:03d}"

    def generate_aftermarket_part_number(self, code: str, index: int) -> str:
        """Generate aftermarket part number."""
        return f"AM-{code}-{index:03d}"

    def generate_part_entry(self, category: str, part_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Generate a single part catalog entry."""
        part_id = self.generate_part_id(category, part_data["code"], index)
        oem_part = self.generate_oem_part_number(part_data["code"], index)
        aftermarket_part = self.generate_aftermarket_part_number(part_data["code"], index)
        
        # Generate prices within the specified ranges
        oem_min, oem_max = part_data["oem_price_range"]
        am_min, am_max = part_data["am_price_range"]
        
        oem_cost = round(random.uniform(oem_min, oem_max), 2)
        am_cost = round(random.uniform(am_min, am_max), 2)
        
        # Select compatible vehicles (3-5 vehicles from the list)
        available_vehicles = part_data["vehicles"]
        num_vehicles = random.randint(3, min(5, len(available_vehicles)))
        compatible_vehicles = random.sample(available_vehicles, num_vehicles)
        
        # Quantity is typically 1 for most parts, but some parts come in sets
        quantity = 1
        if "set" in part_data["name"].lower() or "kit" in part_data["name"].lower():
            quantity = random.choice([1, 2, 4])  # Sets can be 1, 2, or 4 pieces
        
        return {
            "part_id": part_id,
            "name": part_data["name"],
            "category": category,
            "oem_part": oem_part,
            "aftermarket": aftermarket_part,
            "quantity": quantity,
            "oem_cost": oem_cost,
            "am_cost": am_cost,
            "compatible_vehicles": compatible_vehicles
        }

    def generate_catalog(self, count: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """Generate the complete parts catalog."""
        print(f"Generating {count} parts catalog entries...")
        
        catalog = {}
        parts_generated = 0
        
        # Distribute parts across categories
        categories = list(self.part_categories.keys())
        parts_per_category = count // len(categories)
        remaining_parts = count % len(categories)
        
        for category_idx, category in enumerate(categories):
            category_data = self.part_categories[category]
            parts_list = category_data["parts"]
            
            # Calculate how many parts to generate for this category
            category_count = parts_per_category
            if category_idx < remaining_parts:
                category_count += 1
            
            catalog[category] = []
            
            # Generate parts for this category
            for i in range(category_count):
                if i < len(parts_list):
                    part_data = parts_list[i]
                else:
                    # If we need more parts than available, cycle through with variations
                    base_part = parts_list[i % len(parts_list)]
                    part_data = base_part.copy()
                    variant_num = i // len(parts_list) + 1
                    part_data["name"] = f"{base_part['name']} (Variant {variant_num})"
                    part_data["code"] = f"{base_part['code']}-V{variant_num}"
                
                part_entry = self.generate_part_entry(category, part_data, parts_generated + 1)
                catalog[category].append(part_entry)
                parts_generated += 1
                
                if parts_generated % 10 == 0:
                    print(f"Generated {parts_generated}/{count} parts...")
        
        return catalog

    def save_catalog(self, catalog: Dict[str, List[Dict[str, Any]]], filename: str = "parts_catalog.json"):
        """Save the catalog to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        total_parts = sum(len(parts) for parts in catalog.values())
        print(f"✅ Saved {total_parts} parts to {filename}")
        
        # Print summary statistics
        total_oem_value = 0
        total_am_value = 0
        
        print(f"📊 Summary:")
        print(f"   Total parts: {total_parts}")
        print(f"   Category distribution:")
        
        for category, parts in catalog.items():
            category_oem_value = sum(part['oem_cost'] for part in parts)
            category_am_value = sum(part['am_cost'] for part in parts)
            
            total_oem_value += category_oem_value
            total_am_value += category_am_value
            
            print(f"     {category}: {len(parts)} parts")
            print(f"       OEM value: ${category_oem_value:,.2f}")
            print(f"       Aftermarket value: ${category_am_value:,.2f}")
        
        savings = total_oem_value - total_am_value
        savings_percent = (savings / total_oem_value) * 100 if total_oem_value > 0 else 0
        
        print(f"   Total catalog value:")
        print(f"     OEM: ${total_oem_value:,.2f}")
        print(f"     Aftermarket: ${total_am_value:,.2f}")
        print(f"     Potential savings: ${savings:,.2f} ({savings_percent:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description='Generate automotive parts catalog')
    parser.add_argument('--count', type=int, default=50, 
                       help='Number of parts to generate (default: 50)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Count must be at least 1")
        return
    
    generator = PartsCatalogGenerator()
    catalog = generator.generate_catalog(args.count)
    generator.save_catalog(catalog)


if __name__ == "__main__":
    main()