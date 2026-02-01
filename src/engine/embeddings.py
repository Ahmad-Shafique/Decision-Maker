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
        
        Tries Gemini first, then falls back to DeepSeek if configured.
        """
        # Checks cache first
        if text in self._cache:
            return self._cache[text]

        # 1. Try Gemini
        if self.api_key:
            try:
                url = f"{self.base_url}/{self.model}:embedContent?key={self.api_key}"
                payload = {"content": {"parts": [{"text": text}]}}
                
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding", {}).get("values")
                
                if embedding:
                    self._cache[text] = embedding
                    return embedding
            except Exception as e:
                print(f"Warning: Gemini embedding failed: {e}. Trying fallback...")
        
        # 2. Try DeepSeek Fallback
        return self._embed_with_deepseek(text)

    def _embed_with_deepseek(self, text: str) -> Optional[List[float]]:
        """Fallback to DeepSeek (or compatible OpenAI implementation)."""
        ds_key = os.getenv("DEEPSEEK_API_KEY")
        ds_endpoint = os.getenv("DEEPSEEK_API_ENDPOINT", "https://api.deepseek.com/v1")
        
        if not ds_key:
            print("Warning: No DeepSeek API key (DEEPSEEK_API_KEY) found for fallback.")
            return None
            
        try:
            # Using standard OpenAI-compatible format
            # Endpoint is usually .../embeddings
            # If user provided base URL like https://api.deepseek.com/v1, append /embeddings
            if not ds_endpoint.endswith("/embeddings"):
                 ds_endpoint = ds_endpoint.rstrip("/") + "/embeddings"
                 
            headers = {
                "Authorization": f"Bearer {ds_key}",
                "Content-Type": "application/json"
            }
            # DeepSeek usually uses text-embedding-ada-002 compatible or their own model
            # Assuming 'deepseek-embedding' or similar. Use config or default.
            model = os.getenv("DEEPSEEK_EMBEDDING_MODEL", "deepseek-embedding")
            
            payload = {
                "input": text,
                "model": model
            }
            
            response = requests.post(ds_endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # OpenAI format: data -> data[0] -> embedding
            embedding = data.get("data", [])[0].get("embedding")
            
            if embedding:
                self._cache[text] = embedding
                print("DEBUG: Successfully used DeepSeek fallback.")
                return embedding
                
        except Exception as e:
            print(f"Error: DeepSeek fallback failed: {e}")
            
        return None

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for a list of texts (sequentially for now)."""
        return [self.embed_text(t) for t in texts]
