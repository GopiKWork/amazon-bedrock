"""
Nova Pro Multimodal LLM Implementation
=====================================

Concrete implementation using Amazon Bedrock Nova Pro for multimodal text generation.
"""

import json
import base64
import io
import pathlib
import logging
from typing import List
from PIL import Image as PILImage
import boto3

from ..base_classes import BaseMultimodalLLM
from ..validation import create_bedrock_formatter
from ..utils.image_processing import ImageProcessor

logger = logging.getLogger(__name__)


class NovaProMultimodalLLM(BaseMultimodalLLM):
    """Nova Pro multimodal LLM implementation."""
    
    def __init__(self, region_name: str = 'us-west-2', model_id: str = None):
        """
        Initialize Nova Pro multimodal LLM.
        
        Args:
            region_name: AWS region for Bedrock service
            model_id: Model ID to use (optional, defaults to us.amazon.nova-pro-v1:0)
        """
        self.region_name = region_name
        self.model_id = model_id or 'us.amazon.nova-pro-v1:0'
        
        # Initialize API formatter for proper request formatting
        self.api_formatter = create_bedrock_formatter()
        
        # Initialize boto3 session and Bedrock runtime client
        session = boto3.Session()
        self.bedrock_runtime = session.client("bedrock-runtime", region_name=region_name)
        
        logger.info(f"NovaProMultimodalLLM initialized: model={self.model_id}")
    

    
    def generate_text_description(self, image) -> str:
        """
        Generate detailed text description from image using Nova Pro.
        
        Args:
            image: Image content to describe
            
        Returns:
            Detailed text description of the image
        """
        # Convert image to bytes
        image_bytes = ImageProcessor.image_to_bytes(image, resize=False, size=(256, 256))
        
        # Prepare the prompt for detailed description
        prompt = """You are an assistant tasked with generating detailed descriptions of images for retrieval purposes. 
        These descriptions will be embedded and used to retrieve the original image. 
        Provide a comprehensive, well-structured description that captures:
        - Main objects, people, or subjects in the image
        - Visual characteristics (colors, textures, lighting)
        - Spatial relationships and composition
        - Context and setting
        - Any text or symbols visible
        - Overall mood or atmosphere
        
        Make the description detailed enough for accurate retrieval while being concise and well-organized."""
        
        # Create properly formatted multimodal message
        message = self.api_formatter.create_multimodal_message(
            text=prompt,
            image_data=image_bytes,
            image_format="jpeg"
        )
        
        # Use API formatter to create properly formatted request
        body = self.api_formatter.format_text_generation_request(
            messages=[message],
            max_tokens=4096,
            temperature=0.1
        )
        
        # Validate request format
        if not self.api_formatter.validate_request_format(body, "nova_pro"):
            raise ValueError("Invalid request format for Nova Pro multimodal")
        
        logger.debug(f"Generating text description for image")
        
        # Make API call to Bedrock
        response = self.bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId=self.model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse response for Nova Pro
        response_body = json.loads(response.get("body").read())
        text_description = response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")
        
        if not text_description:
            raise RuntimeError(f"No text description returned from model. Response: {response_body}")
        
        logger.debug(f"Generated text description: {len(text_description)} characters")
        return text_description