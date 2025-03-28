"""
Body proportions analysis module.
Handles the analysis of body proportions from body keypoints.
Uses shoulder midpoint instead of neck for more accurate measurements.
"""
from src.utils import calculate_distance, logger


class BodyProportionAnalyzer:
    """
    Class for analyzing body proportions from keypoints.

    This class provides methods to determine body proportions
    such as "Balanced", "Long Torso", or "Long Legs" based on
    the ratio between torso and leg length.
    """

    def __init__(self):
        """Initialize the BodyProportionAnalyzer."""
        self.proportion_thresholds = {
            "balanced_min": 0.8,  # Minimum ratio for balanced proportion
            "balanced_max": 1.2,  # Maximum ratio for balanced proportion
            "long_torso_min": 1.2,  # Minimum ratio for long torso
            "short_torso_max": 0.8,  # Maximum ratio for short torso (long legs)
        }
        logger.info("BodyProportionAnalyzer initialized")

    def analyze(self, keypoints):
        """
        Analyze body proportions based on body keypoints.
        Uses shoulder midpoint instead of neck for more accurate measurements.

        Args:
            keypoints (dict): Dictionary of body keypoints with coordinates

        Returns:
            str: Body proportion category ("Balanced", "Long Torso", "Long Legs", or "Unknown")
        """
        logger.info("Analyzing body proportions")
        try:
            # Check if we have the necessary keypoints
            required_points = [
                "RShoulder",
                "LShoulder",
                "RHip",
                "LHip",
                "RKnee",
                "LKnee",
                "RAnkle",
                "LAnkle",
            ]
            if not all(point in keypoints for point in required_points):
                logger.warning(
                    "Not all required keypoints are available for proportion analysis"
                )
                return "Unknown"

            # Calculate torso length (shoulder midpoint to hips)
            right_shoulder = keypoints["RShoulder"]
            left_shoulder = keypoints["LShoulder"]

            # Calculate shoulder midpoint
            shoulder_mid_x = (right_shoulder[0] + left_shoulder[0]) / 2
            shoulder_mid_y = (right_shoulder[1] + left_shoulder[1]) / 2
            shoulder_midpoint = (shoulder_mid_x, shoulder_mid_y)

            right_hip = keypoints["RHip"]
            left_hip = keypoints["LHip"]

            # Use midpoint of hips
            hip_mid_x = (right_hip[0] + left_hip[0]) / 2
            hip_mid_y = (right_hip[1] + left_hip[1]) / 2
            hip_midpoint = (hip_mid_x, hip_mid_y)

            torso_length = calculate_distance(shoulder_midpoint, hip_midpoint)

            # Calculate leg length (hips to ankles)
            right_ankle = keypoints["RAnkle"]
            left_ankle = keypoints["LAnkle"]

            # Average of both legs
            right_leg_length = calculate_distance(right_hip, right_ankle)
            left_leg_length = calculate_distance(left_hip, left_ankle)
            leg_length = (right_leg_length + left_leg_length) / 2

            # Calculate torso-to-leg ratio
            torso_leg_ratio = torso_length / leg_length if leg_length > 0 else 0

            logger.debug(
                f"Measurements - Torso (shoulder to hip): {torso_length:.1f}px, Legs: {leg_length:.1f}px, Ratio: {torso_leg_ratio:.2f}"
            )

            # Determine proportion category based on ratio
            if (
                self.proportion_thresholds["balanced_min"]
                <= torso_leg_ratio
                <= self.proportion_thresholds["balanced_max"]
            ):
                proportion = "Balanced"
            elif torso_leg_ratio > self.proportion_thresholds["long_torso_min"]:
                proportion = "Long Torso"
            else:  # torso_leg_ratio < self.proportion_thresholds["short_torso_max"]
                proportion = "Long Legs"

            logger.info(
                f"Detected body proportion: {proportion} (Torso-Leg Ratio: {torso_leg_ratio:.2f})"
            )
            return proportion

        except Exception as e:
            logger.error(f"Error analyzing body proportions: {str(e)}")
            return "Unknown"

    def get_proportion_details(self, proportion):
        """
        Get detailed description of a body proportion.

        Args:
            proportion (str): Body proportion category

        Returns:
            dict: Detailed description and style recommendations
        """
        proportion_details = {
            "Balanced": {
                "description": "Your torso and legs are in balanced proportion to each other.",
                "clothing_tip": "Most clothing styles work well for your balanced proportions.",
            },
            "Long Torso": {
                "description": "Your torso is proportionally longer than your legs.",
                "clothing_tip": "High-waisted bottoms can help create the illusion of longer legs.",
            },
            "Long Legs": {
                "description": "Your legs are proportionally longer than your torso.",
                "clothing_tip": "Mid to low-rise bottoms and longer tops work well for your proportions.",
            },
            "Unknown": {
                "description": "Unable to determine body proportions accurately.",
                "clothing_tip": "Consider a professional fitting consultation.",
            },
        }

        return proportion_details.get(proportion, proportion_details["Unknown"])


# Create a singleton instance for use across the application
body_proportion_analyzer = BodyProportionAnalyzer()


def analyze_proportions(keypoints):
    """
    Legacy function to maintain compatibility with existing code.

    Args:
        keypoints (dict): Dictionary of body keypoints with coordinates

    Returns:
        str: Body proportion category
    """
    return body_proportion_analyzer.analyze(keypoints)
