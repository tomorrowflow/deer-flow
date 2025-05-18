# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper, BraveSearchWrapper

from src.config import SearchEngine, SELECTED_SEARCH_ENGINE
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)

# Import enhanced search tools
from src.tools.duckduckgo_search.enhanced_duckduckgo_search import EnhancedDuckDuckGoSearchResults
from src.tools.brave_search.enhanced_brave_search import EnhancedBraveSearch, EnhancedBraveSearchWrapper
from src.tools.arxiv_search.enhanced_arxiv_search import EnhancedArxivQueryRun, EnhancedArxivAPIWrapper
from src.tools.searxng_search import SearxNGSearchAPIWrapper, get_searxng_search_tool

from src.tools.decorators import create_logged_tool

logger = logging.getLogger(__name__)
# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)
# Use enhanced versions for the other search tools
LoggedDuckDuckGoSearch = create_logged_tool(EnhancedDuckDuckGoSearchResults)
LoggedBraveSearch = create_logged_tool(EnhancedBraveSearch)
LoggedArxivSearch = create_logged_tool(EnhancedArxivQueryRun)
# SearxNG search is handled differently through get_searxng_search_tool



# Get the selected search tool
def get_web_search_tool(max_search_results: int):
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        return LoggedTavilySearch(
            name="web_search",
            max_results=max_search_results,
            include_raw_content=True,
            include_images=True,
            include_image_descriptions=True,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return LoggedDuckDuckGoSearch(name="web_search", num_results=max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=EnhancedBraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
                search_kwargs={"count": max_search_results},
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=EnhancedArxivAPIWrapper(
                top_k_results=max_search_results,
                load_max_docs=max_search_results,
                load_all_available_meta=True,
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.SEARXNG.value:
        # Use the factory function to get the SearxNG search tool
        from src.config import tools as tools_config
        search_tool = get_searxng_search_tool(tools_config)
        search_tool.name = "web_search"  # Override the default name
        return search_tool
    else:
        raise ValueError(f"Unsupported search engine: {SELECTED_SEARCH_ENGINE}")


if __name__ == "__main__":
    # Test each search tool
    print("Testing DuckDuckGo search...")
    results = LoggedDuckDuckGoSearch(
        name="web_search", num_results=3, output_format="list"
    ).invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print("\nTesting Brave search...")
    brave_wrapper = EnhancedBraveSearchWrapper(
        api_key=os.getenv("BRAVE_SEARCH_API_KEY", "")
    )
    results = LoggedBraveSearch(
        name="web_search", search_wrapper=brave_wrapper
    ).invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print("\nTesting Arxiv search...")
    arxiv_wrapper = EnhancedArxivAPIWrapper(top_k_results=3, load_max_docs=3)
    results = LoggedArxivSearch(
        name="web_search", api_wrapper=arxiv_wrapper
    ).invoke("quantum computing")
    print(results)
