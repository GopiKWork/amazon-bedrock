#!/usr/bin/env python3
"""
Cleanup Utility
===============

Utility script to clean up AWS resources created during testing and demos.
This script can delete vectors from vector stores, objects from object stores,
and remove S3 buckets safely.
"""

import boto3
import sys
import argparse
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError

from config import REGION_NAME, get_bucket_name
from utils import get_aws_account_id
import s3_vector_ops


class AWSResourceCleanup:
    """AWS resource cleanup utility."""
    
    def __init__(self, region_name: str = REGION_NAME, dry_run: bool = False):
        """
        Initialize cleanup utility.
        
        Args:
            region_name: AWS region name
            dry_run: If True, only show what would be deleted without actually deleting
        """
        self.region_name = region_name
        self.dry_run = dry_run
        
        try:
            self.s3_client = boto3.client('s3', region_name=region_name)
            self.s3_vectors_client = boto3.client('s3vectors', region_name=region_name)
            self.sts_client = boto3.client('sts', region_name=region_name)
            
            # Get account ID for bucket naming
            self.account_id = self.sts_client.get_caller_identity()['Account']
            self.vector_bucket_name = get_bucket_name(self.account_id)
            self.object_bucket_name = f"{self.vector_bucket_name}-object"
            
            print(f"Cleanup utility initialized for account {self.account_id}")
            print(f"Region: {self.region_name}")
            print(f"Vector bucket: {self.vector_bucket_name}")
            print(f"Object bucket: {self.object_bucket_name}")
            if dry_run:
                print("DRY RUN MODE: No resources will actually be deleted")
            
        except NoCredentialsError:
            print("ERROR: AWS credentials not found. Please configure AWS credentials.")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to initialize AWS clients: {e}")
            sys.exit(1)
    
    def list_vector_indexes(self) -> List[str]:
        """List all vector indexes in the vector bucket."""
        try:
            # Check if bucket exists first
            try:
                self.s3_vectors_client.get_vector_bucket(vectorBucketName=self.vector_bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    print(f"Vector bucket {self.vector_bucket_name} does not exist")
                    return []
                else:
                    raise
            
            # Use the s3_vector_ops function to list indexes
            index_names = s3_vector_ops.get_index_names(self.s3_vectors_client, self.vector_bucket_name)
            print(f"Found {len(index_names)} vector indexes: {index_names}")
            return index_names
            
        except ClientError as e:
            print(f"Error accessing vector bucket: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing vector indexes: {e}")
            return []
    
    def delete_vectors_from_index(self, index_name: str) -> bool:
        """Delete all vectors from a specific index."""
        try:
            print(f"Deleting vectors from index: {index_name}")
            
            if self.dry_run:
                print(f"  [DRY RUN] Would delete all vectors from {index_name}")
                return True
            
            # Use the s3_vector_ops function to delete the index
            return s3_vector_ops.delete_index(self.s3_vectors_client, self.vector_bucket_name, index_name)
                
        except Exception as e:
            print(f"Error deleting vectors from {index_name}: {e}")
            return False
    
    def delete_all_vector_indexes(self, index_names: Optional[List[str]] = None) -> bool:
        """Delete all vector indexes in the bucket."""
        if index_names:
            # Use provided index names
            indexes = index_names
            print(f"Using provided index names: {indexes}")
        else:
            # Try to discover indexes
            indexes = self.list_vector_indexes()
            
        if not indexes:
            print("No vector indexes to delete")
            return True
        
        success_count = 0
        for index_name in indexes:
            if self.delete_vectors_from_index(index_name):
                success_count += 1
        
        print(f"Successfully deleted {success_count}/{len(indexes)} vector indexes")
        return success_count == len(indexes)
    
    def list_s3_objects(self, bucket_name: str) -> List[Dict[str, Any]]:
        """List all objects in an S3 bucket."""
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name)
            objects = response.get('Contents', [])
            print(f"Found {len(objects)} objects in bucket {bucket_name}")
            return objects
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"Bucket {bucket_name} does not exist")
                return []
            else:
                print(f"Error listing objects in {bucket_name}: {e}")
                return []
    
    def delete_s3_objects(self, bucket_name: str) -> bool:
        """Delete all objects from an S3 bucket."""
        objects = self.list_s3_objects(bucket_name)
        if not objects:
            print(f"No objects to delete in bucket {bucket_name}")
            return True
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete {len(objects)} objects from {bucket_name}")
            return True
        
        try:
            # Delete objects in batches
            delete_keys = [{'Key': obj['Key']} for obj in objects]
            
            # S3 delete_objects can handle up to 1000 objects at once
            batch_size = 1000
            success_count = 0
            
            for i in range(0, len(delete_keys), batch_size):
                batch = delete_keys[i:i + batch_size]
                response = self.s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch}
                )
                
                deleted = response.get('Deleted', [])
                errors = response.get('Errors', [])
                
                success_count += len(deleted)
                
                if errors:
                    for error in errors:
                        print(f"  Error deleting {error['Key']}: {error['Message']}")
            
            print(f"Successfully deleted {success_count}/{len(objects)} objects from {bucket_name}")
            return success_count == len(objects)
            
        except Exception as e:
            print(f"Error deleting objects from {bucket_name}: {e}")
            return False
    
    def delete_vector_bucket(self) -> bool:
        """Delete the S3 Vector Store bucket."""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would delete vector bucket {self.vector_bucket_name}")
                return True
            
            # Check if vector bucket exists using S3 Vectors API
            try:
                self.s3_vectors_client.get_vector_bucket(vectorBucketName=self.vector_bucket_name)
                print(f"Vector bucket {self.vector_bucket_name} exists")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    print(f"Vector bucket {self.vector_bucket_name} does not exist")
                    return True
                else:
                    raise
            
            # Delete the vector bucket using S3 Vectors API
            self.s3_vectors_client.delete_vector_bucket(vectorBucketName=self.vector_bucket_name)
            print(f"Successfully deleted vector bucket: {self.vector_bucket_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting vector bucket {self.vector_bucket_name}: {e}")
            return False
    
    def delete_s3_bucket(self, bucket_name: str) -> bool:
        """Delete a regular S3 bucket (must be empty)."""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would delete S3 bucket {bucket_name}")
                return True
            
            # Check if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                print(f"S3 bucket {bucket_name} exists")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    print(f"S3 bucket {bucket_name} does not exist")
                    return True
                else:
                    raise
            
            # Ensure bucket is empty
            objects = self.list_s3_objects(bucket_name)
            if objects:
                print(f"ERROR: Bucket {bucket_name} is not empty. Delete objects first.")
                return False
            
            # Delete the bucket
            self.s3_client.delete_bucket(Bucket=bucket_name)
            print(f"Successfully deleted S3 bucket: {bucket_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting S3 bucket {bucket_name}: {e}")
            return False
    
    def cleanup_all(self) -> bool:
        """Perform complete cleanup of all resources."""
        print("\n" + "=" * 60)
        print("Starting complete AWS resource cleanup")
        print("=" * 60)
        
        success = True
        
        # Step 1: Delete all vector indexes
        print("\n1. Deleting vector indexes...")
        if not self.delete_all_vector_indexes():
            success = False
        
        # Step 2: Delete objects from object bucket
        print("\n2. Deleting objects from object bucket...")
        if not self.delete_s3_objects(self.object_bucket_name):
            success = False
        
        # Step 3: Delete object bucket
        print("\n3. Deleting object bucket...")
        if not self.delete_s3_bucket(self.object_bucket_name):
            success = False
        
        # Step 4: Delete vector bucket (should be empty after deleting indexes)
        print("\n4. Deleting vector bucket...")
        if not self.delete_vector_bucket():
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("Cleanup completed successfully!")
        else:
            print("Cleanup completed with some errors. Check the output above.")
        print("=" * 60)
        
        return success


