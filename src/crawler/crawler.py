# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import sys
import logging
import os

from .article import Article
from .jina_client import JinaClient
from .crawl4ai_client import Crawl4aiClient
from .readability_extractor import ReadabilityExtractor
from src.config.tools import CRAWLER_TYPE, CRAWL4AI_URL

logger = logging.getLogger(__name__)


class Crawler:
    def crawl(self, url: str) -> Article:
        # To help LLMs better understand content, we extract clean
        # articles from HTML, convert them to markdown, and split
        # them into text and image blocks for one single and unified
        # LLM message.
        #
        # Select the crawler based on configuration
        if CRAWLER_TYPE == "crawl4ai":
            if not CRAWL4AI_URL:
                logger.warning("CRAWL4AI_URL is not set. Falling back to Jina.")
                client = JinaClient()
            else:
                logger.info(f"Using Crawl4ai client with URL: {CRAWL4AI_URL}")
                client = Crawl4aiClient(CRAWL4AI_URL)
        else:
            # Default to Jina
            logger.info("Using Jina client")
            client = JinaClient()
            
        # Get HTML content from the selected crawler
        html = client.crawl(url, return_format="html")
        
        # Use our readability extractor to process the HTML
        extractor = ReadabilityExtractor()
        article = extractor.extract_article(html)
        article.url = url
        return article


if __name__ == "__main__":
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = "https://fintel.io/zh-hant/s/br/nvdc34"
    crawler = Crawler()
    article = crawler.crawl(url)
    print(article.to_markdown())
