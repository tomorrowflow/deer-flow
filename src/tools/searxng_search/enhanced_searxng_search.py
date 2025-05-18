# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple

import requests
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.tools import BaseTool

from src.tools.decorators import create_logged_tool

logger = logging.getLogger(__name__)


class SearxNGSearchAPIWrapper:
    """Wrapper for the SearxNG Search API."""

    def __init__(self, searxng_base_url: str):
        """Initialize the SearxNG Search API wrapper.
        
        Args:
            searxng_base_url: The base URL of the SearxNG instance.
        """
        self.searxng_base_url = searxng_base_url
        logger.debug(f"SearxNGAPI: Initialized with base URL: {searxng_base_url}")

    def results(self, query: str, **kwargs) -> List[Dict]:
        """Get search results from SearxNG API.
        
        Args:
            query: The search query.
            **kwargs: Additional parameters to pass to the SearxNG API.
        
        Returns:
            A list of dictionaries containing search results.
        """
        logger.debug(f"SearxNGAPI: Preparing request for query: '{query}'")
        
        # Measure API call time
        start_time = time.time()
        
        # Construct the URL with the required format=json parameter
        params = {"q": query, "format": "json"}
        
        # Add any additional parameters from kwargs
        params.update(kwargs)
        
        # Construct full request URL for logging
        request_url = requests.Request('GET', self.searxng_base_url, params=params).prepare().url
        logger.info(f"Making SearxNG request to: {request_url}")
        
        # Initialize response variable to avoid unbound variable errors in exception handlers
        response = None
        
        try:
            # Make the request to SearxNG
            logger.debug(f"SearxNGAPI: Sending request to {self.searxng_base_url}")
            response = requests.get(self.searxng_base_url, params=params)
            
            api_time = time.time() - start_time
            logger.debug(f"SearxNGAPI: Request completed in {api_time:.3f} seconds with status code {response.status_code}")
            logger.info(f"SearxNG request to {self.searxng_base_url} returned status: {response.status_code}")
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the JSON response
            data = response.json()
            logger.debug(f"SearxNGAPI: Successfully parsed JSON response")
            
            # Extract the results
            results = []
            if "results" in data:
                num_results = len(data['results'])
                logger.debug(f"SearxNGAPI: Found {num_results} results")
                logger.info(f"SearxNG request for query '{query}' returned {num_results} results.")
                
                for result in data["results"]:
                    processed_result = {
                        "title": result.get("title", ""),
                        "link": result.get("url", ""),
                        "snippet": result.get("content", ""),
                    }
                    results.append(processed_result)
            else:
                logger.warning("SearxNGAPI: No results found in the response")
            
            return results
            
        except requests.exceptions.HTTPError as e:
            if response:
                logger.error(f"SearxNG request failed with status {response.status_code}: {response.text}")
            logger.error(f"SearxNGAPI: Request failed with error: {repr(e)}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during SearxNG request: {e}")
            logger.error(f"SearxNGAPI: Request failed with error: {repr(e)}")
            raise
        except json.JSONDecodeError as e:
            if response:
                logger.error(f"Failed to decode JSON from SearxNG response. Error: {e}. Response text: {response.text[:500]}")
            logger.error(f"SearxNGAPI: Failed to parse JSON response: {repr(e)}")
            raise
        except Exception as e:
            logger.error(f"SearxNGAPI: Unexpected error: {repr(e)}")
            raise


