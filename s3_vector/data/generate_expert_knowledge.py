#!/usr/bin/env python3
"""
Automotive Expert Knowledge Generator
====================================

Generates automotive expert knowledge base with technical service bulletins,
warranty claims, diagnostic procedures, and other technical information.

Usage:
    python generate_expert_knowledge.py [--count N]

Options:
    --count N    Number of knowledge entries to generate (default: 50)
"""

import json
import random
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any


class ExpertKnowledgeGenerator:
    def __init__(self):
        self.manufacturers = [
            "Honda", "Toyota", "Ford", "BMW", "Mercedes", "Chevrolet", 
            "Nissan", "Hyundai", "Volkswagen", "Audi", "Lexus", "Acura"
        ]
        
        self.vehicle_categories = [
            "sedan", "suv", "truck", "luxury", "electric", "hybrid", "compact"
        ]
        
        self.knowledge_types = [
            "Technical Service Bulletin",
            "Warranty Claim",
            "Diagnostic Procedure", 
            "Recall Information",
            "Parts Information",
            "Dealer Certification"
        ]
        
        self.severity_levels = ["low", "medium", "high", "critical"]
        
        # Knowledge templates by type
        self.knowledge_templates = {
            "Technical Service Bulletin": {
                "issues": [
                    "Intermittent Starting Issues",
                    "Engine Oil Leak",
                    "Brake Noise During Operation",
                    "Transmission Shifting Problems",
                    "Air Conditioning Not Cooling",
                    "Electrical System Malfunction",
                    "Suspension Noise Over Bumps",
                    "Fuel Economy Degradation",
                    "Dashboard Warning Lights",
                    "Power Window Failure"
                ],
                "symptoms": [
                    "Engine cranks but fails to start intermittently",
                    "Visible oil spots under vehicle after parking",
                    "Squealing or grinding noise when braking",
                    "Harsh or delayed gear shifts",
                    "Warm air blowing from vents",
                    "Intermittent electrical component failures",
                    "Clunking noise when driving over bumps",
                    "Decreased miles per gallon",
                    "Multiple warning lights illuminated",
                    "Window does not respond to switch"
                ],
                "root_causes": [
                    "Faulty starter relay in under-hood fuse box",
                    "Degraded oil pan gasket allowing seepage",
                    "Worn brake pads requiring replacement",
                    "Contaminated transmission fluid affecting operation",
                    "Low refrigerant levels in AC system",
                    "Corroded wiring harness connections",
                    "Worn suspension bushings and mounts",
                    "Clogged air filter restricting airflow",
                    "Faulty sensors triggering false alerts",
                    "Broken window regulator mechanism"
                ]
            },
            "Warranty Claim": {
                "components": [
                    "Engine Block", "Transmission", "Brake System", "Electrical System",
                    "Suspension Components", "Air Conditioning", "Fuel System", "Exhaust System"
                ],
                "claim_types": [
                    "Manufacturing Defect", "Premature Wear", "Component Failure",
                    "Design Flaw", "Material Defect", "Assembly Error"
                ]
            },
            "Diagnostic Procedure": {
                "systems": [
                    "Engine Management", "Brake System", "Transmission", "Electrical",
                    "Suspension", "HVAC", "Fuel System", "Exhaust"
                ],
                "tools": [
                    "OBD-II Scanner", "Multimeter", "Pressure Gauge", "Oscilloscope",
                    "Brake Fluid Tester", "AC Manifold Gauge", "Compression Tester"
                ]
            }
        }
        
        self.parts_database = {
            "Honda": ["39794-T2A-A01", "15400-PLM-A02", "45022-S9A-A00", "17220-R1A-A00"],
            "Toyota": ["90919-02240", "04152-YZZA1", "47750-06040", "17801-21050"],
            "Ford": ["3F2Z-12029-AA", "FL-820-S", "7L1Z-2C026-A", "6L2Z-9601-AA"],
            "BMW": ["11427837997", "83212365950", "34116858652", "13717572779"],
            "Mercedes": ["A0009898301", "A2711800009", "A0004209651", "A2711840025"]
        }

    def generate_knowledge_id(self, knowledge_type: str, index: int) -> str:
        """Generate a knowledge entry ID."""
        type_codes = {
            "Technical Service Bulletin": "tsb",
            "Warranty Claim": "warranty", 
            "Diagnostic Procedure": "diag",
            "Recall Information": "recall",
            "Parts Information": "parts",
            "Dealer Certification": "cert"
        }
        code = type_codes.get(knowledge_type, "know")
        return f"{code}_{index:03d}"

    def generate_tsb_content(self, manufacturer: str, vehicle_category: str) -> Dict[str, Any]:
        """Generate Technical Service Bulletin content."""
        templates = self.knowledge_templates["Technical Service Bulletin"]
        issue = random.choice(templates["issues"])
        symptom = random.choice(templates["symptoms"])
        root_cause = random.choice(templates["root_causes"])
        
        # Generate model and year range
        models = self.get_models_for_manufacturer(manufacturer, vehicle_category)
        model = random.choice(models)
        start_year = random.randint(2018, 2022)
        end_year = random.randint(start_year, 2024)
        
        # Generate part information
        parts = self.parts_database.get(manufacturer, ["PART-001", "PART-002"])
        part_number = random.choice(parts)
        part_price = round(random.uniform(15.99, 299.99), 2)
        
        labor_hours = round(random.uniform(0.5, 4.0), 1)
        
        text = f"""Technical Service Bulletin: {manufacturer} {model} {start_year}-{end_year} {issue}

Symptoms: {symptom}. Customer reports multiple occurrences of this condition.

Root Cause: {root_cause}. This condition is more common in vehicles with higher mileage or in certain environmental conditions.

Solution: Replace affected component (Part #{part_number}) and perform system inspection. Follow proper installation procedures as outlined in service manual.

Affected Models: {start_year}-{end_year} {manufacturer} {model} (all trim levels)
Warranty Extension: Covered under extended warranty up to {random.randint(60, 100)},000 miles
Labor Time: {labor_hours} hours
Difficulty: {random.choice(['Basic', 'Intermediate', 'Advanced'])}"""

        return {
            "text": text,
            "technical_details": f"{root_cause}. Common in {random.choice(['humid climates', 'cold weather', 'high-mileage vehicles', 'stop-and-go traffic'])}. Affects {start_year}-{end_year} {model} models regardless of engine type.",
            "diagnostic_steps": f"1. Verify symptom reproduction 2. Check system voltage/pressure 3. Test component with appropriate tools 4. Inspect related components 5. Replace part and test",
            "parts_list": f"{part_number.split('-')[0]} Component #{part_number} (${part_price}), Related fluids/cleaners (${round(random.uniform(8.50, 25.99), 2)})",
            "labor_time": f"{int(labor_hours * 60)} minutes",
            "special_tools": random.choice(["Multimeter, specialized puller tool", "Pressure gauge, diagnostic scanner", "Torque wrench, alignment tools", "OBD-II scanner, oscilloscope"])
        }

    def generate_warranty_content(self, manufacturer: str, vehicle_category: str) -> Dict[str, Any]:
        """Generate Warranty Claim content."""
        templates = self.knowledge_templates["Warranty Claim"]
        component = random.choice(templates["components"])
        claim_type = random.choice(templates["claim_types"])
        
        models = self.get_models_for_manufacturer(manufacturer, vehicle_category)
        model = random.choice(models)
        
        claim_amount = round(random.uniform(500, 5000), 2)
        mileage = random.randint(15000, 80000)
        
        text = f"""Warranty Claim: {manufacturer} {model} {component} {claim_type}

Claim Details: Customer reports {component.lower()} failure at {mileage:,} miles. Initial inspection confirms {claim_type.lower()} affecting component performance.

Coverage: This issue is covered under manufacturer warranty for vehicles within warranty period. Extended coverage may apply for known defects.

Resolution: Replace {component.lower()} with updated part. Perform system calibration and road test to verify repair.

Claim Amount: ${claim_amount:,}
Approval Status: Pre-approved for certified technicians
Documentation Required: Photos, diagnostic codes, customer statement"""

        return {
            "text": text,
            "technical_details": f"{claim_type} in {component.lower()}. Typically occurs between {mileage-5000:,} and {mileage+10000:,} miles. Manufacturing batch issue identified.",
            "diagnostic_steps": "1. Document customer complaint 2. Perform visual inspection 3. Run diagnostic tests 4. Compare to known failure patterns 5. Submit warranty claim",
            "parts_list": f"Replacement {component} (Warranty covered), Installation hardware (${round(random.uniform(25, 75), 2)})",
            "labor_time": f"{random.randint(60, 240)} minutes",
            "special_tools": "Warranty claim documentation, digital camera, diagnostic equipment"
        }

    def generate_diagnostic_content(self, manufacturer: str, vehicle_category: str) -> Dict[str, Any]:
        """Generate Diagnostic Procedure content."""
        templates = self.knowledge_templates["Diagnostic Procedure"]
        system = random.choice(templates["systems"])
        tool = random.choice(templates["tools"])
        
        models = self.get_models_for_manufacturer(manufacturer, vehicle_category)
        model = random.choice(models)
        
        text = f"""Diagnostic Procedure: {manufacturer} {model} {system} Diagnosis

Procedure Overview: Comprehensive diagnostic approach for {system.lower()} related concerns. Follow systematic troubleshooting methodology.

Required Tools: {tool}, basic hand tools, service manual

Step-by-Step Process:
1. Initial system inspection and visual check
2. Connect diagnostic equipment and retrieve codes
3. Perform functional tests of system components
4. Compare readings to specification values
5. Isolate faulty component through process of elimination
6. Verify repair with post-repair testing

Expected Results: System should operate within manufacturer specifications after repair completion."""

        return {
            "text": text,
            "technical_details": f"{system} diagnostic procedure for {manufacturer} vehicles. Covers common failure modes and testing protocols. Updated for current model year specifications.",
            "diagnostic_steps": "1. Visual inspection 2. Code retrieval 3. Component testing 4. Specification comparison 5. Fault isolation 6. Repair verification",
            "parts_list": f"Diagnostic consumables (${round(random.uniform(15, 45), 2)}), Replacement fuses/relays as needed",
            "labor_time": f"{random.randint(30, 120)} minutes",
            "special_tools": f"{tool}, service manual, safety equipment"
        }

    def get_models_for_manufacturer(self, manufacturer: str, category: str) -> List[str]:
        """Get realistic model names for manufacturer and category."""
        model_map = {
            "Honda": {"sedan": ["Accord", "Civic"], "suv": ["CR-V", "Pilot"], "compact": ["Fit", "HR-V"]},
            "Toyota": {"sedan": ["Camry", "Corolla"], "suv": ["RAV4", "Highlander"], "hybrid": ["Prius", "Camry Hybrid"]},
            "Ford": {"truck": ["F-150", "Ranger"], "suv": ["Explorer", "Escape"], "sedan": ["Fusion", "Focus"]},
            "BMW": {"luxury": ["3 Series", "5 Series"], "suv": ["X3", "X5"], "sedan": ["3 Series", "7 Series"]},
            "Mercedes": {"luxury": ["C-Class", "E-Class"], "suv": ["GLC", "GLE"], "sedan": ["C-Class", "S-Class"]}
        }
        
        manufacturer_models = model_map.get(manufacturer, {})
        category_models = manufacturer_models.get(category, [f"{manufacturer} Model"])
        
        if not category_models:
            category_models = [f"{manufacturer} {category.title()}"]
            
        return category_models

    def generate_knowledge_entry(self, index: int) -> Dict[str, Any]:
        """Generate a single knowledge entry."""
        knowledge_type = random.choice(self.knowledge_types)
        manufacturer = random.choice(self.manufacturers)
        vehicle_category = random.choice(self.vehicle_categories)
        severity_level = random.choice(self.severity_levels)
        
        knowledge_id = self.generate_knowledge_id(knowledge_type, index)
        
        # Generate content based on type
        if knowledge_type == "Technical Service Bulletin":
            content_data = self.generate_tsb_content(manufacturer, vehicle_category)
        elif knowledge_type == "Warranty Claim":
            content_data = self.generate_warranty_content(manufacturer, vehicle_category)
        elif knowledge_type == "Diagnostic Procedure":
            content_data = self.generate_diagnostic_content(manufacturer, vehicle_category)
        else:
            # Generic content for other types
            content_data = {
                "text": f"{knowledge_type}: {manufacturer} {vehicle_category} information and procedures.",
                "technical_details": f"Technical information for {manufacturer} {vehicle_category} vehicles.",
                "diagnostic_steps": "1. Assessment 2. Analysis 3. Action 4. Verification",
                "parts_list": "Various components as needed",
                "labor_time": f"{random.randint(30, 180)} minutes",
                "special_tools": "Standard diagnostic equipment"
            }
        
        # Create metadata
        metadata = {
            "knowledge_type": knowledge_type,
            "manufacturer": manufacturer,
            "vehicle_category": vehicle_category,
            "severity_level": severity_level,
            "warranty_covered": random.choice([True, False]),
            "certification_required": random.choice([True, False]),
            "technical_details": content_data["technical_details"],
            "diagnostic_steps": content_data["diagnostic_steps"],
            "parts_list": content_data["parts_list"],
            "labor_time": content_data["labor_time"],
            "special_tools": content_data["special_tools"]
        }
        
        return {
            "id": knowledge_id,
            "text": content_data["text"],
            "metadata": metadata
        }

    def generate_knowledge_base(self, count: int = 50) -> Dict[str, Any]:
        """Generate the complete expert knowledge base."""
        print(f"Generating {count} expert knowledge entries...")
        
        knowledge_entries = []
        
        for i in range(1, count + 1):
            entry = self.generate_knowledge_entry(i)
            knowledge_entries.append(entry)
            
            if i % 10 == 0:
                print(f"Generated {i}/{count} knowledge entries...")
        
        # Create metadata
        metadata = {
            "generated_at": time.time(),
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_entries": count,
            "description": "Automotive expert knowledge base for dealer-OEM technical advisory",
            "data_types": [
                "Technical Service Bulletins",
                "Warranty Claims", 
                "Parts Inventory",
                "Diagnostic Procedures",
                "Recall Information",
                "Dealer Certifications"
            ],
            "filterable_metadata_keys": [
                "knowledge_type",
                "manufacturer", 
                "vehicle_category",
                "severity_level",
                "warranty_covered",
                "certification_required"
            ],
            "non_filterable_metadata_keys": [
                "technical_details",
                "diagnostic_steps",
                "parts_list", 
                "labor_time",
                "special_tools"
            ]
        }
        
        return {
            "metadata": metadata,
            "knowledge_entries": knowledge_entries
        }

    def save_knowledge_base(self, knowledge_base: Dict[str, Any], filename: str = "automotive_expert_knowledge.json"):
        """Save the knowledge base to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        
        entries_count = len(knowledge_base["knowledge_entries"])
        print(f"✅ Saved {entries_count} knowledge entries to {filename}")
        
        # Print summary statistics
        knowledge_types = {}
        manufacturers = {}
        severity_levels = {}
        
        for entry in knowledge_base["knowledge_entries"]:
            metadata = entry["metadata"]
            
            k_type = metadata["knowledge_type"]
            manufacturer = metadata["manufacturer"]
            severity = metadata["severity_level"]
            
            knowledge_types[k_type] = knowledge_types.get(k_type, 0) + 1
            manufacturers[manufacturer] = manufacturers.get(manufacturer, 0) + 1
            severity_levels[severity] = severity_levels.get(severity, 0) + 1
        
        print(f"📊 Summary:")
        print(f"   Total entries: {entries_count}")
        print(f"   Knowledge type distribution:")
        for k_type, count in sorted(knowledge_types.items()):
            print(f"     {k_type}: {count} entries")
        print(f"   Manufacturer distribution:")
        for manufacturer, count in sorted(manufacturers.items()):
            print(f"     {manufacturer}: {count} entries")
        print(f"   Severity distribution:")
        for severity, count in sorted(severity_levels.items()):
            print(f"     {severity}: {count} entries")


def main():
    parser = argparse.ArgumentParser(description='Generate automotive expert knowledge base')
    parser.add_argument('--count', type=int, default=50, 
                       help='Number of knowledge entries to generate (default: 50)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Count must be at least 1")
        return
    
    generator = ExpertKnowledgeGenerator()
    knowledge_base = generator.generate_knowledge_base(args.count)
    generator.save_knowledge_base(knowledge_base)


if __name__ == "__main__":
    main()