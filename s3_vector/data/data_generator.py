"""
Automotive Data Generator
========================

Generates realistic automotive industry data for S3 Vector demonstration.
"""

import random
import time
from typing import List, Dict, Any
from data_models import DealerInfo, OEMData, VehicleSpec


def generate_dealers(count: int = 50) -> List[DealerInfo]:
    """Generate realistic dealer information."""
    regions = ['North', 'South', 'East', 'West', 'Central']
    vehicle_categories = ['sedan', 'suv', 'truck', 'electric', 'luxury', 'compact']
    
    dealer_specialties = [
        'New Vehicle Sales', 'Used Vehicle Sales', 'Service & Maintenance',
        'Parts & Accessories', 'Fleet Sales', 'Luxury Vehicles', 'Electric Vehicles',
        'Commercial Vehicles', 'Performance Tuning', 'Collision Repair'
    ]
    
    cities = [
        'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
        'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
        'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis',
        'Seattle', 'Denver', 'Washington DC', 'Boston', 'Nashville', 'Detroit',
        'Portland', 'Las Vegas', 'Louisville', 'Baltimore', 'Milwaukee', 'Albuquerque'
    ]
    
    dealers = []
    for i in range(count):
        dealer_id = f"dealer_{i+1:03d}"
        region = random.choice(regions)
        city = random.choice(cities)
        
        # Select 2-4 specialties per dealer
        specialties = random.sample(dealer_specialties, random.randint(2, 4))
        
        # Select 1-3 inventory focus areas
        inventory_focus = random.sample(vehicle_categories, random.randint(1, 3))
        
        dealer = DealerInfo(
            dealer_id=dealer_id,
            name=f"{city} Auto Group",
            location=f"{city}, {region} Region",
            region=region,
            specialties=specialties,
            inventory_focus=inventory_focus,
            contact_info={
                'phone': f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'email': f"contact@{city.lower().replace(' ', '')}auto.com"
            }
        )
        dealers.append(dealer)
        
    return dealers


def generate_oems(count: int = 20) -> List[OEMData]:
    """Generate OEM/manufacturer data."""
    regions = ['North', 'South', 'East', 'West', 'Central']
    manufacturers = [
        'Toyota', 'Ford', 'Chevrolet', 'Honda', 'Nissan', 'BMW', 'Mercedes-Benz',
        'Audi', 'Volkswagen', 'Hyundai', 'Kia', 'Mazda', 'Subaru', 'Lexus'
    ]
    
    # Use the same realistic model mapping from generate_vehicles
    manufacturer_models = {
        'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Tacoma', 'Tundra', 'Prius Prime', 'bZ4X'],
        'Ford': ['F-150', 'Explorer', 'Mustang Mach-E', 'Bronco', 'Escape', 'Fusion', 'Expedition'],
        'Chevrolet': ['Silverado', 'Tahoe', 'Malibu', 'Equinox', 'Traverse', 'Bolt EV', 'Colorado'],
        'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Ridgeline', 'HR-V', 'Passport'],
        'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Frontier', 'Leaf', 'Ariya'],
        'BMW': ['3 Series', '5 Series', 'X3', 'X5', 'M3', 'i4', 'iX'],
        'Mercedes-Benz': ['C-Class', 'E-Class', 'GLC', 'GLE', 'AMG GT', 'EQS', 'G-Class'],
        'Audi': ['A3', 'A4', 'Q3', 'Q5', 'R8', 'e-tron', 'TT'],
        'Volkswagen': ['Jetta', 'Passat', 'Tiguan', 'Atlas', 'Golf', 'ID.4'],
        'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Ioniq 5', 'Genesis'],
        'Kia': ['Forte', 'K5', 'Sportage', 'Sorento', 'EV6', 'Telluride'],
        'Mazda': ['Mazda3', 'Mazda6', 'CX-5', 'CX-9', 'CX-30'],
        'Subaru': ['Legacy', 'Impreza', 'Outback', 'Forester', 'Ascent'],
        'Lexus': ['ES', 'IS', 'RX', 'GX', 'LC', 'UX Hybrid']
    }

    oems = []
    for i, manufacturer in enumerate(manufacturers[:count]):
        oem_id = f"oem_{i+1:03d}"
        
        # Get realistic models for this manufacturer
        if manufacturer in manufacturer_models:
            available_models = manufacturer_models[manufacturer]
            # Select 3-6 models from the available realistic models
            model_count = min(random.randint(3, 6), len(available_models))
            models = random.sample(available_models, model_count)
        else:
            # Fallback for any manufacturer not in our mapping
            model_count = random.randint(3, 6)
            models = [f"{manufacturer} Model {chr(65+j)}" for j in range(model_count)]
        
        # Generate specifications
        specifications = {
            'engine_types': random.sample(['V6', 'V8', 'I4', 'Electric', 'Hybrid'], random.randint(2, 4)),
            'fuel_efficiency': f"{random.randint(20, 45)} MPG",
            'safety_rating': f"{random.randint(4, 5)} stars",
            'warranty': f"{random.randint(3, 10)} years"
        }
        
        # Generate availability data
        availability = {
            'production_capacity': f"{random.randint(50000, 500000)} units/year",
            'lead_time': f"{random.randint(2, 12)} weeks",
            'regions': random.sample(regions, random.randint(2, 4))
        }
        
        # Target markets
        target_markets = random.sample(
            ['Family', 'Business', 'Luxury', 'Performance', 'Eco-Friendly', 'Commercial'],
            random.randint(2, 4)
        )
        
        oem = OEMData(
            oem_id=oem_id,
            manufacturer=manufacturer,
            models=models,
            specifications=specifications,
            availability=availability,
            target_markets=target_markets
        )
        oems.append(oem)
        
    return oems


