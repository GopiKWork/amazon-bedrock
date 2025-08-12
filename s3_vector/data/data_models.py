"""
Data Models for S3 Vector Showcase
==================================

Simple data structures for automotive industry use case.
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class DealerInfo:
    """Automotive dealer information."""
    dealer_id: str
    name: str
    location: str
    region: str
    specialties: List[str]
    inventory_focus: List[str]
    contact_info: Dict[str, str]
    
    def to_text(self) -> str:
        """Convert to searchable text."""
        return f"""
        Dealer: {self.name}
        Location: {self.location}, {self.region}
        Specialties: {', '.join(self.specialties)}
        Inventory Focus: {', '.join(self.inventory_focus)}
        Contact: {self.contact_info.get('phone', 'N/A')}
        """


@dataclass
class OEMData:
    """Original Equipment Manufacturer data."""
    oem_id: str
    manufacturer: str
    models: List[str]
    specifications: Dict[str, Any]
    availability: Dict[str, Any]
    target_markets: List[str]
    
    def to_text(self) -> str:
        """Convert to searchable text."""
        return f"""
        Manufacturer: {self.manufacturer}
        Models: {', '.join(self.models)}
        Target Markets: {', '.join(self.target_markets)}
        Specifications: {json.dumps(self.specifications, indent=2)}
        Availability: {json.dumps(self.availability, indent=2)}
        """


@dataclass
class VehicleSpec:
    """Vehicle specifications."""
    vehicle_id: str
    make: str
    model: str
    year: int
    category: str
    features: List[str]
    price_range: str
    target_demographic: str
    
    def to_text(self) -> str:
        """Convert to searchable text."""
        return f"""
        Vehicle: {self.year} {self.make} {self.model}
        Category: {self.category}
        Features: {', '.join(self.features)}
        Price Range: {self.price_range}
        Target Demographic: {self.target_demographic}
        """


@dataclass
class VectorData:
    """Vector with metadata and content."""
    id: str
    vector: List[float]
    metadata: Dict[str, Any]
    text_content: str
    
    def validate(self) -> bool:
        """Validate vector data structure."""
        if not self.id or not isinstance(self.id, str):
            return False
        if not self.vector or not isinstance(self.vector, list):
            return False
        if not all(isinstance(x, (int, float)) for x in self.vector):
            return False
        if not isinstance(self.metadata, dict):
            return False
        return True