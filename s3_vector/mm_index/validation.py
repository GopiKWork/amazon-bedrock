"""
Vector Validation and Transformation Utilities
==============================================

This module provides validation and transformation utilities for S3 Vector operations,
ensuring vectors meet AWS service requirements and handling common validation errors.
"""

import logging
import numpy as np
import base64
import json
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class VectorConfig:
    """Configuration for vector validation and transformation."""
    dimension: int = 384
    data_type: str = "float32"
    distance_metric: str = "cosine"
    
    def validate(self) -> bool:
        """Validate that the configuration is supported by AWS services."""
        return self.dimension in [256, 384, 1024]


@dataclass
class MetadataConfig:
    """Configuration for metadata validation and limiting."""
    max_tags: int = 10
    priority_tags: List[str] = field(default_factory=lambda: [
        'damage_id', 'vehicle_make', 'vehicle_model', 'damage_type'
    ])
    excluded_tags: List[str] = field(default_factory=list)


class VectorDimensionManager:
    """
    Manages vector dimensions to ensure compatibility with S3 Vector Store.
    
    Handles dimension validation, transformation, and embedding configuration
    to prevent common validation errors.
    """
    
    def __init__(self, target_dimension: int = 384):
        """
        Initialize the dimension manager.
        
        Args:
            target_dimension: Target vector dimension (256, 384, or 1024)
        """
        self.target_dimension = target_dimension
        self.config = VectorConfig(dimension=target_dimension)
        
        if not self.config.validate():
            raise ValueError(f"Unsupported target dimension: {target_dimension}. Must be 256, 384, or 1024.")
        
        logger.info(f"VectorDimensionManager initialized with target dimension: {target_dimension}")
    
    def validate_and_transform(self, vector: Union[List[float], np.ndarray]) -> List[float]:
        """
        Validate and transform vector to target dimensions.
        
        Args:
            vector: Input vector as list or numpy array
            
        Returns:
            Transformed vector with correct dimensions and data type
            
        Raises:
            ValueError: If vector cannot be transformed to target dimensions
        """
        # Convert to numpy array for easier manipulation
        if isinstance(vector, list):
            vector_array = np.array(vector, dtype=np.float32)
        elif isinstance(vector, np.ndarray):
            vector_array = vector.astype(np.float32)
        else:
            raise ValueError(f"Unsupported vector type: {type(vector)}")
        
        original_dimension = len(vector_array)
        logger.debug(f"Input vector dimension: {original_dimension}, target: {self.target_dimension}")
        
        # If dimensions match, just ensure float32 format
        if original_dimension == self.target_dimension:
            return self.ensure_float32(vector_array.tolist())
        
        # Handle dimension transformation
        if original_dimension > self.target_dimension:
            # Truncate vector (simple approach - could use PCA for better results)
            transformed_vector = vector_array[:self.target_dimension]
            logger.warning(f"Truncated vector from {original_dimension} to {self.target_dimension} dimensions")
        else:
            # Pad vector with zeros
            padding_size = self.target_dimension - original_dimension
            transformed_vector = np.pad(vector_array, (0, padding_size), mode='constant', constant_values=0.0)
            logger.warning(f"Padded vector from {original_dimension} to {self.target_dimension} dimensions")
        
        return self.ensure_float32(transformed_vector.tolist())
    
    def ensure_float32(self, vector: List[float]) -> List[float]:
        """
        Ensure vector values are float32 format as required by AWS S3 Vector.
        
        Args:
            vector: Input vector
            
        Returns:
            Vector with float32 values
        """
        return [float(np.float32(value)) for value in vector]
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """
        Get proper embedding configuration for Bedrock models.
        
        Returns:
            Configuration dictionary for Titan Multimodal Embeddings
        """
        return {
            "embeddingConfig": {
                "outputEmbeddingLength": self.target_dimension
            }
        }
    
    def validate_vector_batch(self, vectors: List[Union[List[float], np.ndarray]]) -> List[List[float]]:
        """
        Validate and transform a batch of vectors.
        
        Args:
            vectors: List of input vectors
            
        Returns:
            List of transformed vectors
        """
        transformed_vectors = []
        for i, vector in enumerate(vectors):
            try:
                transformed = self.validate_and_transform(vector)
                transformed_vectors.append(transformed)
            except Exception as e:
                logger.error(f"Failed to transform vector {i}: {e}")
                raise ValueError(f"Vector {i} transformation failed: {e}")
        
        logger.info(f"Successfully transformed {len(transformed_vectors)} vectors to {self.target_dimension} dimensions")
        return transformed_vectors
    
    def get_dimension_info(self) -> Dict[str, Any]:
        """
        Get information about the current dimension configuration.
        
        Returns:
            Dictionary with dimension configuration details
        """
        return {
            "target_dimension": self.target_dimension,
            "data_type": self.config.data_type,
            "distance_metric": self.config.distance_metric,
            "supported_dimensions": [256, 384, 1024]
        }


