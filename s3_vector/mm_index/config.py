#!/usr/bin/env python3
"""
MM Index Configuration
=====================

Configuration constants for the MM Index package.
"""

# AWS Configuration
DEFAULT_REGION = 'us-west-2'

# Indexing Strategies (single source of truth)
SUPPORTED_INDEXING_STRATEGIES = [
    'text',
    'hybrid', 
    'full_embedding',
    'generate_text',
    'summarize'
]

