"""
Main BodyAnalyzer class for the body analyzer package.
Orchestrates the analysis of body shape and proportions from an image URL.
"""

import time
from pydantic import HttpUrl
from src.body_proportions import analyze_proportions, BodyProportionAnalyzer
from src.body_shape import analyze_body_shape, BodyShapeAnalyzer
from src.utils import download_image, get_pose_points, logger

# Import exceptions
from src.analysis_exceptions import (
    BodyAnalysisError,
    ImageDownloadError,
    NoBodyDetectedError,
)


class BodyAnalyzer:
    """
    A class for analyzing body features from images.
    Focuses on determining body shape and proportion from pose keypoints.
    """

    def __init__(self):
        """
        Initialize the BodyAnalyzer.
        """
        logger.info("Body analyzer initialized")
        self.body_shape_analyzer = BodyShapeAnalyzer()
        self.body_proportion_analyzer = BodyProportionAnalyzer()

    def analyze(self, image_url):
        """
        Analyze an image and return body shape and proportion.

        Args:
            image_url (str): URL of the image to analyze

        Returns:
            dict: Dictionary containing body_shape and proportion
        """
        logger.info(f"Starting body analysis for image: {image_url}")
        start_time = time.time()

        # Initialize result with default values
        result = {
            "body_shape": "Unknown",
            "body_proportion": "Unknown",
            "body_image_url": HttpUrl(image_url),
        }

        # Download and prepare image
        try:
            image = download_image(image_url)
            logger.info(f"Image downloaded successfully with shape: {image.shape}")
        except Exception as e:
            logger.error(f"Error downloading or processing image: {str(e)}")
            raise ImageDownloadError(f"Failed to process image: {str(e)}")

        # Detect body keypoints using MediaPipe
        logger.info("Detecting body keypoints using MediaPipe")
        keypoints = get_pose_points(image)

        if not keypoints:
            logger.warning("No body detected in the image")
            raise NoBodyDetectedError("No body detected in the image")

        # Log detection success
        logger.info(f"Body detected with {len(keypoints)} keypoints")

        # Analyze body shape
        result["body_shape"] = analyze_body_shape(keypoints)
        logger.info(f"Body shape analysis complete: {result['body_shape']}")

        # Analyze body proportions
        result["body_proportion"] = analyze_proportions(keypoints)
        logger.info(f"Body proportion analysis complete: {result['body_proportion']}")

        shape_details = self.body_shape_analyzer.get_shape_details(result["body_shape"])
        if shape_details:
            result["shape_details"] = shape_details

        proportion_details = self.body_proportion_analyzer.get_proportion_details(
            result["body_proportion"]
        )
        if proportion_details:
            result["proportion_details"] = proportion_details

        # Calculate and log total processing time
        total_time = time.time() - start_time
        logger.info(f"Analysis completed in {total_time:.2f} seconds")
        logger.info(f"{result=}")

        return result

    def analyze_with_details(self, image_url):
        """
        Analyze an image and return body shape and proportion with detailed descriptions.

        Args:
            image_url (str): URL of the image to analyze

        Returns:
            dict: Dictionary containing body_shape, proportion, and detailed descriptions
        """
        # Get basic analysis
        result = self.analyze(image_url)

        # If there was an error, return the result as is
        if "error" in result:
            return result

        # Return the full result including any details that were added
        return result