class MetadataLimiter:
    """
    Manages metadata to ensure compliance with S3 Vector Store limits.
    
    AWS S3 Vector Store has a limit of 10 metadata tags per vector.
    This class ensures metadata doesn't exceed this limit while preserving
    the most important information.
    """
    
    def __init__(self, max_tags: int = 10, max_value_bytes: int = 2048, priority_tags: Optional[List[str]] = None):
        """
        Initialize the metadata limiter.
        
        Args:
            max_tags: Maximum number of metadata tags allowed (AWS limit is 10)
            max_value_bytes: Maximum bytes per metadata value (AWS limit is 2048)
            priority_tags: List of tags that should be preserved if possible
        """
        self.max_tags = max_tags
        self.max_value_bytes = max_value_bytes
        self.priority_tags = priority_tags or [
            'damage_id', 'vehicle_make', 'vehicle_model', 'damage_type',
            'strategy', 'severity', 'estimated_cost'
        ]
        self.config = MetadataConfig(max_tags=max_tags, priority_tags=self.priority_tags)
        
        logger.info(f"MetadataLimiter initialized with max_tags: {max_tags}, max_value_bytes: {max_value_bytes}, priority_tags: {len(self.priority_tags)}")
    
    def limit_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limit metadata to max_tags while preserving priority tags and handling byte size limits.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Limited metadata dictionary with at most max_tags entries and compliant total size
        """
        if not metadata:
            return {}
        
        original_count = len(metadata)
        
        # Start with priority tags that exist in the metadata
        limited_metadata = {}
        remaining_slots = self.max_tags
        current_total_bytes = 0
        
        # First, add priority tags if they fit
        for tag in self.priority_tags:
            if tag in metadata and remaining_slots > 0:
                value_str = str(metadata[tag])
                value_bytes = len(value_str.encode('utf-8'))
                
                # Check if adding this tag would exceed total byte limit
                if current_total_bytes + value_bytes <= self.max_value_bytes:
                    limited_metadata[tag] = metadata[tag]
                    remaining_slots -= 1
                    current_total_bytes += value_bytes
                else:
                    # Try to truncate the value to fit
                    available_bytes = self.max_value_bytes - current_total_bytes
                    if available_bytes > 10:  # Need at least some space for meaningful content
                        truncated_value = self._truncate_to_bytes(value_str, available_bytes - 3) + "..."
                        limited_metadata[tag] = truncated_value
                        remaining_slots -= 1
                        current_total_bytes += len(truncated_value.encode('utf-8'))
                        logger.warning(f"Truncated priority tag '{tag}': {value_bytes} bytes -> {len(truncated_value.encode('utf-8'))} bytes")
                    else:
                        logger.warning(f"Skipped priority tag '{tag}': would exceed total byte limit")
        
        # Then add remaining tags until we hit the limits
        for key, value in metadata.items():
            if key not in limited_metadata and remaining_slots > 0:
                value_str = str(value)
                value_bytes = len(value_str.encode('utf-8'))
                
                # Check if adding this tag would exceed total byte limit
                if current_total_bytes + value_bytes <= self.max_value_bytes:
                    limited_metadata[key] = value
                    remaining_slots -= 1
                    current_total_bytes += value_bytes
                else:
                    # Try to truncate the value to fit
                    available_bytes = self.max_value_bytes - current_total_bytes
                    if available_bytes > 10:  # Need at least some space for meaningful content
                        truncated_value = self._truncate_to_bytes(value_str, available_bytes - 3) + "..."
                        limited_metadata[key] = truncated_value
                        remaining_slots -= 1
                        current_total_bytes += len(truncated_value.encode('utf-8'))
                        logger.warning(f"Truncated tag '{key}': {value_bytes} bytes -> {len(truncated_value.encode('utf-8'))} bytes")
                        break  # No more space available
                    else:
                        logger.warning(f"Skipped tag '{key}': would exceed total byte limit")
                        break  # No more space available
        
        # Log what was excluded
        excluded_tags = [key for key in metadata.keys() if key not in limited_metadata]
        if excluded_tags:
            self.log_excluded_tags(metadata, limited_metadata)
        
        logger.info(f"Limited metadata: {original_count} -> {len(limited_metadata)} tags, total size: {current_total_bytes} bytes")
        return limited_metadata
    
    def log_excluded_tags(self, original: Dict[str, Any], limited: Dict[str, Any]) -> None:
        """
        Log which tags were excluded for debugging purposes.
        
        Args:
            original: Original metadata dictionary
            limited: Limited metadata dictionary
        """
        excluded_tags = [key for key in original.keys() if key not in limited.keys()]
        
        if excluded_tags:
            logger.warning(f"Excluded {len(excluded_tags)} metadata tags due to limit: {excluded_tags}")
            
            # Log the values of excluded tags for debugging
            excluded_info = {tag: original[tag] for tag in excluded_tags}
            logger.debug(f"Excluded tag values: {excluded_info}")
    
    def validate_metadata_size(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate that metadata is within size limits.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            True if metadata is within limits, False otherwise
        """
        if not metadata:
            return True
        
        tag_count = len(metadata)
        is_valid = tag_count <= self.max_tags
        
        if not is_valid:
            logger.warning(f"Metadata validation failed: {tag_count} tags > {self.max_tags} limit")
        
        return is_valid
    
    def get_metadata_info(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about metadata structure and compliance.
        
        Args:
            metadata: Metadata dictionary to analyze
            
        Returns:
            Dictionary with metadata analysis information
        """
        if not metadata:
            return {
                "tag_count": 0,
                "within_limits": True,
                "priority_tags_present": [],
                "non_priority_tags": [],
                "would_be_excluded": []
            }
        
        tag_count = len(metadata)
        within_limits = tag_count <= self.max_tags
        priority_tags_present = [tag for tag in self.priority_tags if tag in metadata]
        non_priority_tags = [tag for tag in metadata.keys() if tag not in self.priority_tags]
        
        # Simulate what would be excluded
        would_be_excluded = []
        if not within_limits:
            limited = self.limit_metadata(metadata)
            would_be_excluded = [tag for tag in metadata.keys() if tag not in limited]
        
        return {
            "tag_count": tag_count,
            "within_limits": within_limits,
            "priority_tags_present": priority_tags_present,
            "non_priority_tags": non_priority_tags,
            "would_be_excluded": would_be_excluded,
            "max_tags_limit": self.max_tags
        }
    
    def add_strategy_metadata(self, metadata: Dict[str, Any], strategy: str) -> Dict[str, Any]:
        """
        Add strategy information to metadata, ensuring it fits within limits.
        
        Args:
            metadata: Original metadata
            strategy: Indexing strategy used
            
        Returns:
            Metadata with strategy information added
        """
        enhanced_metadata = metadata.copy() if metadata else {}
        enhanced_metadata['strategy'] = strategy
        
        return self.limit_metadata(enhanced_metadata)
    

    
    def _truncate_to_bytes(self, text: str, max_bytes: int) -> str:
        """
        Truncate text to fit within a specific byte limit.
        
        Args:
            text: Text to truncate
            max_bytes: Maximum bytes allowed
            
        Returns:
            Truncated text that fits within byte limit
        """
        if len(text.encode('utf-8')) <= max_bytes:
            return text
        
        # Binary search to find the right truncation point
        left, right = 0, len(text)
        result = ""
        
        while left <= right:
            mid = (left + right) // 2
            candidate = text[:mid]
            
            if len(candidate.encode('utf-8')) <= max_bytes:
                result = candidate
                left = mid + 1
            else:
                right = mid - 1
        
        return result


class BedrockAPIFormatter:
    """
    Formats and validates Bedrock API requests to prevent malformed request errors.
    
    Handles proper formatting for different Bedrock models including Titan Multimodal
    Embeddings and Nova Pro models.
    """
    
    # Request templates for different models
    TITAN_MULTIMODAL_TEMPLATE = {
        "inputText": str,
        "inputImage": str,  # base64 encoded
        "embeddingConfig": {
            "outputEmbeddingLength": int  # 256, 384, or 1024
        }
    }
    
    NOVA_PRO_TEMPLATE = {
        "messages": [
            {
                "role": str,
                "content": [
                    {
                        "text": str
                    },
                    {
                        "image": {
                            "format": str,
                            "source": {
                                "bytes": str  # base64 encoded
                            }
                        }
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": int,
            "temperature": float
        }
    }
    
    def __init__(self):
        """Initialize the API formatter."""
        logger.info("BedrockAPIFormatter initialized")
    
    def format_multimodal_request(self, text: Optional[str] = None, 
                                image_data: Optional[bytes] = None,
                                embedding_dimension: int = 384) -> Dict[str, Any]:
        """
        Format request for Titan Multimodal Embeddings.
        
        Args:
            text: Text content to embed
            image_data: Image data as bytes
            embedding_dimension: Target embedding dimension
            
        Returns:
            Properly formatted request dictionary
            
        Raises:
            ValueError: If neither text nor image is provided
        """
        if not text and not image_data:
            raise ValueError("At least one of text or image_data must be provided")
        
        if embedding_dimension not in [256, 384, 1024]:
            raise ValueError(f"Invalid embedding dimension: {embedding_dimension}. Must be 256, 384, or 1024")
        
        request = {
            "embeddingConfig": {
                "outputEmbeddingLength": embedding_dimension
            }
        }
        
        if text:
            request["inputText"] = text
        
        if image_data:
            # Encode image data to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            request["inputImage"] = image_b64
        
        logger.debug(f"Formatted Titan multimodal request with text: {bool(text)}, image: {bool(image_data)}")
        return request
    
    def format_text_generation_request(self, messages: List[Dict[str, Any]], 
                                     max_tokens: int = 1000,
                                     temperature: float = 0.7) -> Dict[str, Any]:
        """
        Format request for text generation models like Nova Pro.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Properly formatted request dictionary
        """
        # Validate and clean message format
        formatted_messages = []
        for message in messages:
            formatted_message = self._format_message(message)
            formatted_messages.append(formatted_message)
        
        request = {
            "messages": formatted_messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        logger.debug(f"Formatted text generation request with {len(formatted_messages)} messages")
        return request
    
    def _format_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a single message, removing extraneous keys.
        
        Args:
            message: Original message dictionary
            
        Returns:
            Cleaned message dictionary
        """
        # Start with required fields
        formatted = {
            "role": message.get("role", "user")
        }
        
        # Handle content - can be string or list
        content = message.get("content", "")
        if isinstance(content, str):
            formatted["content"] = [{"text": content}]
        elif isinstance(content, list):
            formatted_content = []
            for item in content:
                if isinstance(item, dict):
                    # Remove extraneous keys like 'type'
                    clean_item = {}
                    if "text" in item:
                        clean_item["text"] = item["text"]
                    elif "image" in item:
                        clean_item["image"] = item["image"]
                    formatted_content.append(clean_item)
                else:
                    # Handle string content in list
                    formatted_content.append({"text": str(item)})
            formatted["content"] = formatted_content
        else:
            formatted["content"] = [{"text": str(content)}]
        
        return formatted
    
    def validate_request_format(self, request: Dict[str, Any], model_type: str = "titan_multimodal") -> bool:
        """
        Validate request format before sending to Bedrock.
        
        Args:
            request: Request dictionary to validate
            model_type: Type of model ("titan_multimodal" or "nova_pro")
            
        Returns:
            True if request format is valid, False otherwise
        """
        try:
            if model_type == "titan_multimodal":
                return self._validate_titan_request(request)
            elif model_type == "nova_pro":
                return self._validate_nova_request(request)
            else:
                logger.warning(f"Unknown model type for validation: {model_type}")
                return False
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            return False
    
    def _validate_titan_request(self, request: Dict[str, Any]) -> bool:
        """Validate Titan Multimodal Embeddings request format."""
        # Must have embeddingConfig
        if "embeddingConfig" not in request:
            logger.error("Missing embeddingConfig in Titan request")
            return False
        
        embedding_config = request["embeddingConfig"]
        if "outputEmbeddingLength" not in embedding_config:
            logger.error("Missing outputEmbeddingLength in embeddingConfig")
            return False
        
        dimension = embedding_config["outputEmbeddingLength"]
        if dimension not in [256, 384, 1024]:
            logger.error(f"Invalid outputEmbeddingLength: {dimension}")
            return False
        
        # Must have at least inputText or inputImage
        has_text = "inputText" in request and request["inputText"]
        has_image = "inputImage" in request and request["inputImage"]
        
        if not has_text and not has_image:
            logger.error("Titan request must have inputText or inputImage")
            return False
        
        return True
    
    def _validate_nova_request(self, request: Dict[str, Any]) -> bool:
        """Validate Nova Pro request format."""
        # Must have messages
        if "messages" not in request:
            logger.error("Missing messages in Nova request")
            return False
        
        messages = request["messages"]
        if not isinstance(messages, list) or len(messages) == 0:
            logger.error("Messages must be a non-empty list")
            return False
        
        # Validate each message
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                logger.error(f"Message {i} must be a dictionary")
                return False
            
            if "role" not in message:
                logger.error(f"Message {i} missing role")
                return False
            
            if "content" not in message:
                logger.error(f"Message {i} missing content")
                return False
            
            # Check for extraneous keys in content
            content = message["content"]
            if isinstance(content, list):
                for j, item in enumerate(content):
                    if isinstance(item, dict) and "type" in item:
                        logger.error(f"Message {i}, content {j} has extraneous 'type' key")
                        return False
        
        return True
    
    def encode_image_to_base64(self, image_data: bytes) -> str:
        """
        Encode image data to base64 string.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_data).decode('utf-8')
    
    def create_multimodal_message(self, text: str, image_data: Optional[bytes] = None,
                                image_format: str = "jpeg") -> Dict[str, Any]:
        """
        Create a properly formatted multimodal message for Nova Pro.
        
        Args:
            text: Text content
            image_data: Optional image data as bytes
            image_format: Image format (jpeg, png, etc.)
            
        Returns:
            Formatted message dictionary
        """
        content = [{"text": text}]
        
        if image_data:
            image_b64 = self.encode_image_to_base64(image_data)
            content.append({
                "image": {
                    "format": image_format,
                    "source": {
                        "bytes": image_b64
                    }
                }
            })
        
        return {
            "role": "user",
            "content": content
        }


def create_dimension_manager(target_dimension: int = 384) -> VectorDimensionManager:
    """
    Factory function to create a VectorDimensionManager with validation.
    
    Args:
        target_dimension: Target vector dimension
        
    Returns:
        Configured VectorDimensionManager instance
    """
    return VectorDimensionManager(target_dimension=target_dimension)


def create_metadata_limiter(max_tags: int = 10, max_value_bytes: int = 2048, priority_tags: Optional[List[str]] = None) -> MetadataLimiter:
    """
    Factory function to create a MetadataLimiter with validation.
    
    Args:
        max_tags: Maximum number of metadata tags allowed
        max_value_bytes: Maximum bytes per metadata value
        priority_tags: List of priority tags to preserve
        
    Returns:
        Configured MetadataLimiter instance
    """
    return MetadataLimiter(max_tags=max_tags, max_value_bytes=max_value_bytes, priority_tags=priority_tags)


def create_bedrock_formatter() -> BedrockAPIFormatter:
    """
    Factory function to create a BedrockAPIFormatter.
    
    Returns:
        Configured BedrockAPIFormatter instance
    """
    return BedrockAPIFormatter()


# Convenience functions for common operations
def validate_vector_dimension(vector: Union[List[float], np.ndarray], 
                            target_dimension: int = 384) -> List[float]:
    """
    Convenience function to validate and transform a single vector.
    
    Args:
        vector: Input vector
        target_dimension: Target dimension
        
    Returns:
        Transformed vector
    """
    manager = VectorDimensionManager(target_dimension)
    return manager.validate_and_transform(vector)


def get_bedrock_embedding_config(dimension: int = 384) -> Dict[str, Any]:
    """
    Convenience function to get Bedrock embedding configuration.
    
    Args:
        dimension: Target embedding dimension
        
    Returns:
        Bedrock embedding configuration
    """
    manager = VectorDimensionManager(dimension)
    return manager.get_embedding_config()


def limit_metadata_tags(metadata: Dict[str, Any], max_tags: int = 10, 
                       priority_tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function to limit metadata tags.
    
    Args:
        metadata: Original metadata dictionary
        max_tags: Maximum number of tags allowed
        priority_tags: List of priority tags to preserve
        
    Returns:
        Limited metadata dictionary
    """
    limiter = MetadataLimiter(max_tags=max_tags, priority_tags=priority_tags)
    return limiter.limit_metadata(metadata)


def validate_metadata_compliance(metadata: Dict[str, Any], max_tags: int = 10) -> bool:
    """
    Convenience function to validate metadata compliance.
    
    Args:
        metadata: Metadata dictionary to validate
        max_tags: Maximum number of tags allowed
        
    Returns:
        True if metadata is compliant, False otherwise
    """
    limiter = MetadataLimiter(max_tags=max_tags)
    return limiter.validate_metadata_size(metadata)


def format_titan_multimodal_request(text: Optional[str] = None, 
                                   image_data: Optional[bytes] = None,
                                   embedding_dimension: int = 384) -> Dict[str, Any]:
    """
    Convenience function to format Titan Multimodal Embeddings request.
    
    Args:
        text: Text content to embed
        image_data: Image data as bytes
        embedding_dimension: Target embedding dimension
        
    Returns:
        Formatted request dictionary
    """
    formatter = BedrockAPIFormatter()
    return formatter.format_multimodal_request(text, image_data, embedding_dimension)


def format_nova_pro_request(messages: List[Dict[str, Any]], 
                          max_tokens: int = 1000,
                          temperature: float = 0.7) -> Dict[str, Any]:
    """
    Convenience function to format Nova Pro request.
    
    Args:
        messages: List of message dictionaries
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        Formatted request dictionary
    """
    formatter = BedrockAPIFormatter()
    return formatter.format_text_generation_request(messages, max_tokens, temperature)


def validate_bedrock_request(request: Dict[str, Any], model_type: str = "titan_multimodal") -> bool:
    """
    Convenience function to validate Bedrock API request format.
    
    Args:
        request: Request dictionary to validate
        model_type: Type of model ("titan_multimodal" or "nova_pro")
        
    Returns:
        True if request format is valid, False otherwise
    """
    formatter = BedrockAPIFormatter()
    return formatter.validate_request_format(request, model_type)