def main():
    """Main function to run cleanup utility."""
    parser = argparse.ArgumentParser(description='AWS Resource Cleanup Utility')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--region', default=REGION_NAME,
                       help=f'AWS region (default: {REGION_NAME})')
    parser.add_argument('--vectors-only', action='store_true',
                       help='Only delete vector indexes, not S3 buckets')
    parser.add_argument('--objects-only', action='store_true',
                       help='Only delete S3 objects, not buckets or vectors')
    parser.add_argument('--index-names', nargs='+',
                       help='Specific vector index names to delete (space-separated)')
    parser.add_argument('--list-only', action='store_true',
                       help='Only list vector indexes without deleting anything')
    
    args = parser.parse_args()
    
    # Initialize cleanup utility
    cleanup = AWSResourceCleanup(region_name=args.region, dry_run=args.dry_run)
    
    try:
        if args.list_only:
            print("Listing vector indexes...")
            indexes = cleanup.list_vector_indexes()
            if indexes:
                print(f"\nFound {len(indexes)} vector indexes:")
                for i, index_name in enumerate(indexes, 1):
                    print(f"  {i}. {index_name}")
            else:
                print("No vector indexes found.")
            success = True
        elif args.vectors_only:
            print("Cleaning up vector indexes only...")
            success = cleanup.delete_all_vector_indexes(args.index_names)
        elif args.objects_only:
            print("Cleaning up S3 objects only...")
            success = (cleanup.delete_s3_objects(cleanup.object_bucket_name) and
                      cleanup.delete_s3_objects(cleanup.vector_bucket_name))
        else:
            # Full cleanup
            success = cleanup.cleanup_all()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\nCleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()