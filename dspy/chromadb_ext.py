import chromadb
from typing import List, Optional, Union, Any
from chromadb.api.types import (
    Documents,
    EmbeddingFunction,
    Embeddings,
    Embeddable,
)
import chromadb.utils.embedding_functions
from chromadb.config import Settings
import json

class AmazonBedrockTitanMultiModalEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(
        self,
        session: "boto3.Session",  
        model_name: str = "amazon.titan-embed-image-v1",
        **kwargs: Any,
    ):
        self._model_name = model_name
        self._client = session.client(
            service_name="bedrock-runtime",
            **kwargs,
        )

    def embed(self, inputText:str =None,inputImage:str = None) -> Embeddings:
        accept = "application/json"
        content_type = "application/json"
        body = {}
        if inputText:
            body["inputText"] = inputText
        if inputImage:
            body["inputImage"] = inputImage
            body = json.dumps(body)
            response = self._client.invoke_model(
                body=body,
                modelId=self._model_name,
                accept=accept,
                contentType=content_type,
            )
            embedding = json.load(response.get("body")).get("embedding")
        return [embedding]



class AmazonBedrockCohereEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(
        self,
        session: "boto3.Session",  
        model_name: str = "cohere.embed-english-v3",
        input_type:str = "search_document",
        **kwargs: Any,
    ):
        self._model_name = model_name
        self.input_type = input_type
        self._client = session.client(
            service_name="bedrock-runtime",
            **kwargs,
        )

    def __call__(self, input: Documents) -> Embeddings:
        accept = "application/json"
        content_type = "application/json"
 
        embeddings = []
        for text in input:
            input_body = {"texts": [text], "input_type": self.input_type, "truncate":"START"}
            body = json.dumps(input_body)
            response = self._client.invoke_model(
                body=body,
                modelId=self._model_name,
                accept=accept,
                contentType=content_type,
            )
            embedding = json.load(response.get("body")).get("embeddings")
            embeddings.append(embedding)
        return embeddings