def generate_vehicles(count: int = 100) -> List[VehicleSpec]:
    """Generate vehicle specification data with realistic make/model combinations."""
    
    # Realistic vehicle models by manufacturer
    manufacturer_models = {
        'Toyota': {
            'sedan': ['Camry', 'Corolla', 'Avalon'],
            'suv': ['RAV4', 'Highlander', 'Sequoia', '4Runner'],
            'truck': ['Tacoma', 'Tundra'],
            'electric': ['Prius Prime', 'bZ4X'],
            'compact': ['Yaris', 'Corolla Hatchback']
        },
        'Ford': {
            'sedan': ['Fusion', 'Taurus'],
            'suv': ['Explorer', 'Expedition', 'Escape', 'Bronco'],
            'truck': ['F-150', 'F-250', 'Ranger'],
            'electric': ['Mustang Mach-E', 'F-150 Lightning'],
            'compact': ['Fiesta', 'Focus']
        },
        'Chevrolet': {
            'sedan': ['Malibu', 'Impala'],
            'suv': ['Tahoe', 'Suburban', 'Equinox', 'Traverse'],
            'truck': ['Silverado', 'Colorado'],
            'electric': ['Bolt EV', 'Bolt EUV'],
            'compact': ['Spark', 'Sonic']
        },
        'Honda': {
            'sedan': ['Accord', 'Civic', 'Insight'],
            'suv': ['CR-V', 'Pilot', 'HR-V', 'Passport'],
            'truck': ['Ridgeline'],
            'compact': ['Fit', 'Civic Hatchback']
        },
        'Nissan': {
            'sedan': ['Altima', 'Sentra', 'Maxima'],
            'suv': ['Rogue', 'Pathfinder', 'Armada', 'Murano'],
            'truck': ['Frontier', 'Titan'],
            'electric': ['Leaf', 'Ariya'],
            'compact': ['Versa', 'Kicks']
        },
        'BMW': {
            'sedan': ['3 Series', '5 Series', '7 Series'],
            'suv': ['X3', 'X5', 'X7', 'X1'],
            'luxury': ['M3', 'M5', 'Z4'],
            'electric': ['i3', 'i4', 'iX']
        },
        'Mercedes-Benz': {
            'sedan': ['C-Class', 'E-Class', 'S-Class'],
            'suv': ['GLC', 'GLE', 'GLS', 'GLA'],
            'luxury': ['AMG GT', 'SL-Class', 'G-Class'],
            'electric': ['EQS', 'EQC', 'EQB']
        },
        'Audi': {
            'sedan': ['A3', 'A4', 'A6', 'A8'],
            'suv': ['Q3', 'Q5', 'Q7', 'Q8'],
            'luxury': ['R8', 'TT', 'RS6'],
            'electric': ['e-tron', 'e-tron GT']
        },
        'Volkswagen': {
            'sedan': ['Jetta', 'Passat'],
            'suv': ['Tiguan', 'Atlas', 'Taos'],
            'compact': ['Golf', 'Beetle'],
            'electric': ['ID.4']
        },
        'Hyundai': {
            'sedan': ['Elantra', 'Sonata', 'Genesis'],
            'suv': ['Tucson', 'Santa Fe', 'Palisade'],
            'compact': ['Accent', 'Veloster'],
            'electric': ['Ioniq 5', 'Kona Electric']
        },
        'Kia': {
            'sedan': ['Forte', 'K5', 'Stinger'],
            'suv': ['Sportage', 'Sorento', 'Telluride'],
            'compact': ['Rio', 'Soul'],
            'electric': ['EV6', 'Niro EV']
        },
        'Mazda': {
            'sedan': ['Mazda3', 'Mazda6'],
            'suv': ['CX-3', 'CX-5', 'CX-9', 'CX-30'],
            'compact': ['Mazda2']
        },
        'Subaru': {
            'sedan': ['Legacy', 'Impreza'],
            'suv': ['Outback', 'Forester', 'Ascent'],
            'compact': ['Crosstrek']
        },
        'Lexus': {
            'sedan': ['ES', 'IS', 'LS'],
            'suv': ['RX', 'GX', 'LX', 'NX'],
            'luxury': ['LC', 'RC'],
            'electric': ['UX Hybrid']
        }
    }
    
    vehicle_categories = ['sedan', 'suv', 'truck', 'electric', 'luxury', 'compact']
    price_ranges = ['economy', 'mid-range', 'luxury', 'premium']
    
    features_pool = [
        'GPS Navigation', 'Bluetooth Connectivity', 'Backup Camera', 'Heated Seats',
        'Sunroof', 'Leather Interior', 'All-Wheel Drive', 'Automatic Transmission',
        'Cruise Control', 'Keyless Entry', 'Premium Sound System', 'USB Ports',
        'Wireless Charging', 'Lane Departure Warning', 'Collision Detection',
        'Adaptive Cruise Control', 'Parking Sensors', 'Remote Start'
    ]
    
    demographics = [
        'Young Professionals', 'Families', 'Seniors', 'Students', 'Business Executives',
        'Outdoor Enthusiasts', 'Urban Commuters', 'Suburban Families'
    ]
    
    vehicles = []
    for i in range(count):
        vehicle_id = f"vehicle_{i+1:03d}"
        
        # Select manufacturer and ensure we have models for them
        manufacturer = random.choice(list(manufacturer_models.keys()))
        available_categories = list(manufacturer_models[manufacturer].keys())
        
        # Select category from what's available for this manufacturer
        category = random.choice(available_categories)
        
        # Select model from the appropriate category for this manufacturer
        available_models = manufacturer_models[manufacturer][category]
        model = random.choice(available_models)
        
        year = random.randint(2020, 2024)
        
        # Set price range based on manufacturer and category
        if manufacturer in ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus']:
            price_range = random.choice(['luxury', 'premium'])
        elif category == 'luxury':
            price_range = random.choice(['luxury', 'premium'])
        elif category == 'truck':
            price_range = random.choice(['mid-range', 'luxury'])
        else:
            price_range = random.choice(['economy', 'mid-range'])
        
        # Select 4-8 features per vehicle
        features = random.sample(features_pool, random.randint(4, 8))
        
        target_demographic = random.choice(demographics)
        
        vehicle = VehicleSpec(
            vehicle_id=vehicle_id,
            make=manufacturer,
            model=model,
            year=year,
            category=category,
            features=features,
            price_range=price_range,
            target_demographic=target_demographic
        )
        vehicles.append(vehicle)
        
    return vehicles