def get_searxng_search_tool(config) -> BaseTool:
    """Get a SearxNG search tool.
    
    Args:
        config: The configuration object containing the SEARXNG_BASE_URL.
        
    Returns:
        A BaseTool for searching with SearxNG.
    """
    searxng_base_url = os.getenv("SEARXNG_BASE_URL", "")
    
    if not searxng_base_url:
        raise ValueError("SEARXNG_BASE_URL environment variable is not set")
    
    # Create the SearxNG search wrapper
    search_wrapper = SearxNGSearchAPIWrapper(searxng_base_url=searxng_base_url)
    
    # Create a BaseTool class for SearxNG search
    class SearxNGSearchTool(BaseTool):
        name: str = "searxng_search"
        description: str = "A wrapper around SearxNG. Useful for when you need to answer questions about current events. Input should be a search query."
        
        def _extract_query_and_kwargs(self, tool_kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
            """Extract query string and additional kwargs from tool input.
            
            Handles three primary input formats:
            1. {'args': {'query': 'actual_query', 'param1': 'val1'}, ...}
            2. {'query': 'actual_query', 'param1': 'val1', ...}
            3. {'args': ['query_string', ...], ...}
            
            Args:
                tool_kwargs: The input kwargs dictionary
                
            Returns:
                Tuple of (query_string, api_call_kwargs)
                
            Raises:
                ValueError: If query cannot be extracted from input
            """
            query_str: str = ""
            api_call_kwargs: Dict[str, Any] = {}
            tool_args = tool_kwargs.get("args")
            tool_direct_kwargs = tool_kwargs.get("kwargs", {})
    
            if isinstance(tool_args, dict):  # Case 1: args is a dict {'query': '...', ...}
                if "query" in tool_args:
                    query_str = str(tool_args["query"])
                    # Capture other items in args_dict as potential API params
                    api_call_kwargs.update({k: v for k, v in tool_args.items() if k != "query"})
                else:
                    logger.error(f"Missing 'query' in 'args' dictionary: {tool_args}")
                    raise ValueError("Missing 'query' in 'args' dictionary.")
            elif isinstance(tool_args, (list, tuple)) and tool_args:  # Case 3: args is a list/tuple ['query_string', ...]
                query_str = str(tool_args[0])
                # If there are other positional args, they are not typically used for API kwargs directly
                # If kwargs were also passed (e.g. tool_kwargs['kwargs']), merge them.
                if isinstance(tool_direct_kwargs, dict):
                    api_call_kwargs.update(tool_direct_kwargs)
            elif "query" in tool_kwargs:  # Case 2: query is a direct key in tool_kwargs
                query_str = str(tool_kwargs["query"])
                # Capture other items in tool_kwargs as potential API params
                api_call_kwargs.update({k: v for k, v in tool_kwargs.items() if k != "query"})
            else:
                logger.error(f"Could not extract 'query' from tool input: {tool_kwargs}")
                raise ValueError(f"Could not extract 'query' from tool input: {tool_kwargs}")
    
            # Reset api_call_kwargs and rebuild based on where query was found or if a 'kwargs' key exists
            extracted_api_kwargs = {}
            if isinstance(tool_args, dict):
                extracted_api_kwargs = {k: v for k, v in tool_args.items() if k != "query"}
            elif "query" in tool_kwargs:  # query was a direct key
                extracted_api_kwargs = {k: v for k, v in tool_kwargs.items() if k != "query" and k not in ["args", "kwargs"]}
    
            # Explicitly merge from top-level 'kwargs' if it exists
            if isinstance(tool_direct_kwargs, dict):
                extracted_api_kwargs.update(tool_direct_kwargs)
            
            api_call_kwargs = extracted_api_kwargs
    
            if not query_str:
                logger.error(f"Could not extract 'query' from tool input: {tool_kwargs}")
                raise ValueError(f"Could not extract 'query' from tool input: {tool_kwargs}")
                
            logger.debug(f"Extracted query: '{query_str}', api_call_kwargs: {api_call_kwargs} from tool_kwargs: {tool_kwargs}")
            return query_str, api_call_kwargs
        
        def _run(self, **tool_kwargs: Any) -> str:
            """Run the SearxNG search tool.
            
            Args:
                **tool_kwargs: Keyword arguments that may contain query directly or in args dict
                
            Returns:
                JSON string of search results or error message
            """
            try:
                query, api_call_kwargs = self._extract_query_and_kwargs(tool_kwargs)
                logger.info(f"Executing SearxNG search with query: '{query}' and kwargs: {api_call_kwargs}")
                
                raw_results = search_wrapper.results(query=query, **api_call_kwargs)
                
                serializable_results: list
                if isinstance(raw_results, list):
                    # Just use the raw results directly - they should already be serializable
                    # If they're not, json.dumps will handle the error
                    serializable_results = raw_results
                elif isinstance(raw_results, dict) and 'results' in raw_results and isinstance(raw_results['results'], list):
                    serializable_results = raw_results['results']
                else:
                    logger.warning(f"Unexpected result type from api_wrapper in _run: {type(raw_results)}. Content: {str(raw_results)[:200]}. Returning empty list.")
                    serializable_results = []
                    
                return json.dumps(serializable_results)
            except ValueError as ve:
                logger.error(f"ValueError in SearxNGTool _run during argument extraction: {ve} for input {tool_kwargs}")
                return json.dumps({"error": True, "message": f"Argument extraction failed: {str(ve)}"})
            except Exception as e:
                logger.error(f"Exception in SearxNGTool _run: {e} for input {tool_kwargs}", exc_info=True)
                return json.dumps({"error": True, "message": f"An unexpected error occurred: {str(e)}"})
            
        async def _arun(self, **tool_kwargs: Any) -> str:
            """Run the SearxNG search tool asynchronously.
            
            Args:
                **tool_kwargs: Keyword arguments that may contain query directly or in args dict
                
            Returns:
                JSON string of search results or error message
            """
            try:
                query, api_call_kwargs = self._extract_query_and_kwargs(tool_kwargs)
                logger.info(f"Executing async SearxNG search with query: '{query}' and kwargs: {api_call_kwargs}")
                
                raw_results = await asyncio.to_thread(search_wrapper.results, query=query, **api_call_kwargs)
                
                serializable_results: list
                if isinstance(raw_results, list):
                    # Just use the raw results directly - they should already be serializable
                    # If they're not, json.dumps will handle the error
                    serializable_results = raw_results
                elif isinstance(raw_results, dict) and 'results' in raw_results and isinstance(raw_results['results'], list):
                    serializable_results = raw_results['results']
                else:
                    logger.warning(f"Unexpected result type from api_wrapper in _arun: {type(raw_results)}. Content: {str(raw_results)[:200]}. Returning empty list.")
                    serializable_results = []
                    
                return json.dumps(serializable_results)
            except ValueError as ve:
                logger.error(f"ValueError in SearxNGTool _arun during argument extraction: {ve} for input {tool_kwargs}")
                return json.dumps({"error": True, "message": f"Argument extraction failed: {str(ve)}"})
            except Exception as e:
                logger.error(f"Exception in SearxNGTool _arun: {e} for input {tool_kwargs}", exc_info=True)
                return json.dumps({"error": True, "message": f"An unexpected error occurred: {str(e)}"})
    
    # Create and return the logged tool
    LoggedSearxNGSearchTool = create_logged_tool(SearxNGSearchTool)
    return LoggedSearxNGSearchTool(name="searxng_search")


if __name__ == "__main__":
    # Test the SearxNG search tool
    searxng_base_url = os.getenv("SEARXNG_BASE_URL", "")
    wrapper = SearxNGSearchAPIWrapper(searxng_base_url=searxng_base_url)
    search_tool = get_searxng_search_tool(None)
    results = search_tool.invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))