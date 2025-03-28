"""
Skin tone analysis module.
Handles the detection and classification of skin tones from facial images.
"""


import cv2
import numpy as np

from src.utils import logger

def get_safe_region(image, center_x, center_y, size):
    """
    Extract a safe region around a center point, handling image boundaries.

    Args:
        image (numpy.ndarray): Image in OpenCV format
        center_x (int): Center X coordinate
        center_y (int): Center Y coordinate
        size (int): Half-size of square region

    Returns:
        numpy.ndarray or None: Image region or None if invalid
    """
    height, width = image.shape[:2]

    x1 = max(0, center_x - size)
    y1 = max(0, center_y - size)
    x2 = min(width - 1, center_x + size)
    y2 = min(height - 1, center_y + size)

    if x2 <= x1 or y2 <= y1:
        return None

    return image[y1:y2, x1:x2]


def analyze_skin_tone(image, landmarks):
    """
    Determine skin tone based on facial regions.
    Uses hue, saturation, and value from HSV color space for accurate classification.

    Args:
        image (numpy.ndarray): Image in OpenCV format
        landmarks (numpy.ndarray): Facial landmarks

    Returns:
        str: Detected skin tone
    """
    logger.info("Analyzing skin tone")
    try:
        # Extract sample points for skin tone analysis

        # Calculate key facial points
        # Left cheek region (average of points 1, 2, 3)
        left_cheek_x = int((landmarks[1][0] + landmarks[2][0] + landmarks[3][0]) / 3)
        left_cheek_y = int((landmarks[1][1] + landmarks[2][1] + landmarks[3][1]) / 3)

        # Right cheek region (average of points 13, 14, 15)
        right_cheek_x = int(
            (landmarks[13][0] + landmarks[14][0] + landmarks[15][0]) / 3
        )
        right_cheek_y = int(
            (landmarks[13][1] + landmarks[14][1] + landmarks[15][1]) / 3
        )

        # Forehead region (above nose bridge)
        forehead_x = int(landmarks[27][0])
        forehead_y = int(landmarks[27][1] - (landmarks[8][1] - landmarks[27][1]) * 0.2)

        # Get sample regions with fixed size
        sample_size = 10

        # Extract regions safely
        left_region = get_safe_region(image, left_cheek_x, left_cheek_y, sample_size)
        right_region = get_safe_region(image, right_cheek_x, right_cheek_y, sample_size)
        forehead_region = get_safe_region(image, forehead_x, forehead_y, sample_size)

        # Collect valid regions
        valid_regions = [
            r
            for r in [left_region, right_region, forehead_region]
            if r is not None and r.size > 0
        ]

        if not valid_regions:
            logger.warning("No valid skin regions found for analysis")
            return "Unknown"

        # Process each region and average the results
        all_hue = []
        all_sat = []
        all_val = []

        for region in valid_regions:
            try:
                region_hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
                all_hue.append(np.mean(region_hsv[:, :, 0]))
                all_sat.append(np.mean(region_hsv[:, :, 1]))
                all_val.append(np.mean(region_hsv[:, :, 2]))
            except Exception as e:
                logger.warning(f"Error processing region: {str(e)}")
                continue

        if not all_hue:
            logger.warning("Failed to process any skin regions")
            return "Unknown"

        # Average the values from all regions
        avg_hue = np.mean(all_hue)
        avg_sat = np.mean(all_sat)
        avg_val = np.mean(all_val)

        logger.debug(
            f"Skin HSV - Hue: {avg_hue:.1f}, Saturation: {avg_sat:.1f}, Value: {avg_val:.1f}"
        )

        # Classify skin tone using all three components

        # Determine warm vs cool undertone using saturation
        warm_threshold = 50
        is_warm = avg_sat > warm_threshold
        temp_modifier = "Warm" if is_warm else "Cool"

        # Classify skin tone based on value (brightness) and hue
        if avg_val > 200:
            if is_warm:
                skin_tone = f"Very Fair {temp_modifier}"
            else:
                skin_tone = "Porcelain"
        elif avg_val > 170:
            if is_warm:
                skin_tone = f"Fair {temp_modifier}"
            else:
                skin_tone = f"Light {temp_modifier}"
        elif avg_val > 140:
            if avg_hue < 20:
                skin_tone = f"Medium {temp_modifier}"
            else:
                skin_tone = "Olive" if avg_sat > 60 else "Neutral"
        elif avg_val > 110:
            if is_warm:
                skin_tone = f"Tan {temp_modifier}"
            else:
                skin_tone = "Medium Deep"
        elif avg_val > 80:
            if avg_sat > 70:
                skin_tone = f"Deep {temp_modifier}"
            else:
                skin_tone = "Deep Neutral"
        else:
            skin_tone = "Deep Rich"

        logger.info(f"Detected skin tone: {skin_tone}")
        return skin_tone

    except Exception as e:
        logger.exception(f"Error analyzing skin tone: {str(e)}")
        return "Unknown"
