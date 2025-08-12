"""
Custom exceptions for S3 Vector Browser
"""


class S3VectorBrowserError(Exception):
    """Base exception for S3 Vector Browser"""
    pass


class AWSConnectionError(S3VectorBrowserError):
    """Raised when unable to connect to AWS services"""
    pass


class ResourceNotFoundError(S3VectorBrowserError):
    """Raised when a requested resource is not found"""
    pass


class PermissionDeniedError(S3VectorBrowserError):
    """Raised when user lacks permission for an operation"""
    pass


class ServiceUnavailableError(S3VectorBrowserError):
    """Raised when AWS service is temporarily unavailable"""
    pass


class NavigationError(S3VectorBrowserError):
    """Raised when navigation state is invalid"""
    pass


class DataLoadingError(S3VectorBrowserError):
    """Raised when data loading fails"""
    pass