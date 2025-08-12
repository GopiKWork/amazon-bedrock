#!/usr/bin/env python3
"""
Synthetic Data Generator for S3 Vector Showcase
===============================================

This script generates comprehensive synthetic data for automotive dealer-OEM interactions
with both filterable and non-filterable metadata, saving it to a JSON file for use by
the S3 Vector showcase demos.

Usage:
    python synthetic_data_generator.py

Output:
    synthetic_automotive_data.json - Contains 100 OEM/Dealer interaction scenarios
"""

import json
import time
import random
import argparse
from typing import List, Dict, Any
from data_models import DealerInfo, OEMData, VehicleSpec
import data_generator


def generate_comprehensive_metadata(dealer: DealerInfo, oem: OEMData, vehicle: VehicleSpec, 
                                  interaction_type: str, scenario_id: str) -> Dict[str, Any]:
    """Generate comprehensive metadata with both filterable and non-filterable fields."""
    
    # Filterable metadata (6 keys to stay within AWS S3 Vector Store limit with 4 non-filterable)
    filterable_metadata = {
        "region": dealer.region,
        "manufacturer": oem.manufacturer,
        "vehicle_category": vehicle.category,
        "year_established": random.randint(2005, 2023),
        "certified": random.choice([True, False]),
        "specialties": random.sample(dealer.specialties, min(2, len(dealer.specialties)))
    }
    
    # Generate detailed contact information
    contact_details = f"{dealer.name}, {dealer.location}. Phone: {dealer.contact_info['phone']}. Email: {dealer.contact_info['email']}. Hours: Mon-Sat {random.randint(7,9)}AM-{random.randint(7,9)}PM, Sun {random.randint(10,12)}AM-{random.randint(5,7)}PM"
    
    # Generate service history
    years_operating = 2024 - filterable_metadata["year_established"]
    customers_served = random.randint(5000, 50000)
    satisfaction_rate = random.randint(85, 99)
    
    service_history = f"Operating since {filterable_metadata['year_established']}, served over {customers_served:,} customers, {satisfaction_rate}% satisfaction rating"
    
    if interaction_type == "Service Training":
        service_history += f", certified {oem.manufacturer} service partner since {random.randint(2015, 2023)}"
    elif interaction_type == "Marketing Collaboration":
        service_history += f", marketing partnership with {oem.manufacturer} for {random.randint(2, 8)} years"
    elif interaction_type == "Warranty Claim":
        service_history += f", processes {random.randint(50, 500)} warranty claims annually"
    
    # Generate detailed specifications
    showroom_size = random.randint(25000, 80000)
    service_bays = random.randint(10, 35)
    technicians = random.randint(8, 40)
    sales_staff = random.randint(5, 25)
    
    detailed_specs = f"{showroom_size:,} sq ft facility, {service_bays} service bays, certified technicians: {technicians}, sales staff: {sales_staff}"
    
    if vehicle.category == "electric":
        charging_stations = random.randint(5, 20)
        detailed_specs += f", {charging_stations} charging stations"
    elif vehicle.category == "truck":
        parts_warehouse = random.randint(15000, 30000)
        detailed_specs += f", parts warehouse: {parts_warehouse:,} sq ft"
    elif vehicle.category == "luxury":
        detailed_specs += f", VIP customer lounge, concierge services"
    
    # Generate full description
    full_description = f"{dealer.name} is a {oem.manufacturer} dealership in the {dealer.region} region specializing in {', '.join(dealer.specialties)}. "
    
    if interaction_type == "Inventory Request":
        full_description += f"Currently requesting {vehicle.category} inventory to meet growing demand in the {dealer.region} market."
    elif interaction_type == "Service Training":
        full_description += f"Participating in {oem.manufacturer} technical training programs for {vehicle.model} maintenance and repair procedures."
    elif interaction_type == "Marketing Collaboration":
        full_description += f"Collaborating with {oem.manufacturer} on promotional campaigns targeting {vehicle.target_demographic} customers."
    elif interaction_type == "Warranty Claim":
        full_description += f"Processing warranty claims for {vehicle.year} {vehicle.make} {vehicle.model} vehicles with comprehensive customer support."
    elif interaction_type == "Parts Order":
        full_description += f"Maintaining extensive parts inventory for {oem.manufacturer} vehicles with rapid order fulfillment capabilities."
    else:
        full_description += f"Engaged in {interaction_type.lower()} activities with {oem.manufacturer} to enhance customer experience."
    
    full_description += f" The dealership focuses on {vehicle.price_range} price range vehicles and serves the {vehicle.target_demographic} demographic."
    
    # Non-filterable metadata (4 keys)
    non_filterable_metadata = {
        "full_description": full_description,
        "contact_details": contact_details,
        "service_history": service_history,
        "detailed_specs": detailed_specs
    }
    
    # Combine all metadata
    return {**filterable_metadata, **non_filterable_metadata}


