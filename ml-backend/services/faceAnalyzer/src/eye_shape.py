"""
Eye shape analysis module.
Handles the detection and classification of eye shapes from facial landmarks.
"""

import numpy as np

from src.utils import logger


def analyze_eye_shape(eye_points):
    """
    Determine eye shape based on eye landmark points.

    Args:
        eye_points (numpy.ndarray): Eye landmark points (6 points per eye)

    Returns:
        str: Detected eye shape ("Almond", "Round", "Upturned", "Downturned", "Monolid", "Hooded", or "Unknown")
    """
    try:
        # Calculate dimensions
        eye_width = np.linalg.norm(eye_points[0] - eye_points[3])
        eye_height = (
            np.linalg.norm(eye_points[1] - eye_points[5])
            + np.linalg.norm(eye_points[2] - eye_points[4])
        ) / 2
        eye_ratio = eye_width / eye_height

        logger.debug(
            f"Eye measurements - Width: {eye_width:.2f}, Height: {eye_height:.2f}, Ratio: {eye_ratio:.2f}"
        )

        # Determine eye shape based on proportions
        if eye_ratio > 3.5:
            eye_shape = "Almond"
        elif 2.8 < eye_ratio <= 3.5:
            # Check if the outer corner is higher or lower than the inner corner
            is_upturned = (
                eye_points[5][1] < eye_points[1][1]
            )  # Y-axis increases downward
            eye_shape = "Upturned" if is_upturned else "Downturned"
        elif 2.2 < eye_ratio <= 2.8:
            eye_shape = "Round"
        else:
            # Check for monolid (little to no visible crease)
            vertical_distance = abs(eye_points[1][1] - eye_points[5][1])
            eye_shape = "Monolid" if vertical_distance < 3 else "Hooded"

        logger.debug(f"Detected eye shape: {eye_shape}")
        return eye_shape

    except Exception as e:
        logger.exception(f"Error analyzing eye shape: {str(e)}")
        return "Unknown"


def analyze_eyes(landmarks):
    """
    Analyze both eyes and determine the overall eye shape.

    Args:
        landmarks (numpy.ndarray): Full set of facial landmarks

    Returns:
        str: Overall eye shape classification
    """
    logger.info("Analyzing eye shape")
    try:
        # Extract eye landmarks
        left_eye = landmarks[36:42]  # Left eye points
        right_eye = landmarks[42:48]  # Right eye points

        # Analyze each eye
        left_eye_shape = analyze_eye_shape(left_eye)
        right_eye_shape = analyze_eye_shape(right_eye)

        # Determine overall eye shape (prioritize left eye if different)
        overall_shape = (
            left_eye_shape if left_eye_shape == right_eye_shape else left_eye_shape
        )

        logger.info(
            f"Left eye: {left_eye_shape}, Right eye: {right_eye_shape}, Selected: {overall_shape}"
        )
        return overall_shape

    except Exception as e:
        logger.error(f"Error in overall eye analysis: {str(e)}")
        return "Unknown"
