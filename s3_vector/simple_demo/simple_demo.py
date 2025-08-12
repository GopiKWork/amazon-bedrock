#!/usr/bin/env python3
"""
Simple S3 Vector Demo
====================

This script demonstrates basic AWS S3 Vector capabilities with a simple
automotive industry use case. It creates a small vector index with inline
sample data and demonstrates core functionality.

Features demonstrated:
- Vector bucket and index creation
- Simple vector ingestion with metadata
- Metadata filtering examples
- Basic similarity search

Usage:
    python simple_demo.py

Author: Automotive S3 Vector Project
"""

import boto3
from botocore.exceptions import ClientError

# Project imports
from config import REGION_NAME, VECTOR_DIMENSION, DISTANCE_METRIC, get_bucket_name

# Configuration flag for resource cleanup
CLEAN_UP = False  # Set to True to remove buckets, indexes, and vectors after demo


def run_simple_demo():
    """Execute a simple inline S3 Vector demo."""
    print("AWS S3 Vector Simple Demo")

    index_name = "simple-demo-index"
    
    try:
        s3_vectors_client = boto3.client('s3vectors', region_name=REGION_NAME)
        
        # Get AWS account ID for bucket naming (same bucket as end-to-end demo)
        sts_client = boto3.client('sts', region_name=REGION_NAME)
        account_id = sts_client.get_caller_identity()['Account']
        bucket_name = get_bucket_name(account_id)
        
        # Check if vector bucket already exists using S3 Vectors API
        try:
            s3_vectors_client.get_vector_bucket(vectorBucketName=bucket_name)
            print(f"Using existing vector bucket: {bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] in ['NoSuchBucket', 'NotFoundException']:
                # Create vector bucket
                try:
                    s3_vectors_client.create_vector_bucket(vectorBucketName=bucket_name)
                    print(f"Created new vector bucket: {bucket_name}")
                except ClientError as create_error:
                    if create_error.response['Error']['Code'] == 'ConflictException':
                        print(f"Using existing vector bucket: {bucket_name}")
                    else:
                        raise
            else:
                raise
        
        # Create vector index
        try:
            s3_vectors_client.create_index(
                vectorBucketName=bucket_name,
                indexName=index_name,
                dimension=VECTOR_DIMENSION,
                distanceMetric=DISTANCE_METRIC,
                dataType="float32",
                metadataConfiguration={
                    "nonFilterableMetadataKeys": [
                        "full_description",
                        "contact_details", 
                        "service_history",
                        "detailed_specs"
                    ]
                }
            )
            print(f"Created index: {index_name}")
        except ClientError as index_error:
            if index_error.response['Error']['Code'] == 'ConflictException':
                print(f"Using existing index: {index_name}")
            else:
                raise
        
        # Initialize embedding model (lazy import to speed up startup)
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Use inline sample data
        sample_texts = [
            "Toyota dealer in North region specializing in electric vehicle sales and service",
            "Ford dealership in South region focusing on truck sales and commercial vehicles", 
            "BMW luxury vehicle dealer in West region with premium service offerings",
            "Honda dealer in East region specializing in sedan and compact car sales",
            "Chevrolet dealer in Central region with focus on SUV and family vehicle sales",
            "Mercedes-Benz premium dealer in West region with luxury vehicle expertise"
        ]
        
        sample_metadata = [
            {"region": "North", "manufacturer": "Toyota", "vehicle_category": "electric", "year_established": 2015, "certified": True, "specialties": ["electric", "hybrid"], "full_description": "Toyota dealership specializing in electric and hybrid vehicles with comprehensive service center and charging station facilities.", "contact_details": "123 Electric Ave, North City, NC 12345. Phone: (555) 123-4567", "service_history": "Established 2015, served over 15,000 customers, 98% satisfaction rating", "detailed_specs": "50,000 sq ft showroom, 20 service bays, 10 charging stations"},
            {"region": "South", "manufacturer": "Ford", "vehicle_category": "truck", "year_established": 2010, "certified": True, "specialties": ["truck", "commercial"], "full_description": "Ford dealership focusing on truck and commercial vehicle sales with extensive parts inventory and fleet services.", "contact_details": "456 Truck Blvd, South Town, ST 67890. Phone: (555) 234-5678", "service_history": "Operating since 2010, fleet partner for 200+ businesses, commercial vehicle specialist", "detailed_specs": "75,000 sq ft facility, 30 service bays, parts warehouse: 25,000 sq ft"},
            {"region": "West", "manufacturer": "BMW", "vehicle_category": "luxury", "year_established": 2008, "certified": True, "specialties": ["luxury", "performance"], "full_description": "BMW luxury vehicle dealer offering premium sales and service experience with state-of-the-art facilities.", "contact_details": "789 Luxury Lane, West Hills, WH 13579. Phone: (555) 345-6789", "service_history": "Premium dealer since 2008, BMW Excellence Award winner 2019-2023", "detailed_specs": "40,000 sq ft showroom, 15 service bays, customer lounge with premium amenities"},
            {"region": "East", "manufacturer": "Honda", "vehicle_category": "sedan", "year_established": 2012, "certified": False, "specialties": ["sedan", "compact"], "full_description": "Honda dealer specializing in sedan and compact car sales with focus on fuel efficiency and reliability.", "contact_details": "321 Economy Dr, East Valley, EV 24680. Phone: (555) 456-7890", "service_history": "Family business since 2012, community involvement leader, first-time buyer program", "detailed_specs": "30,000 sq ft dealership, 12 service bays, family waiting area"},
            {"region": "Central", "manufacturer": "Chevrolet", "vehicle_category": "suv", "year_established": 2018, "certified": True, "specialties": ["suv", "family"], "full_description": "Chevrolet dealer with focus on SUV and family vehicle sales, offering comprehensive financing options.", "contact_details": "654 Family Way, Central City, CC 97531. Phone: (555) 567-8901", "service_history": "Established 2018, rapid growth dealer, family vehicle specialist", "detailed_specs": "45,000 sq ft facility, 18 service bays, kids play area"},
            {"region": "West", "manufacturer": "Mercedes-Benz", "vehicle_category": "luxury", "year_established": 2005, "certified": True, "specialties": ["luxury", "premium"], "full_description": "Mercedes-Benz premium dealer offering the ultimate luxury vehicle experience with white-glove service.", "contact_details": "987 Premium Plaza, West Luxury, WL 86420. Phone: (555) 678-9012", "service_history": "Luxury dealer since 2005, Mercedes-Benz Circle of Excellence member", "detailed_specs": "60,000 sq ft flagship showroom, 25 service bays, VIP customer lounge"}
        ]
        
        # Generate embeddings and ingest vectors
        embeddings = model.encode(sample_texts)
        
        vectors_to_ingest = []
        for i, (text, metadata, embedding) in enumerate(zip(sample_texts, sample_metadata, embeddings)):
            vectors_to_ingest.append({
                "key": f"demo_vector_{i+1}",
                "data": {"float32": embedding.tolist()},
                "metadata": metadata
            })
        
        s3_vectors_client.put_vectors(
            vectorBucketName=bucket_name,
            indexName=index_name,
            vectors=vectors_to_ingest
        )
        print(f"Ingested {len(vectors_to_ingest)} vectors")
        
        # Search examples
        
        # Example 1: Simple equality filter
        print("\n1. Simple equality filter")
        query_text = "Looking for luxury vehicle dealers"
        print(f"Query: {query_text}")
        print("Filter: region = 'West'")
        
        query_embedding = model.encode([query_text])[0]
        search_results = s3_vectors_client.query_vectors(
            vectorBucketName=bucket_name,
            indexName=index_name,
            queryVector={"float32": query_embedding.tolist()},
            topK=3,
            filter={"region": "West"},
            returnDistance=True,
            returnMetadata=True
        )

        print("Raw results:")
        print(search_results)
        print("\n\n")
        print("Results:")
        if 'vectors' in search_results:
            for i, result in enumerate(search_results['vectors'], 1):
                similarity = 1.0 - result.get('distance', 0.0)
                metadata = result.get('metadata', {})
                print(f"  {i}. {metadata.get('manufacturer', 'N/A')} - {metadata.get('region', 'N/A')} (Score: {similarity:.4f})")
                print(f"     Non-filterable: {metadata.get('full_description', 'N/A')[:80]}...")
        
        # Example 2: Numeric comparison ($gte)
        print("\n2. Numeric comparison filter")
        query_text = "Established dealerships with experience"
        print(f"Query: {query_text}")
        print("Filter: year_established >= 2010")
        
        query_embedding = model.encode([query_text])[0]
        search_results = s3_vectors_client.query_vectors(
            vectorBucketName=bucket_name,
            indexName=index_name,
            queryVector={"float32": query_embedding.tolist()},
            topK=4,
            filter={"year_established": {"$gte": 2010}},
            returnDistance=True,
            returnMetadata=True
        )
        
        print("Results:")
        if 'vectors' in search_results:
            for i, result in enumerate(search_results['vectors'], 1):
                similarity = 1.0 - result.get('distance', 0.0)
                metadata = result.get('metadata', {})
                print(f"  {i}. {metadata.get('manufacturer', 'N/A')} - Est. {metadata.get('year_established', 'N/A')} (Score: {similarity:.4f})")
                print(f"     Contact: {metadata.get('contact_details', 'N/A')[:60]}...")
        
        # Example 3: Boolean filter
        print("\n3. Boolean filter")
        query_text = "Certified automotive dealers"
        print(f"Query: {query_text}")
        print("Filter: certified = true")
        
        query_embedding = model.encode([query_text])[0]
        search_results = s3_vectors_client.query_vectors(
            vectorBucketName=bucket_name,
            indexName=index_name,
            queryVector={"float32": query_embedding.tolist()},
            topK=3,
            filter={"certified": True},
            returnDistance=True,
            returnMetadata=True
        )
        
        print("Results:")
        if 'vectors' in search_results:
            for i, result in enumerate(search_results['vectors'], 1):
                similarity = 1.0 - result.get('distance', 0.0)
                metadata = result.get('metadata', {})
                print(f"  {i}. {metadata.get('manufacturer', 'N/A')} - Certified: {metadata.get('certified', 'N/A')} (Score: {similarity:.4f})")
                print(f"     Service History: {metadata.get('service_history', 'N/A')[:70]}...")
        
        # Cleanup based on CLEAN_UP flag
        if CLEAN_UP:
            s3_vectors_client.delete_index(vectorBucketName=bucket_name, indexName=index_name)
            s3_vectors_client.delete_vector_bucket(vectorBucketName=bucket_name)
            print("Resources cleaned up")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Main function to run the simple S3 Vector demo."""
    success = run_simple_demo()
    return success


if __name__ == "__main__":
    # Run the simple demo
    success = main()
    
    if success:
        exit(0)
    else:
        exit(1)