def generate_synthetic_data(count: int = 100) -> List[Dict[str, Any]]:
    """Generate comprehensive synthetic data for S3 Vector showcase."""
    print(f"🔄 Generating {count} synthetic automotive interaction scenarios...")
    
    # Generate base data using existing generators
    dealers = data_generator.generate_dealers(50)
    oems = data_generator.generate_oems(20)
    vehicles = data_generator.generate_vehicles(100)
    
    interaction_types = [
        'Inventory Request', 'Service Training', 'Marketing Collaboration',
        'Warranty Claim', 'Parts Order', 'Technical Support', 'Sales Inquiry',
        'Promotional Campaign', 'Customer Feedback', 'Quality Issue Report'
    ]
    
    synthetic_data = []
    
    for i in range(count):
        scenario_id = f"scenario_{i+1:03d}"
        dealer = random.choice(dealers)
        oem = random.choice(oems)
        vehicle = random.choice(vehicles)
        interaction_type = random.choice(interaction_types)
        
        # Create interaction text
        interaction_text = f"""
        Interaction Type: {interaction_type}
        
        Dealer: {dealer.name} ({dealer.location})
        Dealer Specialties: {', '.join(dealer.specialties)}
        Dealer Focus: {', '.join(dealer.inventory_focus)}
        
        OEM: {oem.manufacturer}
        Available Models: {', '.join(oem.models[:3])}
        Target Markets: {', '.join(oem.target_markets)}
        
        Vehicle Context: {vehicle.year} {vehicle.make} {vehicle.model}
        Category: {vehicle.category}
        Features: {', '.join(vehicle.features[:5])}
        Price Range: {vehicle.price_range}
        
        Scenario: {_generate_scenario_description(interaction_type, dealer, oem, vehicle)}
        """.strip()
        
        # Generate comprehensive metadata
        metadata = generate_comprehensive_metadata(dealer, oem, vehicle, interaction_type, scenario_id)
        
        scenario = {
            'id': scenario_id,
            'text': interaction_text,
            'metadata': metadata,
            'interaction_type': interaction_type,
            'dealer_info': {
                'name': dealer.name,
                'location': dealer.location,
                'region': dealer.region,
                'specialties': dealer.specialties
            },
            'oem_info': {
                'manufacturer': oem.manufacturer,
                'models': oem.models[:3]
            },
            'vehicle_info': {
                'year': vehicle.year,
                'make': vehicle.make,
                'model': vehicle.model,
                'category': vehicle.category,
                'price_range': vehicle.price_range
            }
        }
        
        synthetic_data.append(scenario)
        
        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/{count} scenarios")
    
    print(f"Generated {len(synthetic_data)} synthetic scenarios")
    return synthetic_data


