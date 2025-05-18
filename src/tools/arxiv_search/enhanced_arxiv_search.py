# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import time
from typing import Dict, List, Optional, Any

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper

logger = logging.getLogger(__name__)


class EnhancedArxivAPIWrapper(ArxivAPIWrapper):
    """Enhanced Arxiv API wrapper with detailed logging."""
    
    def run(self, query: str) -> str:
        """Run Arxiv search with detailed logging."""
        logger.debug(f"ArxivAPI: Preparing request for query: '{query}'")
        
        # Log search parameters
        logger.debug(f"ArxivAPI: Using parameters - top_k_results: {self.top_k_results}, load_max_docs: {self.load_max_docs}, load_all_available_meta: {self.load_all_available_meta}")
        
        # Measure API call time
        start_time = time.time()
        
        try:
            # Call the API
            logger.debug(f"ArxivAPI: Sending request to Arxiv API")
            results = super().run(query)
            
            api_time = time.time() - start_time
            logger.debug(f"ArxivAPI: Request completed in {api_time:.3f} seconds")
            
            # Log results size
            logger.debug(f"ArxivAPI: Received response of length {len(results)} characters")
            
            return results
            
        except Exception as e:
            logger.error(f"ArxivAPI: Request failed with error: {repr(e)}")
            raise
    
    def load(self, query: str) -> List[Dict]:
        """Load raw data from Arxiv with detailed logging."""
        logger.debug(f"ArxivAPI: Loading raw data for query: '{query}'")
        
        # Measure API call time
        start_time = time.time()
        
        try:
            # Call the API
            logger.debug(f"ArxivAPI: Fetching papers from Arxiv")
            docs = super().load(query)
            
            api_time = time.time() - start_time
            logger.debug(f"ArxivAPI: Data loading completed in {api_time:.3f} seconds")
            
            # Log results
            logger.debug(f"ArxivAPI: Loaded {len(docs)} papers")
            
            return docs
            
        except Exception as e:
            logger.error(f"ArxivAPI: Data loading failed with error: {repr(e)}")
            raise


class EnhancedArxivQueryRun(ArxivQueryRun):
    """Enhanced Arxiv search tool with detailed internal logging."""

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run Arxiv search with detailed logging."""
        logger.info(f"ArxivSearch: Starting search for query: '{query}'")
        
        try:
            # Ensure we're using our enhanced wrapper
            if not isinstance(self.api_wrapper, EnhancedArxivAPIWrapper):
                logger.warning("ArxivSearch: Not using EnhancedArxivAPIWrapper, logging will be limited")
            
            # Measure execution time
            start_time = time.time()
            
            # Get search results
            logger.info(f"ArxivSearch: Calling Arxiv API")
            results = self.api_wrapper.run(query)
            
            api_time = time.time() - start_time
            logger.info(f"ArxivSearch: API call completed in {api_time:.3f} seconds")
            
            # Log results size
            logger.info(f"ArxivSearch: Received response of length {len(results)} characters")
            
            return results
            
        except Exception as e:
            logger.error(f"ArxivSearch: Search failed with error: {repr(e)}")
            raise

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run Arxiv search asynchronously with detailed logging."""
        # Note: ArxivQueryRun doesn't have a native async implementation
        # We're implementing this to maintain consistency with other search tools
        logger.info(f"ArxivSearch (async): Starting search for query: '{query}'")
        logger.info(f"ArxivSearch (async): Note - Using synchronous implementation as async is not natively supported")
        
        return self._run(query, run_manager)


if __name__ == "__main__":
    wrapper = EnhancedArxivAPIWrapper(top_k_results=3, load_max_docs=3)
    search = EnhancedArxivQueryRun(api_wrapper=wrapper)
    results = search.invoke("quantum computing")
    print(results)