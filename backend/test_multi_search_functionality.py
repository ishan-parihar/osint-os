#!/usr/bin/env python3
"""
Quick functionality test for multi_search_service.py to ensure our type fixes didn't break anything
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.multi_search_service import MultiSearchEngine, SearchResult, SearchResponse

async def test_multi_search():
    """Test basic functionality of multi_search_service."""
    print("🧪 Testing MultiSearchEngine functionality...")
    
    try:
        # Test instantiation
        engine = MultiSearchEngine()
        print("✅ MultiSearchEngine instantiation successful")
        
        # Test dataclass creation
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            description="Test description",
            source="test",
            relevance_score=0.8
        )
        print("✅ SearchResult creation successful")
        
        response = SearchResponse(
            query="test query",
            results=[result],
            total_results=1,
            search_time=0.5,
            engine="test"
        )
        print("✅ SearchResponse creation successful")
        
        # Test result serialization
        serialized = engine._serialize_result(result)
        print("✅ Result serialization successful")
        print(f"   Serialized keys: {list(serialized.keys())}")
        
        # Test URL normalization
        normalized = engine._normalize_url("https://www.example.com/")
        print("✅ URL normalization successful")
        print(f"   Normalized URL: {normalized}")
        
        # Test relevance calculation
        score = engine._calculate_relevance("Test Title", "Test description", "test")
        print("✅ Relevance calculation successful")
        print(f"   Relevance score: {score:.2f}")
        
        print("\n🎉 All functionality tests passed! Type fixes preserved functionality.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multi_search())
    sys.exit(0 if success else 1)