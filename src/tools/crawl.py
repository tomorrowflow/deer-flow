# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import Annotated

from langchain_core.tools import tool
from .decorators import log_io

from src.crawler import Crawler

logger = logging.getLogger(__name__)


@tool
@log_io
def crawl_tool(
    url: Annotated[str, "The url to crawl."],
) -> str:
    """Use this to crawl a url and get a readable content in markdown format."""
    try:
        logger.info(f"Initializing crawler for URL: {url}")
        crawler = Crawler()
        
        logger.info(f"Starting to crawl URL: {url}")
        article = crawler.crawl(url)
        
        logger.info(f"Successfully crawled URL: {url}, converting to markdown")
        markdown_content = article.to_markdown()
        
        logger.info(f"Markdown conversion complete, content length: {len(markdown_content)} characters")
        # Return the full markdown content as a string to match the return type annotation
        return markdown_content
    except BaseException as e:
        error_msg = f"Failed to crawl. Error: {repr(e)}"
        logger.error(error_msg)
        return error_msg
