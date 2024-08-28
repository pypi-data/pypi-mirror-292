from gravybox.betterstack import collect_logger

logger = collect_logger()


class GravyboxException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.log_extras = {}


class BadStatusCode(GravyboxException):
    def __init__(self, query, upstream_api, response):
        message = "bad status code"
        super().__init__(message)
        self.response = response
        self.log_extras["query"] = query
        self.log_extras["upstream_api"] = upstream_api,
        self.log_extras["status_code"] = response.status_code,
        self.log_extras["payload"] = response.text


class UpstreamAPIFailure(GravyboxException):
    def __init__(self, query, upstream_api, response):
        message = "unhandled upstream api failure"
        super().__init__(message)
        self.log_extras["query"] = query,
        self.log_extras["upstream_api"] = upstream_api,
        self.log_extras["status_code"] = response.status_code,
        self.log_extras["payload"] = response.text


class UpstreamAPIServerCrash(GravyboxException):
    def __init__(self, query, upstream_api):
        message = "upstream api server crashed"
        super().__init__(message)
        self.log_extras["query"] = query,
        self.log_extras["upstream_api"] = upstream_api


class DataUnavailableFailure(GravyboxException):
    def __init__(self, query, upstream_api):
        message = "queried data is not available"
        super().__init__(message)
        self.log_extras["query"] = query,
        self.log_extras["upstream_api"] = upstream_api


class UnexpectedCondition(GravyboxException):
    def __init__(self, condition):
        message = "encountered unexpected condition"
        super().__init__(message)
        self.log_extras["condition"] = condition


class MalformedInput(GravyboxException):
    def __init__(self, malformed_input):
        message = "malformed input"
        super().__init__(message)
        self.log_extras["malformed_input"] = malformed_input
