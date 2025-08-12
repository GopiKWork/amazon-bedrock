#!/usr/bin/env python3
"""
Automotive Dealer Database Generator
===================================

Generates a normalized dealer database with realistic automotive dealer information.

Usage:
    python generate_dealer_database.py [--count N]

Options:
    --count N    Number of dealers to generate (default: 50)
"""

import json
import random
import argparse
from datetime import datetime
from typing import Dict, List, Any


class DealerDatabaseGenerator:
    def __init__(self):
        # Base data for realistic generation
        self.regions = ["North", "South", "East", "West", "Central"]
        
        # Expanded cities by region with multiple states
        self.cities = {
            "North": [
                # Michigan
                "Detroit, MI", "Grand Rapids, MI", "Ann Arbor, MI", "Lansing, MI",
                # Illinois  
                "Chicago, IL", "Springfield, IL", "Rockford, IL", "Peoria, IL",
                # Minnesota
                "Minneapolis, MN", "St. Paul, MN", "Duluth, MN", "Rochester, MN",
                # Wisconsin
                "Milwaukee, WI", "Madison, WI", "Green Bay, WI", "Kenosha, WI",
                # Ohio
                "Cleveland, OH", "Columbus, OH", "Cincinnati, OH", "Toledo, OH",
                # Indiana
                "Indianapolis, IN", "Fort Wayne, IN", "Evansville, IN", "South Bend, IN",
                # Iowa
                "Des Moines, IA", "Cedar Rapids, IA", "Davenport, IA", "Sioux City, IA"
            ],
            "South": [
                # Georgia
                "Atlanta, GA", "Savannah, GA", "Augusta, GA", "Columbus, GA",
                # Florida
                "Miami, FL", "Orlando, FL", "Tampa, FL", "Jacksonville, FL", "Tallahassee, FL",
                # Texas
                "Houston, TX", "Dallas, TX", "Austin, TX", "San Antonio, TX", "Fort Worth, TX",
                # Tennessee
                "Nashville, TN", "Memphis, TN", "Knoxville, TN", "Chattanooga, TN",
                # North Carolina
                "Charlotte, NC", "Raleigh, NC", "Greensboro, NC", "Durham, NC",
                # South Carolina
                "Charleston, SC", "Columbia, SC", "Greenville, SC", "Rock Hill, SC",
                # Alabama
                "Birmingham, AL", "Montgomery, AL", "Mobile, AL", "Huntsville, AL",
                # Louisiana
                "New Orleans, LA", "Baton Rouge, LA", "Shreveport, LA", "Lafayette, LA",
                # Mississippi
                "Jackson, MS", "Gulfport, MS", "Southaven, MS", "Hattiesburg, MS",
                # Arkansas
                "Little Rock, AR", "Fort Smith, AR", "Fayetteville, AR", "Springdale, AR"
            ],
            "East": [
                # New York
                "New York, NY", "Buffalo, NY", "Rochester, NY", "Albany, NY", "Syracuse, NY",
                # Massachusetts
                "Boston, MA", "Worcester, MA", "Springfield, MA", "Cambridge, MA",
                # Pennsylvania
                "Philadelphia, PA", "Pittsburgh, PA", "Allentown, PA", "Erie, PA",
                # New Jersey
                "Newark, NJ", "Jersey City, NJ", "Paterson, NJ", "Elizabeth, NJ",
                # Maryland
                "Baltimore, MD", "Annapolis, MD", "Frederick, MD", "Rockville, MD",
                # Virginia
                "Virginia Beach, VA", "Norfolk, VA", "Richmond, VA", "Newport News, VA",
                # Connecticut
                "Hartford, CT", "New Haven, CT", "Bridgeport, CT", "Stamford, CT",
                # Washington DC
                "Washington, DC",
                # Delaware
                "Wilmington, DE", "Dover, DE", "Newark, DE",
                # Rhode Island
                "Providence, RI", "Warwick, RI", "Cranston, RI",
                # Vermont
                "Burlington, VT", "South Burlington, VT", "Rutland, VT",
                # New Hampshire
                "Manchester, NH", "Nashua, NH", "Concord, NH",
                # Maine
                "Portland, ME", "Lewiston, ME", "Bangor, ME"
            ],
            "West": [
                # California
                "Los Angeles, CA", "San Francisco, CA", "San Diego, CA", "Sacramento, CA", "San Jose, CA",
                # Washington
                "Seattle, WA", "Spokane, WA", "Tacoma, WA", "Vancouver, WA",
                # Oregon
                "Portland, OR", "Eugene, OR", "Salem, OR", "Gresham, OR",
                # Arizona
                "Phoenix, AZ", "Tucson, AZ", "Mesa, AZ", "Chandler, AZ",
                # Nevada
                "Las Vegas, NV", "Reno, NV", "Henderson, NV", "North Las Vegas, NV",
                # Utah
                "Salt Lake City, UT", "Provo, UT", "West Valley City, UT", "West Jordan, UT",
                # Colorado (Western part)
                "Grand Junction, CO", "Durango, CO", "Aspen, CO", "Vail, CO",
                # Idaho
                "Boise, ID", "Nampa, ID", "Meridian, ID", "Idaho Falls, ID",
                # Montana
                "Billings, MT", "Missoula, MT", "Great Falls, MT", "Bozeman, MT",
                # Wyoming
                "Cheyenne, WY", "Casper, WY", "Laramie, WY", "Gillette, WY",
                # Alaska
                "Anchorage, AK", "Fairbanks, AK", "Juneau, AK",
                # Hawaii
                "Honolulu, HI", "Pearl City, HI", "Hilo, HI"
            ],
            "Central": [
                # Colorado (Central/Eastern part)
                "Denver, CO", "Colorado Springs, CO", "Aurora, CO", "Lakewood, CO",
                # Missouri
                "Kansas City, MO", "St. Louis, MO", "Springfield, MO", "Columbia, MO",
                # Kansas
                "Wichita, KS", "Overland Park, KS", "Kansas City, KS", "Topeka, KS",
                # Oklahoma
                "Oklahoma City, OK", "Tulsa, OK", "Norman, OK", "Broken Arrow, OK",
                # Nebraska
                "Omaha, NE", "Lincoln, NE", "Bellevue, NE", "Grand Island, NE",
                # New Mexico
                "Albuquerque, NM", "Las Cruces, NM", "Santa Fe, NM", "Rio Rancho, NM",
                # North Dakota
                "Fargo, ND", "Bismarck, ND", "Grand Forks, ND", "Minot, ND",
                # South Dakota
                "Sioux Falls, SD", "Rapid City, SD", "Aberdeen, SD", "Brookings, SD"
            ]
        }
        
        self.dealer_names = [
            "Premium Auto Service", "Honda Service Center", "BMW Authorized Dealer", 
            "Toyota Service Plus", "Ford Service Center", "Chevrolet Dealership",
            "Nissan Service Hub", "Mercedes-Benz Center", "Audi Service Station",
            "Hyundai Service Point", "Kia Motors Service", "Subaru Service Center",
            "Mazda Service Hub", "Volkswagen Service", "Lexus Service Center",
            "Acura Service Point", "Infiniti Service Hub", "Cadillac Service Center",
            "Buick Service Station", "GMC Service Hub", "Jeep Service Center",
            "Ram Service Point", "Chrysler Service Hub", "Dodge Service Center",
            "Lincoln Service Station", "Volvo Service Center", "Jaguar Service Hub",
            "Land Rover Service", "Porsche Service Center", "Tesla Service Hub",
            "Genesis Service Point", "Alfa Romeo Service", "Maserati Service Center",
            "Bentley Service Hub", "Rolls-Royce Service", "McLaren Service Point",
            "Ferrari Service Center", "Lamborghini Service", "Aston Martin Service",
            "Lotus Service Hub", "Mini Service Center", "Smart Service Point",
            "Fiat Service Hub", "Mitsubishi Service", "Suzuki Service Center",
            "Isuzu Service Point", "Scion Service Hub", "Saturn Service Center",
            "Pontiac Service Point", "Oldsmobile Service", "Mercury Service Hub"
        ]
        
        self.manufacturers = [
            ["Honda", "Toyota", "Nissan"], ["BMW", "Mercedes", "Audi"], 
            ["Ford", "Chevrolet", "GMC"], ["Hyundai", "Kia", "Genesis"],
            ["Subaru", "Mazda", "Volkswagen"], ["Lexus", "Acura", "Infiniti"],
            ["Cadillac", "Buick", "Lincoln"], ["Jeep", "Ram", "Chrysler"],
            ["Volvo", "Jaguar", "Land Rover"], ["Porsche", "Tesla", "Mini"]
        ]
        
        self.services = [
            "oil_change", "brake_service", "tire_rotation", "general_inspection",
            "engine_repair", "transmission_service", "electrical_diagnosis",
            "air_conditioning", "battery_replacement", "tune_up"
        ]
        
        self.specialties = [
            "Luxury Vehicles", "Performance Tuning", "Service & Maintenance",
            "Collision Repair", "Paint & Body", "Electrical Systems",
            "Hybrid & Electric", "Diesel Engines", "Classic Cars",
            "Commercial Vehicles", "Fleet Services", "Warranty Work"
        ]
        
        self.appointment_slots = ["09:00", "10:30", "13:00", "14:30", "16:00"]
        
        self.business_hours = [
            "Mon-Fri 8AM-6PM, Sat 8AM-4PM",
            "Mon-Fri 7AM-7PM, Sat 8AM-5PM", 
            "Mon-Fri 8AM-5PM, Sat 9AM-3PM",
            "Mon-Sat 8AM-6PM, Sun 10AM-4PM",
            "Mon-Fri 7AM-6PM, Sat 8AM-4PM"
        ]

    def generate_dealer_id(self, index: int) -> str:
        """Generate a dealer ID."""
        return f"DEALER-{index:03d}"

    def generate_phone_number(self) -> str:
        """Generate a realistic phone number."""
        area_codes = ["555", "312", "404", "213", "617", "202", "713", "214", "206", "303"]
        area_code = random.choice(area_codes)
        exchange = random.randint(100, 999)
        number = random.randint(1000, 9999)
        return f"({area_code}) {exchange}-{number}"

    def generate_email(self, dealer_name: str) -> str:
        """Generate an email address based on dealer name."""
        # Clean the dealer name for email
        clean_name = dealer_name.lower().replace(" ", "").replace("-", "")
        domains = ["gmail.com", "dealership.com", "autoservice.com", "service.com"]
        domain = random.choice(domains)
        return f"contact@{clean_name[:10]}.{domain}"

    def extract_state_from_city(self, city: str) -> str:
        """Extract state abbreviation from city string."""
        if ", " in city:
            return city.split(", ")[1]
        return "Unknown"
    
    def extract_city_name(self, city: str) -> str:
        """Extract city name from city string."""
        if ", " in city:
            return city.split(", ")[0]
        return city

    def generate_address(self, city: str) -> str:
        """Generate a realistic address."""
        street_numbers = [str(random.randint(100, 9999)) for _ in range(1)]
        street_names = [
            "Auto Lane", "Service Blvd", "Dealer Drive", "Mechanic Way", 
            "Repair Road", "Motor Ave", "Vehicle St", "Garage Blvd",
            "Workshop Way", "Maintenance Dr", "Parts Place", "Service Center Dr"
        ]
        street_number = random.choice(street_numbers)
        street_name = random.choice(street_names)
        return f"{street_number} {street_name}, {city}"

    def generate_dealer(self, index: int) -> Dict[str, Any]:
        """Generate a single dealer record."""
        dealer_id = self.generate_dealer_id(index)
        region = random.choice(self.regions)
        city = random.choice(self.cities[region])
        dealer_name = random.choice(self.dealer_names)
        
        # Ensure unique dealer names by adding region suffix if needed
        if random.random() < 0.3:  # 30% chance to add region suffix
            dealer_name = f"{dealer_name} - {region}"
        
        manufacturer_group = random.choice(self.manufacturers)
        selected_services = random.sample(self.services, random.randint(4, 8))
        selected_specialties = random.sample(self.specialties, random.randint(2, 4))
        
        dealer = {
            "name": dealer_name,
            "region": region,
            "location": city,
            "state": self.extract_state_from_city(city),
            "city": self.extract_city_name(city),
            "manufacturer_specialties": manufacturer_group,
            "services": selected_services,
            "certified": random.choice([True, True, True, False]),  # 75% certified
            "contact": {
                "phone": self.generate_phone_number(),
                "address": self.generate_address(city),
                "hours": random.choice(self.business_hours),
                "email": self.generate_email(dealer_name)
            },
            "appointment_slots": self.appointment_slots.copy(),
            "year_established": random.randint(1995, 2020),
            "specialties": selected_specialties
        }
        
        return dealer

    def generate_database(self, count: int = 50) -> Dict[str, Any]:
        """Generate the complete dealer database."""
        print(f"Generating {count} dealer records...")
        
        database = {}
        
        for i in range(1, count + 1):
            dealer_id = self.generate_dealer_id(i)
            dealer = self.generate_dealer(i)
            database[dealer_id] = dealer
            
            if i % 10 == 0:
                print(f"Generated {i}/{count} dealers...")
        
        return database

    def save_database(self, database: Dict[str, Any], filename: str = "normalized_dealer_database.json"):
        """Save the database to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(database)} dealers to {filename}")
        
        # Print summary statistics
        regions = {}
        certified_count = 0
        
        for dealer in database.values():
            region = dealer['region']
            regions[region] = regions.get(region, 0) + 1
            if dealer['certified']:
                certified_count += 1
        
        print(f"📊 Summary:")
        print(f"   Total dealers: {len(database)}")
        print(f"   Certified dealers: {certified_count} ({certified_count/len(database)*100:.1f}%)")
        print(f"   Regional distribution:")
        for region, count in sorted(regions.items()):
            print(f"     {region}: {count} dealers")


def main():
    parser = argparse.ArgumentParser(description='Generate automotive dealer database')
    parser.add_argument('--count', type=int, default=50, 
                       help='Number of dealers to generate (default: 50)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Count must be at least 1")
        return
    
    generator = DealerDatabaseGenerator()
    database = generator.generate_database(args.count)
    generator.save_database(database)


if __name__ == "__main__":
    main()