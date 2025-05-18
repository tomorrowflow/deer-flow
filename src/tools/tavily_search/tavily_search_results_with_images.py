import json
from typing import Dict, List, Optional, Tuple, Union

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from pydantic import Field

from src.tools.tavily_search.tavily_search_api_wrapper import (
    EnhancedTavilySearchAPIWrapper,
)


class TavilySearchResultsWithImages(TavilySearchResults):  # type: ignore[override, override]
    """Tool that queries the Tavily Search API and gets back json.

    Setup:
        Install ``langchain-openai`` and ``tavily-python``, and set environment variable ``TAVILY_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-community tavily-python
            export TAVILY_API_KEY="your-api-key"

    Instantiate:

        .. code-block:: python

            from langchain_community.tools import TavilySearchResults

            tool = TavilySearchResults(
                max_results=5,
                include_answer=True,
                include_raw_content=True,
                include_images=True,
                include_image_descriptions=True,
                # search_depth="advanced",
                # include_domains = []
                # exclude_domains = []
            )

    Invoke directly with args:

        .. code-block:: python

            tool.invoke({'query': 'who won the last french open'})

        .. code-block:: json

            {
                "url": "https://www.nytimes.com...",
                "content": "Novak Djokovic won the last French Open by beating Casper Ruud ..."
            }

    Invoke with tool call:

        .. code-block:: python

            tool.invoke({"args": {'query': 'who won the last french open'}, "type": "tool_call", "id": "foo", "name": "tavily"})

        .. code-block:: python

            ToolMessage(
                content='{ "url": "https://www.nytimes.com...", "content": "Novak Djokovic won the last French Open by beating Casper Ruud ..." }',
                artifact={
                    'query': 'who won the last french open',
                    'follow_up_questions': None,
                    'answer': 'Novak ...',
                    'images': [
                        'https://www.amny.com/wp-content/uploads/2023/06/AP23162622181176-1200x800.jpg',
                        ...
                        ],
                    'results': [
                        {
                            'title': 'Djokovic ...',
                            'url': 'https://www.nytimes.com...',
                            'content': "Novak...",
                            'score': 0.99505633,
                            'raw_content': 'Tennis\nNovak ...'
                        },
                        ...
                    ],
                    'response_time': 2.92
                },
                tool_call_id='1',
                name='tavily_search_results_json',
            )

    """  # noqa: E501

    include_image_descriptions: bool = False
    """Include a image descriptions in the response.

    Default is False.
    """

    api_wrapper: EnhancedTavilySearchAPIWrapper = Field(default_factory=EnhancedTavilySearchAPIWrapper)  # type: ignore[arg-type]

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[Union[List[Dict[str, str]], str], Dict]:
        """Use the tool."""
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        logger.info(f"TavilySearch: Starting search for query: '{query}'")
        
        # TODO: remove try/except, should be handled by BaseTool
        try:
            logger.info(f"TavilySearch: Calling Tavily API with query: '{query}', max_results: {self.max_results}")
            start_time = time.time()
            
            raw_results = self.api_wrapper.raw_results(
                query,
                self.max_results,
                self.search_depth,
                self.include_domains,
                self.exclude_domains,
                self.include_answer,
                self.include_raw_content,
                self.include_images,
                self.include_image_descriptions,
            )
            
            api_time = time.time() - start_time
            logger.info(f"TavilySearch: API call completed in {api_time:.3f} seconds")
            
            if "results" in raw_results:
                logger.info(f"TavilySearch: Received {len(raw_results['results'])} search results")
            if "images" in raw_results and raw_results["images"]:
                logger.info(f"TavilySearch: Received {len(raw_results['images'])} images")
                
        except Exception as e:
            logger.error(f"TavilySearch: API call failed with error: {repr(e)}")
            return repr(e), {}
            
        logger.info("TavilySearch: Processing and cleaning results")
        start_time = time.time()
        cleaned_results = self.api_wrapper.clean_results_with_images(raw_results)
        processing_time = time.time() - start_time
        logger.info(f"TavilySearch: Results processed in {processing_time:.3f} seconds")
        
        print("sync", json.dumps(cleaned_results, indent=2, ensure_ascii=False))
        return cleaned_results, raw_results

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[Union[List[Dict[str, str]], str], Dict]:
        """Use the tool asynchronously."""
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        logger.info(f"TavilySearch (async): Starting search for query: '{query}'")
        
        try:
            logger.info(f"TavilySearch (async): Calling Tavily API with query: '{query}', max_results: {self.max_results}")
            start_time = time.time()
            
            raw_results = await self.api_wrapper.raw_results_async(
                query,
                self.max_results,
                self.search_depth,
                self.include_domains,
                self.exclude_domains,
                self.include_answer,
                self.include_raw_content,
                self.include_images,
                self.include_image_descriptions,
            )
            
            api_time = time.time() - start_time
            logger.info(f"TavilySearch (async): API call completed in {api_time:.3f} seconds")
            
            if "results" in raw_results:
                logger.info(f"TavilySearch (async): Received {len(raw_results['results'])} search results")
            if "images" in raw_results and raw_results["images"]:
                logger.info(f"TavilySearch (async): Received {len(raw_results['images'])} images")
                
        except Exception as e:
            logger.error(f"TavilySearch (async): API call failed with error: {repr(e)}")
            return repr(e), {}
            
        logger.info("TavilySearch (async): Processing and cleaning results")
        start_time = time.time()
        cleaned_results = self.api_wrapper.clean_results_with_images(raw_results)
        processing_time = time.time() - start_time
        logger.info(f"TavilySearch (async): Results processed in {processing_time:.3f} seconds")
        
        print("async", json.dumps(cleaned_results, indent=2, ensure_ascii=False))
        return cleaned_results, raw_results
