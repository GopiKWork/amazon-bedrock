#!/usr/bin/env python3
"""
Global Configuration Constants for Automotive S3 Vector Project
==============================================================

This module contains ONLY global constants used across multiple implementations.
Agent-specific configurations are in their respective directories:
- strands-bedrock-local/config.py
- strands-bedrock-agent-core/config.py

Author: Automotive S3 Vector Project
"""

# AWS Configuration (Global)
REGION_NAME = 'us-west-2'

# Model Configuration (Global)
NOVA_PRO_MODEL_ID = 'us.amazon.nova-pro-v1:0'  # Cross-regional inference profile
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# S3 Vector Index Names (Global - used by both implementations)
DEALER_INDEX_NAME = 'automotive-interactions-index'
EXPERT_INDEX_NAME = 'automotive-expert-knowledge-index'

# Vector Configuration (Global)
VECTOR_DIMENSION = 384
DISTANCE_METRIC = 'cosine'
VECTOR_DATA_TYPE = 'float32'

# Search Configuration (Global)
DEFAULT_MAX_RESULTS = 5
DEFAULT_BATCH_SIZE = 25

# Metadata Configuration (Global)
MAX_METADATA_TAGS = 10  # AWS S3 Vector Store limit for total metadata tags

# Bucket Naming (Global)
def get_bucket_name(account_id: str) -> str:
    """Generate the standard bucket name for the given AWS account ID."""
    return f"automotive-vectors-showcase-{account_id}"

# Multi-modal configuration (Global - for data generation)
CLIP_MODEL_NAME = "sentence-transformers/clip-ViT-B-32"
USE_TEXT_BASED_EMBEDDING = True  # Set to False for real image processing
MULTIMODAL_TEXT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MULTIMODAL_INDEX_NAME = "automotive-damage-multimodal-index"

# Non-filterable metadata keys (Global)
NON_FILTERABLE_METADATA_KEYS = [
    'full_description',
    'contact_details',
    'service_history',
    'detailed_specs',
    'technical_details',
    'diagnostic_steps',
    'parts_list',
    'labor_time',
    'special_tools',
    'original_text'
]

# Valid filter values (Global)
VALID_REGIONS = ['North', 'South', 'East', 'West', 'Central']
VALID_VEHICLE_CATEGORIES = ['sedan', 'suv', 'truck', 'luxury', 'electric', 'hybrid', 'compact']

# Service Types (Global)
SUPPORTED_SERVICE_TYPES = [
    'oil_change', 'brake_service', 'tire_rotation', 'general_inspection',
    'engine_repair', 'transmission_service', 'electrical_diagnosis',
    'air_conditioning', 'battery_replacement', 'tune_up'
]

# Appointment Configuration (Global)
APPOINTMENT_SLOTS = ['09:00', '10:30', '13:00', '14:30', '16:00']
APPOINTMENT_DURATION_MINUTES = 90
ADVANCE_BOOKING_DAYS = 30

# VIN Configuration (Global)
VIN_LENGTH = 17
VIN_PATTERN = r'^[A-HJ-NPR-Z0-9]{17}$'  # Excludes I, O, Q

# Inventory Configuration (Global)
DEFAULT_DELIVERY_DAYS = 2
MAX_INVENTORY_CHECK_DEALERS = 5

# Directory Paths (Global - for data generation)
IMAGES_DIR = 'multimodal_patterns/images'
DATA_DIR = 'data'

# Data File Paths (Global - for data generation only)
EXPERT_KNOWLEDGE_FILE = 'data/automotive_expert_knowledge.json'
DEALER_ESCALATION_FILE = 'data/dealer_issue_escalation.txt'
DEALER_INTERACTION_FILE = 'data/dealer_oem_interaction.json'
MULTIMODAL_DAMAGE_DATA_FILE = 'data/multimodal_damage_data.json'