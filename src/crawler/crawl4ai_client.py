# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import requests
import json

logger = logging.getLogger(__name__)


class Crawl4aiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        logger.info(f"Initialized Crawl4aiClient with base URL: {base_url}")

    def crawl(self, url: str, return_format: str = "text", **kwargs) -> str:
        """
        Crawl a URL using the crawl4ai service.
        
        Args:
            url: The URL to crawl
            return_format: The desired return format (text or html)
            **kwargs: Additional parameters to pass to the crawl4ai service
            
        Returns:
            The crawled content as a string
        """
        headers = {
            "Content-Type": "application/json",
            "X-Return-Format": return_format,  # Add return format header like JinaClient
        }
        
        # Prepare the request payload
        # Format the request payload according to the crawl4ai API requirements
        data = {
            "urls": [url],  # API expects an array of URLs
            "crawler_config": {
                "type": "CrawlerRunConfig",
                "params": {
                    "scraping_strategy": {
                        "type": "WebScrapingStrategy",
                        "params": {}
                    },
                    "exclude_social_media_domains": [
                        "facebook.com",
                        "twitter.com",
                        "x.com",
                        "linkedin.com",
                        "instagram.com",
                        "pinterest.com",
                        "tiktok.com",
                        "snapchat.com",
                        "reddit.com"
                    ]
                }
            },
            "format": return_format,  # Include format in the payload
            "options": {
                "wait_for": ["domcontentloaded", "networkidle0"],  # Wait for page to load completely
                "timeout": 30000  # 30 seconds timeout
            }
        }
        
        # Add any additional parameters from kwargs to the options
        if kwargs:
            data["options"].update(kwargs)
        
        logger.info(f"Making POST request to {self.base_url} for URL: {url} with format: {return_format}")
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            
            # Log the response status code and headers for debugging
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")
            
            # If we get a 422 error, log the response content for debugging
            if response.status_code == 422:
                logger.error(f"422 Unprocessable Entity error. Response content (first 100 chars): {str(response.text)[:100]}...")
                logger.error(f"Request payload: {data}")
                # Try with a simpler payload as a fallback
                logger.info("Attempting fallback with simpler payload...")
                fallback_data = {"urls": [url]}
                fallback_response = requests.post(self.base_url, headers=headers, json=fallback_data)
                if fallback_response.status_code == 200:
                    logger.info("Fallback request succeeded!")
                    response = fallback_response
                else:
                    logger.error(f"Fallback request failed with status code: {fallback_response.status_code}")
                    logger.error(f"Fallback response content (first 100 chars): {str(fallback_response.text)[:100]}...")
                    raise RuntimeError(f"422 Unprocessable Entity error from crawl4ai: {response.text}")
            
            # Check if the request was successful
            response.raise_for_status()
            
            logger.info(f"Successfully received response from crawl4ai for URL: {url}")
            
            # Try to parse the response as JSON
            try:
                json_response = response.json()
                logger.info(f"Response structure (first 100 chars): {json.dumps(json_response)[:100]}...")
                
                # Handle response for multiple URLs (API might return an array or object with URL keys)
                if isinstance(json_response, dict):
                    # If the response is for a single URL or has a content field directly
                    if "content" in json_response:
                        return json_response["content"]
                    # If the response contains results for each URL
                    elif "results" in json_response and isinstance(json_response["results"], dict):
                        # Try to get the result for our specific URL
                        if url in json_response["results"]:
                            result = json_response["results"][url]
                            if isinstance(result, dict) and "content" in result:
                                return result["content"]
                            return json.dumps(result)
                        # If URL not found in results, return the first result's content if available
                        elif json_response["results"] and len(json_response["results"]) > 0:
                            first_url = list(json_response["results"].keys())[0]
                            first_result = json_response["results"][first_url]
                            if isinstance(first_result, dict) and "content" in first_result:
                                return first_result["content"]
                            return json.dumps(first_result)
                    # If the response has a different structure, return the entire JSON
                    return json.dumps(json_response)
                # If the response is an array, return the first item's content if available
                elif isinstance(json_response, list) and len(json_response) > 0:
                    first_item = json_response[0]
                    if isinstance(first_item, dict) and "content" in first_item:
                        return first_item["content"]
                    return json.dumps(first_item)
                else:
                    # If there's no recognizable structure, return the entire JSON response as a string
                    return json.dumps(json_response)
            except json.JSONDecodeError:
                # If the response is not JSON, return the raw text
                logger.info("Response is not JSON, returning raw text")
                return response.text
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to crawl4ai: {str(e)}"
            logger.error(error_msg)
            
            # Try with a simpler payload as a fallback for connection errors
            try:
                logger.info("Attempting fallback with simpler payload after connection error...")
                fallback_data = {"urls": [url]}
                fallback_headers = {"Content-Type": "application/json"}
                fallback_response = requests.post(self.base_url, headers=fallback_headers, json=fallback_data)
                if fallback_response.status_code == 200:
                    logger.info("Fallback request succeeded!")
                    try:
                        json_response = fallback_response.json()
                        logger.info(f"Fallback response structure (first 100 chars): {json.dumps(json_response)[:100]}...")
                        
                        # Handle fallback response for multiple URLs (similar logic as above)
                        if isinstance(json_response, dict):
                            if "content" in json_response:
                                return json_response["content"]
                            elif "results" in json_response and isinstance(json_response["results"], dict):
                                if url in json_response["results"]:
                                    result = json_response["results"][url]
                                    if isinstance(result, dict) and "content" in result:
                                        return result["content"]
                                    return json.dumps(result)
                                elif json_response["results"] and len(json_response["results"]) > 0:
                                    first_url = list(json_response["results"].keys())[0]
                                    first_result = json_response["results"][first_url]
                                    if isinstance(first_result, dict) and "content" in first_result:
                                        return first_result["content"]
                                    return json.dumps(first_result)
                            return json.dumps(json_response)
                        elif isinstance(json_response, list) and len(json_response) > 0:
                            first_item = json_response[0]
                            if isinstance(first_item, dict) and "content" in first_item:
                                return first_item["content"]
                            return json.dumps(first_item)
                        else:
                            return json.dumps(json_response)
                    except json.JSONDecodeError:
                        return fallback_response.text
                else:
                    logger.error(f"Fallback request failed with status code: {fallback_response.status_code}")
            except requests.exceptions.RequestException as fallback_error:
                logger.error(f"Fallback request also failed: {str(fallback_error)}")
            
            raise RuntimeError(error_msg)