def _generate_scenario_description(interaction_type: str, dealer: DealerInfo, 
                                 oem: OEMData, vehicle: VehicleSpec) -> str:
    """Generate realistic scenario descriptions."""
    descriptions = {
        'Inventory Request': f"{dealer.name} requests {vehicle.category} inventory from {oem.manufacturer} for {dealer.region} region market demand.",
        'Service Training': f"{oem.manufacturer} provides technical training to {dealer.name} service team on {vehicle.model} maintenance procedures.",
        'Marketing Collaboration': f"Joint marketing campaign between {dealer.name} and {oem.manufacturer} targeting {vehicle.target_demographic} demographic.",
        'Warranty Claim': f"{dealer.name} processes warranty claim for {vehicle.year} {vehicle.make} {vehicle.model} customer issue.",
        'Parts Order': f"Emergency parts order from {dealer.name} to {oem.manufacturer} for {vehicle.category} vehicle repairs.",
        'Technical Support': f"{oem.manufacturer} technical support assists {dealer.name} with {vehicle.model} diagnostic procedures.",
        'Sales Inquiry': f"Customer inquiry at {dealer.name} about {oem.manufacturer} {vehicle.category} options in {vehicle.price_range} range.",
        'Promotional Campaign': f"Seasonal promotion planning between {dealer.name} and {oem.manufacturer} for {vehicle.category} vehicles.",
        'Customer Feedback': f"Customer satisfaction feedback from {dealer.name} to {oem.manufacturer} regarding {vehicle.model} performance.",
        'Quality Issue Report': f"{dealer.name} reports quality concerns to {oem.manufacturer} about {vehicle.year} {vehicle.model} production batch."
    }
    
    return descriptions.get(interaction_type, f"General interaction between {dealer.name} and {oem.manufacturer}.")


def save_synthetic_data(data: List[Dict[str, Any]], filename: str = "dealer_oem_interaction.json") -> None:
    """Save synthetic data to JSON file."""
    print(f"💾 Saving synthetic data to {filename}...")
    
    # Add metadata about the generated data
    output_data = {
        "metadata": {
            "generated_at": time.time(),
            "generated_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_scenarios": len(data),
            "description": "Synthetic automotive dealer-OEM interaction data for S3 Vector showcase",
            "filterable_metadata_keys": ["region", "manufacturer", "vehicle_category", "year_established", "certified", "specialties"],
            "non_filterable_metadata_keys": ["full_description", "contact_details", "service_history", "detailed_specs"]
        },
        "scenarios": data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(data)} scenarios to {filename}")
    print(f"File size: {len(json.dumps(output_data)) / 1024:.1f} KB")


def load_synthetic_data(filename: str = "dealer_oem_interaction.json") -> List[Dict[str, Any]]:
    """Load synthetic data from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scenarios = data.get('scenarios', [])
        metadata = data.get('metadata', {})
        
        print(f"📂 Loaded {len(scenarios)} scenarios from {filename}")
        print(f"📅 Generated: {metadata.get('generated_date', 'Unknown')}")
        
        return scenarios
    
    except FileNotFoundError:
        print(f"File {filename} not found. Generate data first using: python synthetic_data_generator.py")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {filename}: {e}")
        return []


def main():
    """Main function to generate and save synthetic data."""
    parser = argparse.ArgumentParser(description='Generate dealer-OEM interaction data')
    parser.add_argument('--count', type=int, default=50, 
                       help='Number of OEM interactions to generate (default: 50)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Count must be at least 1")
        return False
    
    print("🚗 Synthetic Automotive Data Generator")
    print("=" * 50)
    print(f"Generating {args.count} synthetic data scenarios for S3 Vector showcase...")
    print("=" * 50)
    
    try:
        # Generate synthetic data
        synthetic_data = generate_synthetic_data(args.count)
        
        # Save to JSON file
        save_synthetic_data(synthetic_data)
        
        # Verify the saved data
        print("\n🔍 Verifying saved data...")
        loaded_data = load_synthetic_data()
        
        if loaded_data:
            print("Data verification successful!")
            
            # Show sample metadata structure
            sample = loaded_data[0]
            print(f"\n📋 Sample metadata structure:")
            print(f"  - Filterable keys: {list(k for k in sample['metadata'].keys() if k not in ['full_description', 'contact_details', 'service_history', 'detailed_specs'])}")
            print(f"  - Non-filterable keys: ['full_description', 'contact_details', 'service_history', 'detailed_specs']")
            print(f"  - Total metadata keys: {len(sample['metadata'])}")
            
            print(f"\nReady for use in S3 Vector showcase demos!")
        else:
            print("Data verification failed!")
            
    except Exception as e:
        print(f"Error generating synthetic data: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\nSynthetic data generation completed successfully!")
    else:
        print("\nSynthetic data generation failed!")