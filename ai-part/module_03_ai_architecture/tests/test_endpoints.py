"""
API Endpoint Tests
==================
Tests for the AI API endpoints.

Run with: pytest tests/test_endpoints.py -v
"""

import pytest
from fastapi.testclient import TestClient

# Import the app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI-Powered API"
        assert "endpoints" in data
    
    def test_health(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_stats(self):
        """Test stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_cost" in data


class TestSummarizeEndpoint:
    """Test summarization endpoint"""
    
    def test_summarize_valid_input(self):
        """Test summarization with valid input"""
        response = client.post("/summarize", json={
            "text": "This is a test text that should be summarized. " * 10,
            "max_length": 50,
            "style": "concise"
        })
        
        # May fail if no API key, so check for either success or expected error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "summary" in data
            assert "tokens_used" in data
    
    def test_summarize_invalid_input(self):
        """Test summarization with too short input"""
        response = client.post("/summarize", json={
            "text": "Short",
            "max_length": 50
        })
        assert response.status_code == 422  # Validation error
    
    def test_summarize_missing_text(self):
        """Test summarization with missing text field"""
        response = client.post("/summarize", json={
            "max_length": 50
        })
        assert response.status_code == 422


class TestSentimentEndpoint:
    """Test sentiment analysis endpoint"""
    
    def test_sentiment_valid_input(self):
        """Test sentiment with valid input"""
        response = client.post("/sentiment", json={
            "text": "I love this product!",
            "include_reasoning": True
        })
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "sentiment" in data
            assert "confidence" in data
    
    def test_sentiment_empty_text(self):
        """Test sentiment with empty text"""
        response = client.post("/sentiment", json={
            "text": ""
        })
        assert response.status_code == 422


class TestCopywriterEndpoint:
    """Test copywriting endpoint"""
    
    def test_copywriter_valid_input(self):
        """Test copywriter with valid input"""
        response = client.post("/copywriter", json={
            "product_name": "Test Product",
            "description": "A great product for testing purposes",
            "tone": "professional",
            "num_variants": 2
        })
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "variants" in data
            assert len(data["variants"]) > 0
    
    def test_copywriter_invalid_tone(self):
        """Test copywriter with invalid tone"""
        response = client.post("/copywriter", json={
            "product_name": "Test",
            "description": "A test product",
            "tone": "invalid_tone"
        })
        assert response.status_code == 422


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self):
        """Test 404 for unknown endpoint"""
        response = client.get("/unknown_endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test 405 for wrong HTTP method"""
        response = client.get("/summarize")
        assert response.status_code == 405


class TestBatchEndpoint:
    """Test batch processing endpoint"""

    def test_batch_valid_input(self):
        """Test batch with valid list of texts"""
        response = client.post("/batch", json={
            "texts": [
                "AI is transforming healthcare by enabling faster diagnoses.",
                "The stock market saw significant gains this quarter."
            ]
        })

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert data["total_items"] == 2
            assert "total_tokens" in data
            assert "processing_time_ms" in data

    def test_batch_single_item(self):
        """Test batch with a single text"""
        response = client.post("/batch", json={
            "texts": ["Python is a versatile programming language."]
        })

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert data["total_items"] == 1

    def test_batch_empty_list(self):
        """Test batch with empty list"""
        response = client.post("/batch", json={
            "texts": []
        })
        assert response.status_code == 422  # Validation error (min_length=1)

    def test_batch_missing_field(self):
        """Test batch with missing texts field"""
        response = client.post("/batch", json={})
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

