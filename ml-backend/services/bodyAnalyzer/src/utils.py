"""
Utility functions for the body analyzer package.
Contains common utility functions used across modules.
"""



import cv2
import numpy as np
import requests
import mediapipe as mp

from PIL import Image
from io import BytesIO
from urllib.parse import urlparse
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler

log_file_dir = Path(__file__).parent.parent / "logs"
if not log_file_dir.exists():
    # Create the folder (and parent directories if needed)
    log_file_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_file_dir / "body_analyzer.log"

# Set up module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up rotating file handler (max size 5MB, keep 3 backup files)
max_log_size = 500 * 1024 * 1024  # 5MB
backup_count = 1
rotating_handler = RotatingFileHandler(log_file_path, maxBytes=max_log_size, backupCount=backup_count)
rotating_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
rotating_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(rotating_handler)


mp_pose = mp.solutions.pose
# Initialize with more appropriate parameters for images
pose = mp_pose.Pose(
    static_image_mode=True,  # Set to True for images
    model_complexity=2,  # Use the most accurate model
    min_detection_confidence=0.5,
)


def download_image(image_url):
    """
    Download image from URL and convert to OpenCV format.

    Args:
        image_url (str): URL of the image to analyze

    Returns:
        numpy.ndarray: Image in RGB format for MediaPipe

    Raises:
        ValueError: If image download or decoding fails
    """
    logger.info(f"Downloading image from URL: {image_url}")

    try:
        response = requests.get(
            image_url, stream=True, headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()  # Raise exception for HTTP errors

        # First method: direct conversion to numpy array
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # Decode to BGR

        if img is None:
            # Fallback to PIL if OpenCV fails
            logger.warning("OpenCV failed to decode image, trying with PIL")
            img = Image.open(BytesIO(response.content))
            img = np.array(img)

            # If image is grayscale, convert to RGB
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            # If image has alpha channel, remove it
            elif img.shape[2] == 4:
                img = img[:, :, :3]
        else:
            # Convert BGR to RGB for MediaPipe
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if img is None:
            logger.error("Failed to decode image with both methods")
            raise ValueError("Failed to decode image")

        logger.info(f"Image downloaded successfully. Shape: {img.shape}")
        return img

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image. Error: {str(e)}")
        raise ValueError(f"Image download failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing downloaded image: {str(e)}")
        raise ValueError(f"Image processing failed: {str(e)}")


def get_pose_points(rgb_image):
    """
    Extract pose keypoints from an image using MediaPipe.

    Args:
        rgb_image (numpy.ndarray): Image in RGB format

    Returns:
        dict: Dictionary of keypoints with coordinates
    """
    try:
        # Verify image is valid
        if rgb_image is None or not isinstance(rgb_image, np.ndarray):
            logger.error("Invalid image provided")
            return {}

        # Check image dimensions
        if len(rgb_image.shape) != 3 or rgb_image.shape[2] != 3:
            logger.error(f"Invalid image dimensions: {rgb_image.shape}")
            return {}

        h, w, _ = rgb_image.shape
        logger.info(f"Processing image with dimensions: {w}x{h}")

        # Process with MediaPipe
        results = pose.process(rgb_image)

        if not results.pose_landmarks:
            logger.warning("No pose landmarks detected.")
            return {}

        # Extract key landmarks
        landmarks = results.pose_landmarks.landmark
        keypoints = {
            # Shoulders
            "LShoulder": (
                int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w),
                int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h),
            ),
            "RShoulder": (
                int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w),
                int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h),
            ),
            # Hips
            "LHip": (
                int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * w),
                int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * h),
            ),
            "RHip": (
                int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x * w),
                int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y * h),
            ),
            # Knees
            "LKnee": (
                int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x * w),
                int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y * h),
            ),
            "RKnee": (
                int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x * w),
                int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y * h),
            ),
            # Ankles
            "LAnkle": (
                int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x * w),
                int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * h),
            ),
            "RAnkle": (
                int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x * w),
                int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h),
            ),
        }

        logger.info(f"Successfully detected {len(keypoints)} keypoints")
        return keypoints

    except Exception as e:
        logger.error(f"Error in get_pose_points: {str(e)}")
        return {}


def calculate_distance(point1, point2):
    """
    Calculate Euclidean distance between two points.

    Args:
        point1 (tuple): First point (x, y)
        point2 (tuple): Second point (x, y)

    Returns:
        float: Euclidean distance
    """
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
