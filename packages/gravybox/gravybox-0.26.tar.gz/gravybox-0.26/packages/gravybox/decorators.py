import time
import traceback

from gravybox.betterstack import collect_logger
from gravybox.exceptions import GravyboxException
from gravybox.protocol import LinkRequest

logger = collect_logger()


def upstream_api_call(upstream_api_provider, upstream_api_endpoint):
    def decorator(function):
        async def wrapper(*args, link_request: LinkRequest = None, **kwargs):
            if link_request is None:
                raise ValueError("please pass the original link request when making a call to an upstream api")
            log_extras = {
                "upstream_api_provider": upstream_api_provider,
                "upstream_api_endpoint": upstream_api_endpoint,
                "trace_id": link_request.trace_id,
                "args": [arg for arg in args],
                "kwargs": [(key, value) for key, value in kwargs.items()]
            }
            logger.info("( ) calling upstream api", extra=log_extras)
            start_time = time.time()
            try:
                result = await function(*args, **kwargs)
                log_extras["elapsed_time"] = time.time() - start_time
                logger.info("(*) calling upstream api succeeded", extra=log_extras)
                return result
            except Exception as error:
                if isinstance(error, GravyboxException):
                    log_extras |= error.log_extras
                log_extras["error_str"] = str(error)
                log_extras["traceback"] = traceback.format_exc()
                log_extras["elapsed_time"] = time.time() - start_time
                logger.warning("(!) calling upstream api failed", extra=log_extras)
                return None

        return wrapper

    return decorator
