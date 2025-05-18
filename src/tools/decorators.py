# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import functools
import inspect
import time
from typing import Any, Callable, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def log_io(func: Callable) -> Callable:
    """
    A decorator that logs the input parameters, output, and execution time of a tool function.

    Args:
        func: The tool function to be decorated

    Returns:
        The wrapped function with input/output logging and execution time
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        import time
        
        # Log input parameters
        func_name = func.__name__
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.info(f"Tool {func_name} called with parameters: {params}")

        # Execute the function and measure execution time
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        # Log the output and execution time
        # Limit output to 100 characters
        result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        logger.info(f"Tool {func_name} returned: {result_str}")
        logger.info(f"Tool {func_name} execution time: {execution_time:.3f} seconds")

        return result

    return wrapper


class LoggedToolMixin:
    """A mixin class that adds logging functionality to any tool."""

    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Helper method to log tool operations."""
        tool_name = self.__class__.__name__.replace("Logged", "")
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {tool_name}.{method_name} called with parameters: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Override _run method to add logging with execution time."""
        import time
        
        self._log_operation("_run", *args, **kwargs)
        
        # Filter out 'args' from kwargs if it exists
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'args'}
        
        # Execute the method and measure execution time
        start_time = time.time()
        result = super()._run(*args, **filtered_kwargs)
        execution_time = time.time() - start_time
        
        tool_name = self.__class__.__name__.replace('Logged', '')
        # Limit output to 100 characters
        result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        logger.debug(f"Tool {tool_name} returned: {result_str}")
        logger.debug(f"Tool {tool_name} execution time: {execution_time:.3f} seconds")
        
        return result


def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    Factory function to create a logged version of any tool class.

    Args:
        base_tool_class: The original tool class to be enhanced with logging

    Returns:
        A new class that inherits from both LoggedToolMixin and the base tool class
    """

    class LoggedTool(LoggedToolMixin, base_tool_class):
        pass

    # Set a more descriptive name for the class
    LoggedTool.__name__ = f"Logged{base_tool_class.__name__}"
    return LoggedTool


def log_mcp_io(server_name: str) -> Callable:
    """
    A decorator factory that creates a decorator for logging MCP tool calls.
    
    This decorator logs:
    - MCP tool name (derived from the function name)
    - The server_name passed to the factory
    - Input parameters
    - Output/result
    - Execution time
    
    Args:
        server_name: The name of the MCP server
        
    Returns:
        A decorator that logs MCP tool calls
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Log input parameters
            tool_name = func.__name__
            params = ", ".join(
                [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
            )
            logger.info(f"MCP Tool {tool_name} from server '{server_name}' called with parameters: {params}")
            
            # Execute the function and measure execution time
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log the output and execution time
            # Limit output to 100 characters
            result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            logger.info(f"MCP Tool {tool_name} from server '{server_name}' returned: {result_str}")
            logger.info(f"MCP Tool {tool_name} from server '{server_name}' execution time: {execution_time:.3f} seconds")
            
            return result
            
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Log input parameters
            tool_name = func.__name__
            params = ", ".join(
                [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
            )
            logger.info(f"MCP Tool {tool_name} from server '{server_name}' called with parameters: {params}")
            
            # Execute the function and measure execution time
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log the output and execution time
            # Limit output to 100 characters
            result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            logger.info(f"MCP Tool {tool_name} from server '{server_name}' returned: {result_str}")
            logger.info(f"MCP Tool {tool_name} from server '{server_name}' execution time: {execution_time:.3f} seconds")
            
            return result
            
        # Return the appropriate wrapper based on whether the function is async or not
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator
