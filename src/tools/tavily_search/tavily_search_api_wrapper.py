import json
from typing import Dict, List, Optional

import aiohttp
import requests
from langchain_community.utilities.tavily_search import TAVILY_API_URL
from langchain_community.utilities.tavily_search import (
    TavilySearchAPIWrapper as OriginalTavilySearchAPIWrapper,
)


class EnhancedTavilySearchAPIWrapper(OriginalTavilySearchAPIWrapper):
    def raw_results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        logger.debug(f"TavilyAPI: Preparing request parameters for query: '{query}'")
        
        params = {
            "api_key": self.tavily_api_key.get_secret_value(),
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
        }
        
        logger.debug(f"TavilyAPI: Sending POST request to {TAVILY_API_URL}/search")
        start_time = time.time()
        
        response = requests.post(
            # type: ignore
            f"{TAVILY_API_URL}/search",
            json=params,
        )
        
        request_time = time.time() - start_time
        logger.debug(f"TavilyAPI: Request completed in {request_time:.3f} seconds with status code {response.status_code}")
        
        response.raise_for_status()
        result = response.json()
        
        logger.debug(f"TavilyAPI: Successfully parsed JSON response")
        return result

    async def raw_results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        """Get results from the Tavily Search API asynchronously."""
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        logger.debug(f"TavilyAPI (async): Preparing request parameters for query: '{query}'")

        # Function to perform the API call
        async def fetch() -> str:
            params = {
                "api_key": self.tavily_api_key.get_secret_value(),
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_domains": include_domains,
                "exclude_domains": exclude_domains,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "include_images": include_images,
                "include_image_descriptions": include_image_descriptions,
            }
            
            logger.debug(f"TavilyAPI (async): Creating aiohttp session")
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                logger.debug(f"TavilyAPI (async): Sending POST request to {TAVILY_API_URL}/search")
                async with session.post(f"{TAVILY_API_URL}/search", json=params) as res:
                    request_time = time.time() - start_time
                    logger.debug(f"TavilyAPI (async): Request completed in {request_time:.3f} seconds with status code {res.status}")
                    
                    if res.status == 200:
                        logger.debug(f"TavilyAPI (async): Reading response text")
                        data = await res.text()
                        return data
                    else:
                        error_msg = f"Error {res.status}: {res.reason}"
                        logger.error(f"TavilyAPI (async): {error_msg}")
                        raise Exception(error_msg)

        logger.debug(f"TavilyAPI (async): Executing fetch operation")
        start_time = time.time()
        results_json_str = await fetch()
        fetch_time = time.time() - start_time
        logger.debug(f"TavilyAPI (async): Fetch completed in {fetch_time:.3f} seconds")
        
        logger.debug(f"TavilyAPI (async): Parsing JSON response")
        result = json.loads(results_json_str)
        logger.debug(f"TavilyAPI (async): Successfully parsed JSON response")
        
        return result

    def clean_results_with_images(
        self, raw_results: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """Clean results from Tavily Search API."""
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        logger.debug("TavilyAPI: Starting to clean and process search results")
        start_time = time.time()
        
        # Process page results
        results = raw_results["results"]
        logger.debug(f"TavilyAPI: Processing {len(results)} page results")
        
        clean_results = []
        for i, result in enumerate(results):
            clean_result = {
                "type": "page",
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "score": result["score"],
            }
            if raw_content := result.get("raw_content"):
                clean_result["raw_content"] = raw_content
            clean_results.append(clean_result)
            
        # Process image results if available
        images = raw_results.get("images", [])
        if images:
            logger.debug(f"TavilyAPI: Processing {len(images)} image results")
            for image in images:
                clean_result = {
                    "type": "image",
                    "image_url": image["url"],
                    "image_description": image["description"],
                }
                clean_results.append(clean_result)
        else:
            logger.debug("TavilyAPI: No image results to process")
            
        processing_time = time.time() - start_time
        logger.debug(f"TavilyAPI: Results cleaning completed in {processing_time:.3f} seconds")
        logger.debug(f"TavilyAPI: Returning {len(clean_results)} total results (pages + images)")
        
        return clean_results


if __name__ == "__main__":
    wrapper = EnhancedTavilySearchAPIWrapper()
    results = wrapper.raw_results("cute panda", include_images=True)
    print(json.dumps(results, indent=2, ensure_ascii=False))
