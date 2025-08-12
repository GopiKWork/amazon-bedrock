"""
Nova Pro LLM Implementation
==========================

Concrete implementation using Amazon Bedrock Nova Pro for text summarization.
"""

import json
import boto3

from ..base_classes import BaseLLM


class NovaProLLM(BaseLLM):
    """Nova Pro LLM implementation for text summarization."""
    
    def __init__(self, region_name: str = 'us-west-2', model_id: str = None):
        """
        Initialize Nova Pro LLM.
        
        Args:
            region_name: AWS region for Bedrock service
            model_id: Model ID to use (optional, defaults to us.amazon.nova-pro-v1:0)
        """
        self.region_name = region_name
        self.model_id = model_id or 'us.amazon.nova-pro-v1:0'
        
        # Initialize boto3 session and Bedrock runtime client
        session = boto3.Session()
        self.bedrock_runtime = session.client("bedrock-runtime", region_name=region_name)
    
    def generate_summary(self, text: str) -> str:
        """
        Generate concise summary from raw text using Nova Pro.
        
        Args:
            text: Raw text content to summarize
            
        Returns:
            Concise summary of the input text
        """
        # Prepare the prompt for summarization
        prompt = f"""You are an expert at creating concise, informative summaries. 
        Please provide a well-structured summary of the following text that:
        - Captures the key points and main ideas
        - Preserves important details and context
        - Is significantly shorter than the original while maintaining semantic meaning
        - Uses clear, professional language
        - Organizes information logically
        
        Text to summarize:
        {text}
        
        Summary:"""
        
        # Prepare request body for Nova Pro
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 2048,
                "temperature": 0.1
            }
        }
        
        # Make API call to Bedrock
        response = self.bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId=self.model_id,
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse response for Nova Pro
        response_body = json.loads(response.get("body").read())
        return response_body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")