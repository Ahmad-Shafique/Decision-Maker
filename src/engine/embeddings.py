"""Embedding Service - Generate vector embeddings for text.

This module provides the EmbeddingService which interfaces with the Gemini API
to generate semantic vector embeddings for principles and situations.
"""

import os
import json
import requests
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """Service to generate embeddings using Gemini API."""
    
    def __init__(self):
        """Initialize the service."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Use text-embedding-004 as planned
        self.model = "text-embedding-004"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self._cache = {}

    def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text string.
        
        Args:
            text: The text to embed.
            
        Returns:
            List of floats representing the vector, or None if failed.
        """
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found.")
            return None

        if text in self._cache:
            return self._cache[text]

        url = f"{self.base_url}/{self.model}:embedContent?key={self.api_key}"
        
        payload = {
            "content": {
                "parts": [{"text": text}]
            }
        }
        
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract embedding
            # Response format: {"embedding": {"values": [...]}}
            embedding = data.get("embedding", {}).get("values")
            
            if embedding:
                self._cache[text] = embedding
                return embedding
            else:
                print(f"Error: No embedding found in response: {data}")
                return None
                
        except Exception as e:
            print(f"Embedding failed: {e}")
            return None

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for a list of texts (sequentially for now)."""
        return [self.embed_text(t) for t in texts]
