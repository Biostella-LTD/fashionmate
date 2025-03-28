"""
Body shape analysis module.
Handles the detection and classification of body shapes based solely on shoulder and hip proportions.
"""

import logging

import numpy as np
from src.utils import calculate_distance, logger


class BodyShapeAnalyzer:
    """
    Class for analyzing and classifying body shapes from keypoints.

    This class determines body shapes such as "Hourglass/Rectangle",
    "Pear/Triangle", or "Inverted Triangle" based solely on the
    proportion between shoulders and hips.
    """

    def __init__(self):
        """Initialize the BodyShapeAnalyzer with shape classification thresholds."""
        # Thresholds for classification
        self.shape_thresholds = {
            "shoulder_hip_balance_min": 0.95,  # Min ratio for balanced shoulders/hips
            "shoulder_hip_balance_max": 1.05,  # Max ratio for balanced shoulders/hips
            "inverted_triangle_min": 1.05,  # Min shoulder/hip ratio for inverted triangle
            "pear_max": 0.95,  # Max shoulder/hip ratio for pear shape
        }
        logger.info("BodyShapeAnalyzer initialized")

    def analyze(self, keypoints):
        """
        Determine body shape based on body keypoints, focusing on shoulder-hip ratio.

        Args:
            keypoints (dict): Dictionary of body keypoints with coordinates

        Returns:
            str: Detected body shape ("Hourglass/Rectangle", "Pear/Triangle", "Inverted Triangle", or "Unknown")
        """
        logger.info("Analyzing body shape")
        try:
            # Check if we have the necessary keypoints
            required_points = ["RShoulder", "LShoulder", "RHip", "LHip"]
            if not all(point in keypoints for point in required_points):
                logger.warning(
                    "Not all required keypoints are available for body shape analysis"
                )
                return "Unknown"

            # Get keypoint coordinates
            right_shoulder = keypoints["RShoulder"]
            left_shoulder = keypoints["LShoulder"]
            right_hip = keypoints["RHip"]
            left_hip = keypoints["LHip"]

            # Calculate shoulder width
            shoulder_width = calculate_distance(right_shoulder, left_shoulder)

            # Calculate hip width
            hip_width = calculate_distance(right_hip, left_hip)

            # Calculate shoulder-hip ratio
            shoulder_hip_ratio = shoulder_width / hip_width if hip_width > 0 else 0

            logger.debug(
                f"Measurements - Shoulder: {shoulder_width:.1f}px, Hip: {hip_width:.1f}px"
            )
            logger.debug(f"Ratio - Shoulder/Hip: {shoulder_hip_ratio:.2f}")

            # Determine body shape based on shoulder-hip ratio
            body_shape = self._classify_shape(shoulder_hip_ratio)

            logger.info(f"Detected body shape: {body_shape}")
            return body_shape

        except Exception as e:
            logger.error(f"Error analyzing body shape: {str(e)}")
            return "Unknown"

    def _classify_shape(self, shoulder_hip_ratio):
        """
        Classify body shape based on shoulder-hip ratio.

        Args:
            shoulder_hip_ratio (float): Ratio of shoulder width to hip width

        Returns:
            str: Body shape classification
        """
        # Using the thresholds defined in the constructor
        if shoulder_hip_ratio > self.shape_thresholds["inverted_triangle_min"]:
            return "Inverted Triangle"
        elif shoulder_hip_ratio < self.shape_thresholds["pear_max"]:
            return "Pear/Triangle"
        else:
            # If shoulders and hips are balanced
            return "Hourglass/Rectangle"

    def get_shape_details(self, body_shape):
        """
        Get detailed description of a body shape.

        Args:
            body_shape (str): Body shape category

        Returns:
            dict: Detailed description and style recommendations
        """
        shape_details = {
            "Hourglass/Rectangle": {
                "description": "Your shoulders and hips are balanced in proportion.",
                "characteristics": [
                    "Balanced shoulder and hip measurements",
                    "Proportional upper and lower body",
                ],
                "clothing_tips": [
                    "Most styles work well with your balanced proportions",
                    "Experiment with different silhouettes to determine your preference",
                    "Use belts to define your waistline if desired",
                ],
            },
            "Pear/Triangle": {
                "description": "Your hips are wider than your shoulders.",
                "characteristics": [
                    "Hips wider than shoulders",
                    "Weight tends to distribute in the lower body",
                ],
                "clothing_tips": [
                    "Clothing that balances your proportions",
                    "Tops with details or structure to add visual width to shoulders",
                    "A-line skirts and dresses that skim over hips",
                ],
            },
            "Inverted Triangle": {
                "description": "Your shoulders are wider than your hips.",
                "characteristics": [
                    "Broader shoulders compared to hips",
                    "Athletic upper body",
                ],
                "clothing_tips": [
                    "Full or pleated skirts to add volume to lower body",
                    "Wide-leg pants to balance proportions",
                    "V-necks to soften shoulder line",
                ],
            },
            "Unknown": {
                "description": "Unable to determine body shape accurately.",
                "characteristics": ["N/A"],
                "clothing_tips": ["Consider a professional style consultation."],
            },
        }

        return shape_details.get(body_shape, shape_details["Unknown"])


# Create a singleton instance for use across the application
body_shape_analyzer = BodyShapeAnalyzer()


def analyze_body_shape(keypoints):
    """
    Function to analyze body shape from keypoints.

    Args:
        keypoints (dict): Dictionary of body keypoints with coordinates

    Returns:
        str: Body shape classification
    """
    return body_shape_analyzer.analyze(keypoints)
