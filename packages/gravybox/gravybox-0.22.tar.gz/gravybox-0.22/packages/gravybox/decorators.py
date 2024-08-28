import traceback

from gravybox.betterstack import collect_logger
from gravybox.exceptions import GravyboxException

logger = collect_logger()


def upstream_api_call(upstream_api_name):
    def decorator(function):
        async def wrapper(*args, trace_id=None, **kwargs):
            if trace_id is None:
                raise ValueError("please pass a trace_id to all upstream api calls")
            try:
                result = await function(*args, **kwargs)
                return result
            except Exception as error:
                if isinstance(error, GravyboxException):
                    log_extras = error.log_extras
                else:
                    log_extras = {}
                log_extras["error_str"] = str(error)
                log_extras["traceback"] = traceback.format_exc()
                log_extras["upstream_api"] = upstream_api_name
                logger.warning("upstream api call failed", extra=log_extras)
                return None

        return wrapper

    return decorator