def generate_interaction_scenarios(dealers: List[DealerInfo], 
                                 oems: List[OEMData], 
                                 vehicles: List[VehicleSpec],
                                 count: int = 200) -> List[Dict[str, Any]]:
    """Generate dealer-OEM interaction scenarios."""
    interaction_types = [
        'Inventory Request', 'Service Training', 'Marketing Collaboration',
        'Warranty Claim', 'Parts Order', 'Technical Support', 'Sales Inquiry',
        'Promotional Campaign', 'Customer Feedback', 'Quality Issue Report'
    ]
    
    scenarios = []
    for i in range(count):
        scenario_id = f"scenario_{i+1:03d}"
        dealer = random.choice(dealers)
        oem = random.choice(oems)
        vehicle = random.choice(vehicles)
        interaction_type = random.choice(interaction_types)
        
        # Create realistic interaction text
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
        """
        
        scenario = {
            'id': scenario_id,
            'text': interaction_text.strip(),
            'metadata': {
                'dealer_id': dealer.dealer_id,
                'region': dealer.region,
                'vehicle_category': vehicle.category,
                'price_range': vehicle.price_range,
                'specialization': dealer.specialties[0] if dealer.specialties else 'General',
                'manufacturer': oem.manufacturer,
                'interaction_type': interaction_type,
                'year_range': f"{vehicle.year}s"
            },
            'non_filterable_metadata': {
                'original_text': interaction_text.strip(),
                'creation_timestamp': time.time(),
                'source_url': f"https://example.com/interactions/{scenario_id}",
                'description': f"{interaction_type} between {dealer.name} and {oem.manufacturer}"
            }
        }
        scenarios.append(scenario)
        
    return scenarios


def _generate_scenario_description(interaction_type: str, 
                                 dealer: DealerInfo, 
                                 oem: OEMData, 
                                 vehicle: VehicleSpec) -> str:
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


