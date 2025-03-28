"""
Custom exception classes for the body analyzer package.
Contains all exception types used across modules.
"""


class BodyAnalysisError(Exception):
    """Base exception class for all body analysis errors."""

    def __init__(self, message="An error occurred during body analysis"):
        self.message = message
        super().__init__(self.message)


class ImageDownloadError(BodyAnalysisError):
    """Exception raised when there is an error downloading or processing an image."""

    def __init__(self, message="Failed to download or process the image"):
        self.message = message
        super().__init__(self.message)


class NoBodyDetectedError(BodyAnalysisError):
    """Exception raised when no body is detected in an image."""

    def __init__(self, message="No body detected in the image"):
        self.message = message
        super().__init__(self.message)


class KeypointsError(BodyAnalysisError):
    """Exception raised when there is an issue with keypoints."""

    def __init__(self, message="Error processing body keypoints"):
        self.message = message
        super().__init__(self.message)


class MissingKeypointsError(KeypointsError):
    """Exception raised when required keypoints are missing."""

    def __init__(self, missing_points=None):
        points_str = (
            ", ".join(missing_points) if missing_points else "required keypoints"
        )
        self.message = f"Missing {points_str} for analysis"
        super(KeypointsError, self).__init__(self.message)
        self.missing_points = missing_points


class ModelError(BodyAnalysisError):
    """Exception raised when there is an error with ML models."""

    def __init__(self, message="Error with machine learning model"):
        self.message = message
        super().__init__(self.message)


class InvalidInputError(BodyAnalysisError):
    """Exception raised when input parameters are invalid."""

    def __init__(self, message="Invalid input parameters"):
        self.message = message
        super().__init__(self.message)


class AnalysisTimeoutError(BodyAnalysisError):
    """Exception raised when analysis takes too long and times out."""

    def __init__(self, message="Analysis timed out"):
        self.message = message
        super().__init__(self.message)
