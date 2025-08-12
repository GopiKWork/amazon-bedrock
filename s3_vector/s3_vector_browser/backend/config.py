"""
Configuration settings for S3 Vector Browser
"""

import os
from typing import Dict, Any

# AWS Configuration
DEFAULT_REGION = 'us-west-2'
AWS_REGION = os.getenv('AWS_REGION', DEFAULT_REGION)

# UI Configuration
APP_TITLE = "S3 Vector Index Browser"
APP_ICON = "🗂️"
PAGE_LAYOUT = "wide"

# Table Configuration
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# Styling Configuration
PRIMARY_COLOR = "#1f77b4"
SUCCESS_COLOR = "#28a745"
WARNING_COLOR = "#ffc107"
ERROR_COLOR = "#dc3545"
BACKGROUND_COLOR = "#f8f9fa"

# Performance Configuration
CACHE_TTL = 300  # 5 minutes
MAX_ITEMS_PER_PAGE = 100

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    'aws_connection': "Unable to connect to AWS S3 Vectors service. Please check your credentials.",
    'bucket_not_found': "The specified vector bucket was not found.",
    'index_not_found': "The specified vector index was not found.",
    'permission_denied': "You don't have permission to access this resource.",
    'service_unavailable': "S3 Vectors service is temporarily unavailable. Please try again later.",
    'unknown_error': "An unexpected error occurred. Please try again."
}