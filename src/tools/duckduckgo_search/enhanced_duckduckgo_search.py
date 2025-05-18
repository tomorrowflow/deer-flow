# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import time
from typing import Dict, List, Optional, Any, Union

from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_community.tools import DuckDuckGoSearchResults

logger = logging.getLogger(__name__)


class EnhancedDuckDuckGoSearchResults(DuckDuckGoSearchResults):
    """Enhanced DuckDuckGo search tool with detailed internal logging."""

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> tuple[Union[List[dict], str], List[dict]]:
        """Run DuckDuckGo search with detailed logging."""
        logger.info(f"DuckDuckGoSearch: Starting search for query: '{query}'")
        
        try:
            # Safely access attributes with getattr to prevent AttributeError
            max_results = getattr(self, "max_results", 10)
            backend = getattr(self, "backend", "text")
            
            logger.info(f"DuckDuckGoSearch: Using parameters - max_results: {max_results}, backend: {backend}")
            
            # Measure API call time
            start_time = time.time()
            
            # Get search results
            logger.info(f"DuckDuckGoSearch: Calling DuckDuckGo API")
            raw_results = self.api_wrapper.results(
                query,
                max_results,
                source=backend
            )
            
            api_time = time.time() - start_time
            logger.info(f"DuckDuckGoSearch: API call completed in {api_time:.3f} seconds")
            
            # Log number of results
            logger.info(f"DuckDuckGoSearch: Received {len(raw_results)} search results")
            
            # Process results
            logger.info("DuckDuckGoSearch: Processing and formatting results")
            start_processing_time = time.time()
            
            # Filter results based on keys_to_include
            keys_to_include = getattr(self, "keys_to_include", None)
            results = [
                {
                    k: v
                    for k, v in d.items()
                    if not keys_to_include or k in keys_to_include
                }
                for d in raw_results
            ]
            
            output_format = getattr(self, "output_format", "string")
            results_separator = getattr(self, "results_separator", ", ")
            
            if output_format == "list":
                processed_results = results
            elif output_format == "json":
                processed_results = json.dumps(results)
            elif output_format == "string":
                res_strs = [", ".join([f"{k}: {v}" for k, v in d.items()]) for d in results]
                processed_results = results_separator.join(res_strs)
            else:
                raise ValueError(
                    f"Invalid output_format: {output_format}. "
                    "Needs to be one of 'string', 'json', 'list'."
                )
                
            processing_time = time.time() - start_processing_time
            logger.info(f"DuckDuckGoSearch: Results processed in {processing_time:.3f} seconds")
            
            return processed_results, raw_results
            
        except Exception as e:
            logger.error(f"DuckDuckGoSearch: Search failed with error: {repr(e)}")
            raise

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> tuple[Union[List[dict], str], List[dict]]:
        """Run DuckDuckGo search asynchronously with detailed logging."""
        logger.info(f"DuckDuckGoSearch (async): Starting search for query: '{query}'")
        logger.info(f"DuckDuckGoSearch (async): Note - Using synchronous implementation as async is not natively supported")
        
        # Call the synchronous implementation
        # We need to handle the run_manager type mismatch by passing None
        return self._run(query, None)


if __name__ == "__main__":
    search = EnhancedDuckDuckGoSearchResults(num_results=3)
    results = search.invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))