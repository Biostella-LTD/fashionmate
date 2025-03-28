"""
Custom exceptions for the face analyzer package.
"""


class FaceAnalysisResponseError(Exception):
    """Base class for all face analysis exceptions."""

    pass


class ModelError(FaceAnalysisResponseError):
    """Error related to face detection or landmark prediction models."""

    pass


class NoFaceDetectedError(FaceAnalysisResponseError):
    """Error when no face is detected in the image."""

    pass


class ImageDownloadError(FaceAnalysisResponseError):
    """Error when downloading or processing the image."""

    pass


class FeatureExtractionError(FaceAnalysisResponseError):
    """Error when extracting or analyzing facial features."""

    pass
