"""
Cost Tracker Middleware
=======================
Tracks token usage and API costs across requests.
"""

from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RequestRecord:
    """Record of a single API request"""
    timestamp: datetime
    endpoint: str
    tokens: int
    cost: float


class CostTracker:
    """
    Thread-safe cost tracking for API requests.
    
    Features:
    - Track total tokens and costs
    - Per-endpoint breakdown
    - Request history
    - Session summary
    """
    
    def __init__(self):
        self._lock = Lock()
        self._total_tokens = 0
        self._total_cost = 0.0
        self._total_requests = 0
        self._endpoint_stats: Dict[str, Dict] = {}
        self._recent_requests: List[RequestRecord] = []
        self._max_history = 100
    
    def add_request(self, endpoint: str, tokens: int, cost: float):
        """
        Record a request's usage.
        
        Args:
            endpoint: API endpoint called
            tokens: Total tokens used
            cost: Estimated cost in USD
        """
        with self._lock:
            self._total_tokens += tokens
            self._total_cost += cost
            self._total_requests += 1
            
            # Update endpoint stats
            if endpoint not in self._endpoint_stats:
                self._endpoint_stats[endpoint] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
            
            self._endpoint_stats[endpoint]["requests"] += 1
            self._endpoint_stats[endpoint]["tokens"] += tokens
            self._endpoint_stats[endpoint]["cost"] += cost
            
            # Add to history
            self._recent_requests.append(RequestRecord(
                timestamp=datetime.now(),
                endpoint=endpoint,
                tokens=tokens,
                cost=cost
            ))
            
            # Trim history
            if len(self._recent_requests) > self._max_history:
                self._recent_requests = self._recent_requests[-self._max_history:]
    
    def get_summary(self) -> Dict:
        """Get a summary of usage statistics"""
        with self._lock:
            return {
                "total_requests": self._total_requests,
                "total_tokens": self._total_tokens,
                "total_cost": round(self._total_cost, 6),
                "avg_tokens_per_request": (
                    round(self._total_tokens / self._total_requests, 2)
                    if self._total_requests > 0 else 0
                ),
                "avg_cost_per_request": (
                    round(self._total_cost / self._total_requests, 6)
                    if self._total_requests > 0 else 0
                ),
                "endpoints": {
                    endpoint: {
                        "requests": stats["requests"],
                        "tokens": stats["tokens"],
                        "cost": round(stats["cost"], 6)
                    }
                    for endpoint, stats in self._endpoint_stats.items()
                }
            }
    
    def get_recent_requests(self, n: int = 10) -> List[Dict]:
        """Get the most recent requests"""
        with self._lock:
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "endpoint": r.endpoint,
                    "tokens": r.tokens,
                    "cost": r.cost
                }
                for r in self._recent_requests[-n:]
            ]
    
    def reset(self):
        """Reset all tracking data"""
        with self._lock:
            self._total_tokens = 0
            self._total_cost = 0.0
            self._total_requests = 0
            self._endpoint_stats = {}
            self._recent_requests = []
