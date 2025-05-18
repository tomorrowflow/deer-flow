# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import time
from typing import Dict, List, Optional, Any

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_community.tools import BraveSearch
from langchain_community.utilities import BraveSearchWrapper

logger = logging.getLogger(__name__)


class EnhancedBraveSearchWrapper(BraveSearchWrapper):
    """Enhanced Brave Search API wrapper with detailed logging."""
    
    def run(self, query: str, count: Optional[int] = None, **kwargs: Any) -> List[Dict]:
        """Run Brave search with detailed logging."""
        logger.debug(f"BraveAPI: Preparing request for query: '{query}'")
        
        # Get the count from search_kwargs if not provided directly
        search_kwargs = getattr(self, "search_kwargs", {}) or {}
        default_count = search_kwargs.get("count", 10)
        actual_count = count if count is not None else default_count
        
        # Log search parameters
        logger.debug(f"BraveAPI: Using parameters - count: {actual_count}, kwargs: {kwargs}")
        
        # Measure API call time
        start_time = time.time()
        
        try:
            # Call the API
            logger.debug(f"BraveAPI: Sending request to Brave Search API")
            # Don't pass count to super().run() as it doesn't accept it
            results = super().run(query, **kwargs)
            
            api_time = time.time() - start_time
            logger.debug(f"BraveAPI: Request completed in {api_time:.3f} seconds")
            
            # Log results
            logger.debug(f"BraveAPI: Received {len(results)} search results")
            
            return results
            
        except Exception as e:
            logger.error(f"BraveAPI: Request failed with error: {repr(e)}")
            raise


class EnhancedBraveSearch(BraveSearch):
    """Enhanced Brave search tool with detailed internal logging."""

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Dict]:
        """Run Brave search with detailed logging."""
        logger.info(f"BraveSearch: Starting search for query: '{query}'")
        
        try:
            # Ensure we're using our enhanced wrapper
            if not isinstance(self.search_wrapper, EnhancedBraveSearchWrapper):
                logger.warning("BraveSearch: Not using EnhancedBraveSearchWrapper, logging will be limited")
            
            # Measure execution time
            start_time = time.time()
            
            # Get search results
            logger.info(f"BraveSearch: Calling Brave Search API")
            
            # Check if the wrapper is our enhanced version that supports count
            if isinstance(self.search_wrapper, EnhancedBraveSearchWrapper):
                # Pass count parameter to control number of results
                results = self.search_wrapper.run(query, count=getattr(self, 'k', 10))
            else:
                # Fall back to standard behavior
                results = self.search_wrapper.run(query)
            
            api_time = time.time() - start_time
            logger.info(f"BraveSearch: API call completed in {api_time:.3f} seconds")
            
            # Log number of results
            logger.info(f"BraveSearch: Received {len(results)} search results")
            
            # Process results
            logger.info("BraveSearch: Processing results")
            start_processing_time = time.time()
            
            # Extract the most relevant results
            processed_results = []
            for result in results:
                processed_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("url", ""),
                    "snippet": result.get("description", ""),
                })
                
            processing_time = time.time() - start_processing_time
            logger.info(f"BraveSearch: Results processed in {processing_time:.3f} seconds")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"BraveSearch: Search failed with error: {repr(e)}")
            raise

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> List[Dict]:
        """Run Brave search asynchronously with detailed logging."""
        # Note: BraveSearch doesn't have a native async implementation
        # We're implementing this to maintain consistency with other search tools
        logger.info(f"BraveSearch (async): Starting search for query: '{query}'")
        logger.info(f"BraveSearch (async): Note - Using synchronous implementation as async is not natively supported")
        
        return self._run(query, run_manager)


if __name__ == "__main__":
    import os
    wrapper = EnhancedBraveSearchWrapper(api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""))
    search = EnhancedBraveSearch(search_wrapper=wrapper)
    results = search.invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))