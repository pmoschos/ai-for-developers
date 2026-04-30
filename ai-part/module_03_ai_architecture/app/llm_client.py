"""
LLM Client
==========
Abstracted LLM client with retry logic, error handling, and cost tracking.
"""

import os
import time
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import tiktoken
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, APITimeoutError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.config import get_settings, estimate_cost

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Structured response from LLM"""
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    latency_ms: float
    estimated_cost: float


class LLMClient:
    """
    Production-ready LLM client with:
    - Retry logic with exponential backoff
    - Token counting
    - Cost estimation
    - Streaming support
    - Error handling
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            model: Model to use (default from settings)
        """
        settings = get_settings()
        self.model = model or settings.default_model
        self.client = OpenAI()
        self.encoder = self._get_encoder()
    
    def _get_encoder(self):
        """Get the appropriate tokenizer for the model"""
        try:
            return tiktoken.encoding_for_model(self.model)
        except KeyError:
            return tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        return len(self.encoder.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimate tokens for a list of messages"""
        total = 0
        for message in messages:
            total += 4  # Message overhead
            for key, value in message.items():
                total += self.count_tokens(str(value))
        total += 2  # Conversation overhead
        return total
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError, APITimeoutError))
    )
    def complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Send a completion request to the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters for the API
            
        Returns:
            LLMResponse with content and metadata
        """
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            cost = estimate_cost(self.model, input_tokens, output_tokens)
            
            logger.info(
                f"LLM request completed: {total_tokens} tokens, "
                f"${cost:.6f}, {latency_ms:.0f}ms"
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                model=self.model,
                latency_ms=latency_ms,
                estimated_cost=cost
            )
            
        except RateLimitError as e:
            logger.warning(f"Rate limited, will retry: {e}")
            raise
        except APIConnectionError as e:
            logger.error(f"Connection error, will retry: {e}")
            raise
        except APITimeoutError as e:
            logger.error(f"Timeout, will retry: {e}")
            raise
        except APIError as e:
            logger.error(f"API error (not retrying): {e}")
            raise
    
    def simple_complete(self, prompt: str, system: Optional[str] = None, **kwargs) -> LLMResponse:
        """
        Simplified completion with just a prompt.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with content and metadata
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        return self.complete(messages, **kwargs)


class LLMClientManager:
    """Manages LLM client singleton without using global keyword"""
    
    def __init__(self):
        self._client: Optional[LLMClient] = None
    
    def get_client(self) -> LLMClient:
        """Get or create the LLM client singleton"""
        if self._client is None:
            self._client = LLMClient()
        return self._client


# Singleton manager instance
_llm_manager = LLMClientManager()


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton"""
    return _llm_manager.get_client()
