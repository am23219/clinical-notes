import json
import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# TODO: Replace with Langfuse for better observability once we're out of MVP

def track_llm_request(
    model: str, 
    prompt_tokens: int, 
    completion_tokens: int, 
    latency_ms: float,
    metadata: Optional[Dict[str, Any]] = None
):
    # Track LLM usage for cost and performance monitoring
    metrics = {
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_ms": latency_ms,
        "timestamp": time.time(),
    }
    
    if metadata:
        metrics.update(metadata)
    
    # Just log for now - will add proper analytics later
    logger.info(f"LLM Request: {json.dumps(metrics)}")

def track_processing_time(func: Callable) -> Callable:
    # Simple decorator to measure how long our API endpoints take
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} took {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    
    return wrapper 