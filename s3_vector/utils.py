#!/usr/bin/env python3
"""
Shared Utilities
===============

Common utility functions used across the project to eliminate duplication.
"""

import boto3
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from config import REGION_NAME, get_bucket_name


def get_aws_account_id(region_name: str = REGION_NAME) -> str:
    """Get AWS account ID using STS."""
    sts_client = boto3.client('sts', region_name=region_name)
    return sts_client.get_caller_identity()['Account']


def get_standard_names(account_id: str = None, region_name: str = REGION_NAME) -> Tuple[str, str, str]:
    """Get standard vector bucket, object bucket, and index names."""
    if account_id is None:
        account_id = get_aws_account_id(region_name)
    
    vector_bucket_name = get_bucket_name(account_id)
    object_bucket_name = f"{vector_bucket_name}-object"
    index_name = f"{vector_bucket_name}/automotive-multimodal-index"
    
    return vector_bucket_name, object_bucket_name, index_name


def create_s3_vectors_client(region_name: str = REGION_NAME):
    """Create S3 Vectors client for vector operations."""
    return boto3.client('s3vectors', region_name=region_name)


def load_json_data(file_path: str) -> Dict[str, Any]:
    """Load data from JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON file {file_path}: {e}")


def load_text_data(file_path: str) -> str:
    """Load text data from file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Text file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading text file {file_path}: {e}")


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    os.makedirs(directory_path, exist_ok=True)


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0