# Common Middleware Package
from .deprecated_urls import DeprecatedURLRedirectMiddleware

# Import from parent middleware.py module
# Note: common.middleware refers to common/middleware.py, not this package
import importlib
_middleware_module = importlib.import_module('..middleware', package='common.middleware')
MANAAccessControlMiddleware = _middleware_module.MANAAccessControlMiddleware
APILoggingMiddleware = _middleware_module.APILoggingMiddleware
DeprecationLoggingMiddleware = _middleware_module.DeprecationLoggingMiddleware

__all__ = [
    'DeprecatedURLRedirectMiddleware',
    'MANAAccessControlMiddleware',
    'APILoggingMiddleware',
    'DeprecationLoggingMiddleware',
]
