# Test script to verify the fix for the TypeError in EnhancedBraveSearchWrapper
from src.tools.brave_search.enhanced_brave_search import EnhancedBraveSearchWrapper, EnhancedBraveSearch
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def test_enhanced_brave_search_wrapper():
    print("Testing EnhancedBraveSearchWrapper...")
    
    # Test with default parameters
    print("\nTesting with default parameters...")
    wrapper = EnhancedBraveSearchWrapper(api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""))
    results = wrapper.run("test query")
    print(f"Got results using default count")
    
    # Test with search_kwargs
    print("\nTesting with search_kwargs...")
    wrapper = EnhancedBraveSearchWrapper(
        api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
        search_kwargs={"count": 5}
    )
    results = wrapper.run("test query")
    print(f"Got results using count from search_kwargs")
    
    # Test with explicit count parameter
    print("\nTesting with explicit count parameter...")
    results = wrapper.run("test query", count=3)
    print(f"Got results using explicit count parameter")
    
    # Test with additional kwargs
    print("\nTesting with additional kwargs...")
    results = wrapper.run("test query", count=3, country="US")
    print(f"Got results using count and additional kwargs")
    
    print("EnhancedBraveSearchWrapper tests passed!")

def test_enhanced_brave_search():
    print("\nTesting EnhancedBraveSearch...")
    
    # Test with default wrapper
    wrapper = EnhancedBraveSearchWrapper(api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""))
    search = EnhancedBraveSearch(search_wrapper=wrapper)
    
    # Test invoke method
    print("\nTesting invoke method...")
    results = search.invoke("test query")
    print(f"Got results from invoke method")
    
    # Test with wrapper that has search_kwargs
    wrapper_with_kwargs = EnhancedBraveSearchWrapper(
        api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
        search_kwargs={"count": 5}
    )
    search_with_kwargs = EnhancedBraveSearch(search_wrapper=wrapper_with_kwargs)
    
    # Test invoke method with search_kwargs
    print("\nTesting invoke method with search_kwargs...")
    results = search_with_kwargs.invoke("test query")
    print(f"Got results from invoke method with search_kwargs")
    
    print("EnhancedBraveSearch tests passed!")

if __name__ == "__main__":
    print("Running tests for the fixed EnhancedBraveSearchWrapper and EnhancedBraveSearch...")
    test_enhanced_brave_search_wrapper()
    test_enhanced_brave_search()
    print("\nAll tests passed! The fix works correctly.")