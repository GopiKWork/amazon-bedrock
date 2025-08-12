#!/usr/bin/env python3
"""
S3 Multimodal Automotive Demo
============================

Demonstration of multimodal indexing patterns using automotive damage assessment data.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mm_index import MMIngestor, ImageResizer
from config import (
    REGION_NAME, 
    MULTIMODAL_DAMAGE_DATA_FILE, 
    DEALER_ESCALATION_FILE, 
    IMAGES_DIR
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_standard_names, load_json_data, load_text_data


def load_damage_data():
    """Load the multimodal damage data from JSON file."""
    data = load_json_data(MULTIMODAL_DAMAGE_DATA_FILE)
    return data['damage_cases']


def load_dealer_escalation_text():
    """Load the dealer escalation text for summarize pattern."""
    return load_text_data(DEALER_ESCALATION_FILE)


def get_image_path(damage_id):
    """Get the path to the damage image."""
    return os.path.join(IMAGES_DIR, f"{damage_id}.jpeg")


def create_mm_ingestor():
    """Create MMIngestor with image resizing for automotive photos."""
    vector_bucket_name, object_bucket_name, index_name = get_standard_names()
    
    mm_ingestor = MMIngestor(
        index_name=index_name,
        region_name=REGION_NAME
    )
    
    # Configure image resizer for automotive damage photos
    mm_ingestor.preprocessor_chain.clear()
    image_resizer = ImageResizer(
        target_size=(512, 384),
        preserve_aspect_ratio=True
    )
    mm_ingestor.add_preprocessor(image_resizer)
    
    print(f"MMIngestor created with {len(mm_ingestor.pattern_engine.list_patterns())} patterns: {mm_ingestor.pattern_engine.list_patterns()}")
    
    return mm_ingestor


def print_search_results(results: List[Dict[str, Any]]):
    """Print search results in a clean format."""
    print(f"Found {len(results)} results:")
    
    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        pattern = metadata.get('pattern', 'unknown')
        score = result['similarity_score']
        
        print(f"  {i}. Score: {score:.3f} | Pattern: {pattern}")
        
        if 'vehicle_make' in metadata and 'vehicle_model' in metadata:
            vehicle = f"{metadata.get('vehicle_year', '')} {metadata['vehicle_make']} {metadata['vehicle_model']}"
            damage_type = metadata.get('damage_type', '').replace('_', ' ').title()
            cost = metadata.get('estimated_cost', 'N/A')
            print(f"     Vehicle: {vehicle} | Damage: {damage_type} | Cost: ${cost}")
        
        if 'document_type' in metadata:
            print(f"     Document: {metadata['document_type']}")
        
        print()


def ingest_dealer_escalation():
    """Ingest dealer escalation text using summarize pattern."""
    print("\n=== Ingesting Dealer Escalation Document ===")
    
    mm_ingestor = create_mm_ingestor()
    escalation_text = load_dealer_escalation_text()
    
    print(f"Loaded dealer escalation text: {len(escalation_text):,} characters")
    
    # Use summarize pattern for long document
    doc_id = mm_ingestor.ingest(
        content={'text': escalation_text},
        metadata={
            'document_type': 'dealer_escalation',
            'category': 'customer_service',
            'dealer': 'Lakeside Honda',
            'customer': 'Mrs. Janet T.',
            'vehicle': '2021 Honda Civic EX',
            'case_id': '2024-0934'
        },
        pattern="summarize"
    )
    
    print(f"Ingested dealer escalation document: {doc_id}")
    return doc_id


def ingest_damage_cases():
    """Ingest automotive damage cases using different patterns."""
    print("\n=== Ingesting Automotive Damage Cases ===")
    
    mm_ingestor = create_mm_ingestor()
    damage_cases = load_damage_data()
    
    print(f"Loaded {len(damage_cases)} damage cases")
    
    # Use different patterns for each case
    patterns_to_use = ["text", "hybrid", "full_embedding", "describe", "summarize", "text"]
    ingested_docs = []
    
    for i, case in enumerate(damage_cases):
        pattern = patterns_to_use[i]
        image_path = get_image_path(case['id'])
        
        # Extend text for summarize pattern (needs 1000+ characters)
        if pattern == "summarize":
            case_text = case['damage_text'] + " " + """
            Additional detailed assessment: The damage assessment was conducted by certified technicians 
            following industry standard procedures. The inspection revealed multiple areas of concern 
            that require immediate attention. The structural integrity of the vehicle has been evaluated 
            and documented according to insurance guidelines. Repair estimates include both parts and 
            labor costs based on current market rates. The vehicle owner has been notified of all 
            findings and recommended repair procedures. All documentation has been submitted to the 
            insurance carrier for processing and approval. The repair facility has been selected 
            based on certification and availability. Timeline for repairs depends on parts availability 
            and shop scheduling. Customer satisfaction and safety remain our top priorities throughout 
            the entire repair process. Quality assurance checks will be performed at each stage.
            The assessment includes detailed photographic documentation of all damage areas, measurements
            of affected components, and evaluation of potential safety implications. All work will be
            performed according to manufacturer specifications and industry best practices.
            """
        else:
            case_text = case['damage_text']
        
        vehicle = f"{case['metadata']['vehicle_year']} {case['metadata']['vehicle_make']} {case['metadata']['vehicle_model']}"
        
        metadata = {
            'damage_id': case['id'],
            'vehicle_make': case['metadata']['vehicle_make'],
            'vehicle_model': case['metadata']['vehicle_model'],
            'vehicle_year': case['metadata']['vehicle_year'],
            'damage_type': case['metadata']['damage_type'],
            'severity': case['metadata']['severity'],
            'estimated_cost': case['metadata']['estimated_cost']
        }
        
        try:
            if pattern in ["hybrid", "full_embedding", "describe"]:
                doc_id = mm_ingestor.ingest(content={'text': case_text, 'image': image_path}, metadata=metadata, pattern=pattern)
            else:  # text and summarize patterns
                doc_id = mm_ingestor.ingest(content={'text': case_text}, metadata=metadata, pattern=pattern)
            
            ingested_docs.append(doc_id)
            print(f"Ingested {case['id']}: {vehicle} using {pattern} pattern -> {doc_id}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"Successfully ingested {len(ingested_docs)} damage cases")
    return ingested_docs


def search_examples():
    """Demonstrate search functionality."""
    print("\n=== Search Examples ===")
    
    mm_ingestor = create_mm_ingestor()
    
    # Search for Honda damage
    print("Searching for 'Honda bumper damage'...")
    results = mm_ingestor.search(query={'text': "Honda bumper damage"}, top_k=3)
    print_search_results(results)
    
    # Search for dealer escalation
    print("Searching for 'dashboard warning lights'...")
    results = mm_ingestor.search(query={'text': "dashboard warning lights"}, top_k=3)
    print_search_results(results)
    
    # Search with metadata filter
    print("Searching for collision damage...")
    results = mm_ingestor.search(
        query={'text': "collision damage"},
        metadata_filters={'damage_type': 'collision_damage'},
        top_k=3
    )
    print_search_results(results)


def main():
    """Run the automotive multimodal demo."""
    print("S3 Multimodal Automotive Demo")
    print("=" * 40)
    print("Demonstrating multimodal indexing with automotive damage data")
    
    try:
        # Step 1: Ingest dealer escalation document
        dealer_doc_id = ingest_dealer_escalation()
        
        # Step 2: Ingest automotive damage cases
        damage_docs = ingest_damage_cases()
        
        # Step 3: Demonstrate search functionality
        search_examples()
        
        print("\n" + "=" * 40)
        print("Demo completed successfully!")
        print(f"Ingested: 1 dealer document + {len(damage_docs)} damage cases")
        print("Patterns used: text, hybrid, full_embedding, describe, summarize")
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure AWS credentials are configured")
        print("2. Verify data files exist in the data/ directory")
        print("3. Check S3 permissions")


if __name__ == "__main__":
    main()