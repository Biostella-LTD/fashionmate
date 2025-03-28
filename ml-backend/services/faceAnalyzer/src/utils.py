"""
Utility functions for the face analyzer package.
Contains common utility functions used across modules.
"""

import re

import cv2
import numpy as np
import requests

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_file_dir = Path(__file__).parent.parent / "logs"
if not log_file_dir.exists():
    # Create the folder (and parent directories if needed)
    log_file_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_file_dir / "face_analyzer.log"

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

def download_image(image_url):
    """
    Download image from URL and convert to OpenCV format.

    Args:
        image_url (str): URL of the image to analyze

    Returns:
        numpy.ndarray: Image in OpenCV format

    Raises:
        ValueError: If image download or decoding fails
    """
    logger.info(f"Downloading image from URL: {image_url}")

    try:
        response = requests.get(
            image_url, stream=True, headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()  # Raise exception for HTTP errors

        # Convert image data to OpenCV format
        image = np.array(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Failed to decode image")
            raise ValueError("Failed to decode image")

        logger.info(f"Image downloaded successfully. Shape: {image.shape}")
        return image

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image. Error: {str(e)}")
        raise ValueError(f"Image download failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing downloaded image: {str(e)}")
        raise ValueError(f"Image processing failed: {str(e)}")
