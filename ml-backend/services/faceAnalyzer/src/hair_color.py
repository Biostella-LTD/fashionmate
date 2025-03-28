"""
Hair color analysis module.
Handles the detection and classification of hair colors from facial images.
"""

import cv2
import numpy as np

from src.utils import logger

# Hair color definitions based on HSV ranges
HAIR_COLOR_RANGES = {    
    "Black": {"lower": (0, 0, 0), "upper": (180, 255, 50), "name": "Black"},    
    "Dark Brown": {"lower": (0, 30, 40), "upper": (20, 140, 80), "name": "Dark Brown"},    
    "Brown": {"lower": (15, 50, 80), "upper": (25, 150, 130), "name": "Brown"},    
    "Light Brown": {    
        "lower": (25, 30, 130),    
        "upper": (30, 100, 180),    
        "name": "Light Brown",    
    },    
    "Blonde": {"lower": (30, 10, 140), "upper": (35, 100, 220), "name": "Blonde"},    
    "Red": {"lower": (0, 100, 100), "upper": (10, 255, 180), "name": "Red"},    
    "Auburn": {"lower": (10, 80, 80), "upper": (20, 200, 120), "name": "Auburn"},    
    "Gray": {"lower": (0, 0, 130), "upper": (180, 30, 200), "name": "Gray"},    
    "White": {"lower": (0, 0, 200), "upper": (180, 30, 255), "name": "White"},    
} 

def create_hair_mask(image, landmarks):  
    """  
    Enhanced hair mask creation using additional landmarks and morphological operations.  
    """  
    height, width = image.shape[:2]  
    mask = np.zeros((height, width), dtype=np.uint8)  
  
    # Define points for the forehead and hair region using more landmarks  
    # For instance, use points 19-24 for eyebrows to estimate the hairline  
    forehead_y = int(np.mean(landmarks[19:24, 1]) - (landmarks[8][1] - np.mean(landmarks[19:24, 1])) * 1.2)  
    forehead_y = max(0, forehead_y)  
  
    # Define the width of the hair region  
    hair_width_factor = 1.3  
    temple_left = landmarks[0][0] - int((landmarks[16][0] - landmarks[0][0]) * (hair_width_factor - 1) / 2)  
    temple_right = landmarks[16][0] + int((landmarks[16][0] - landmarks[0][0]) * (hair_width_factor - 1) / 2)  
    hair_top = forehead_y  
  
    # Ensure boundaries are within image dimensions  
    hair_left = max(0, temple_left)  
    hair_right = min(width, temple_right)  
  
    # Define the hair region polygon  
    hair_region = np.array([  
        [hair_left, hair_top],  
        [hair_right, hair_top],  
        [hair_right, height],  
        [hair_left, height]  
    ], dtype=np.int32)  
  
    # Fill the hair region  
    cv2.fillPoly(mask, [hair_region], 255)  
  
    # Optional: Use facial landmarks to exclude face from hair mask  
    face_contour = landmarks[0:17]  # Jawline  
    forehead_contour = np.array([  
        [landmarks[0][0], forehead_y],  
        [landmarks[16][0], forehead_y]  
    ], dtype=np.int32)  
    full_contour = np.vstack([face_contour, forehead_contour])  
  
    # Exclude face from hair mask  
    cv2.fillPoly(mask, [full_contour], 0)  
  
    # Apply morphological operations  
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  
  
    return mask  


def analyze_hair_color(image, landmarks):
    """
    Determine hair color based on color analysis of the hair region.

    Args:
        image (numpy.ndarray): Image in OpenCV format
        landmarks (numpy.ndarray): Facial landmarks

    Returns:
        str: Detected hair color
    """
    logger.info("Analyzing hair color")
    try:
        # Create mask for hair region
        hair_mask = create_hair_mask(image, landmarks)

        # Apply mask to image
        masked_image = cv2.bitwise_and(image, image, mask=hair_mask)

        # Convert to HSV for better color analysis
        hsv_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)

        # Count non-zero pixels in mask
        non_zero_pixels = cv2.countNonZero(hair_mask)
        if non_zero_pixels < 100:
            logger.warning("Hair region too small for reliable analysis")
            return "Unknown"

        # Get average HSV values in the hair region
        mask_indices = np.where(hair_mask > 0)
        h_values = hsv_image[mask_indices[0], mask_indices[1], 0]
        s_values = hsv_image[mask_indices[0], mask_indices[1], 1]
        v_values = hsv_image[mask_indices[0], mask_indices[1], 2]

        # Calculate mean HSV values
        mean_h = np.mean(h_values) if len(h_values) > 0 else 0
        mean_s = np.mean(s_values) if len(s_values) > 0 else 0
        mean_v = np.mean(v_values) if len(v_values) > 0 else 0

        logger.debug(
            f"Hair region HSV - Hue: {mean_h:.1f}, Saturation: {mean_s:.1f}, Value: {mean_v:.1f}"
        )

        # Match against known hair color ranges
        color_scores = {}
        hsv_mean = np.array([mean_h, mean_s, mean_v])

        for color, range_data in HAIR_COLOR_RANGES.items():
            lower = np.array(range_data["lower"])
            upper = np.array(range_data["upper"])

            # Calculate how well this pixel fits in the range
            # The closer to the center of the range, the higher the score
            range_center = (lower + upper) / 2
            range_size = upper - lower

            # Prevent division by zero
            range_size = np.maximum(range_size, 1)

            # Calculate distance from center, normalized by range size
            distance = np.abs(hsv_mean - range_center) / range_size
            score = 1 - np.mean(distance)  # Higher score = better match

            color_scores[color] = score

        # Find the best matching color
        best_color = max(color_scores.items(), key=lambda x: x[1])

        # Check if the best score is good enough
        if best_color[1] < 0.25:
            logger.warning(
                f"Low confidence hair color detection: {best_color[0]} (score: {best_color[1]:.2f})"
            )

            # Fallback method based on simple value range checks
            if mean_v < 60:
                hair_color = "Black"
            elif mean_v < 100 and mean_s > 30:
                hair_color = "Dark Brown"
            elif mean_s < 30 and mean_v > 150:
                hair_color = "Gray" if mean_v < 200 else "White"
            elif mean_h < 15 and mean_s > 100:
                hair_color = "Red"
            elif mean_h < 30:
                hair_color = "Brown"
            elif mean_h < 40:
                hair_color = "Blonde"
            else:
                hair_color = "Unknown"
        else:
            hair_color = best_color[0]

        logger.info(f"Detected hair color: {hair_color}")
        return hair_color

    except Exception as e:
        logger.error(f"Error analyzing hair color: {str(e)}")
        return "Unknown"
