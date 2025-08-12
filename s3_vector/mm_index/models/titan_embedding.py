"""
Titan Embedding Model Implementation
==================================

Concrete implementation using Amazon Bedrock Titan Embed Image model.
"""

import json
import base64
import io
import logging
from typing import List, Optional
from PIL import Image as PILImage
import boto3

from ..base_classes import BaseEmbeddingModel
from ..utils.image_processing import ImageProcessor
from ..validation import create_bedrock_formatter

logger = logging.getLogger(__name__)


class TitanEmbeddingModel(BaseEmbeddingModel):
    """Titan multimodal embedding model implementation."""
    
    def __init__(self, region_name: str = 'us-west-2', model_id: str = None, embedding_dimension: int = 384):
        """
        Initialize Titan embedding model.
        
        Args:
            region_name: AWS region for Bedrock service
            model_id: Model ID to use (optional, defaults to amazon.titan-embed-image-v1)
            embedding_dimension: Target embedding dimension (256, 384, or 1024)
        """
        self.region_name = region_name
        self.model_id = model_id or 'amazon.titan-embed-image-v1'
        self.embedding_dimension = embedding_dimension
        
        # Initialize API formatter for proper request formatting
        self.api_formatter = create_bedrock_formatter()
        
        # Initialize boto3 session and Bedrock runtime client
        session = boto3.Session()
        self.bedrock_runtime = session.client("bedrock-runtime", region_name=region_name)
        
        logger.info(f"TitanEmbeddingModel initialized: model={self.model_id}, dimension={self.embedding_dimension}")
    

    
    def generate_embeddings(self, text: Optional[str] = None, image = None) -> List[float]:
        """
        Generate embeddings using Titan Embed Image model.
        
        Args:
            text: Text content to embed
            image: Image content to embed
            
        Returns:
            Vector embedding as list of floats
        """
        if not text and not image:
            raise ValueError("At least one of text or image must be provided")
        
        # Prepare image data if provided
        image_data = None
        if image:
            image_data = ImageProcessor.image_to_bytes(image, resize=True, size=(256, 256))
        
        # Use API formatter to create properly formatted request
        body = self.api_formatter.format_multimodal_request(
            text=text,
            image_data=image_data,
            embedding_dimension=self.embedding_dimension
        )
        
        # Validate request format
        if not self.api_formatter.validate_request_format(body, "titan_multimodal"):
            raise ValueError("Invalid request format for Titan multimodal embedding")
        
        logger.debug(f"Generating embeddings: text={bool(text)}, image={bool(image)}, dimension={self.embedding_dimension}")
        
        # Make API call to Bedrock
        response = self.bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId=self.model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response.get("body").read())
        embeddings = response_body.get("embedding")
        
        if not embeddings:
            raise RuntimeError(f"No embeddings returned from model. Response: {response_body}")
        
        logger.debug(f"Generated embeddings: dimension={len(embeddings)}")
        return embeddings