# Simple test script to verify the EnhancedBraveSearchWrapper class
from src.tools.brave_search.enhanced_brave_search import EnhancedBraveSearchWrapper
import os

# Just initialize the wrapper to verify it loads correctly
print("Initializing EnhancedBraveSearchWrapper...")
wrapper = EnhancedBraveSearchWrapper(api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""))
print("Initialization successful!")

# Print the method we're using
print(f"The wrapper has a 'run' method: {hasattr(wrapper, 'run')}")