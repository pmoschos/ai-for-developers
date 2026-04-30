"""
Simple Rate Limiter
===================
Basic rate limiting for API endpoints.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000


class RateLimiter:
    """
    Simple sliding window rate limiter.
    
    Note: For production, use Redis-based rate limiting (e.g., slowapi, fastapi-limiter)
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self._lock = Lock()
        self._request_times: Dict[str, list] = defaultdict(list)
        self._token_counts: Dict[str, list] = defaultdict(list)
    
    def _clean_old_entries(self, entries: list, window_start: float):
        """Remove entries older than the window"""
        return [e for e in entries if e[0] > window_start]
    
    def check_rate_limit(self, client_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if a client is within rate limits.
        
        Args:
            client_id: Unique identifier for the client (IP, API key, etc.)
            
        Returns:
            Tuple of (allowed, error_message)
        """
        now = time.time()
        window_start = now - 60  # 1-minute window
        
        with self._lock:
            # Clean old entries
            self._request_times[client_id] = self._clean_old_entries(
                self._request_times[client_id], window_start
            )
            
            # Check request rate limit
            if len(self._request_times[client_id]) >= self.config.requests_per_minute:
                return False, f"Rate limit exceeded: {self.config.requests_per_minute} requests per minute"
            
            # Add current request
            self._request_times[client_id].append((now,))
            
            return True, None
    
    def add_tokens(self, client_id: str, tokens: int):
        """Record tokens used by a client"""
        now = time.time()
        
        with self._lock:
            self._token_counts[client_id].append((now, tokens))
    
    def get_remaining(self, client_id: str) -> Dict[str, int]:
        """Get remaining quota for a client"""
        now = time.time()
        window_start = now - 60
        
        with self._lock:
            self._request_times[client_id] = self._clean_old_entries(
                self._request_times[client_id], window_start
            )
            
            requests_used = len(self._request_times[client_id])
            
            return {
                "requests_remaining": max(0, self.config.requests_per_minute - requests_used),
                "requests_limit": self.config.requests_per_minute,
                "window_seconds": 60
            }
