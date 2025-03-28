"""
Simple test script for MediaPipe pose detection.
Tests the get_pose_points function from utils.
"""

import os
import sys

import cv2
import matplotlib.pyplot as plt


# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from utils
from src.utils import download_image, get_pose_points, logger

IMAGE_URL = "https://media.istockphoto.com/id/523150985/photo/full-body-portrait-of-a-handsome-young-man-smiling.jpg?s=612x612&w=0&k=20&c=dWBzZLrPBOkzk3LG7CKMUPCMe40cWclIidOvNg2_mVw="


def main():
    """Main function to run the test script."""
    try:
        # Download image
        image = download_image(IMAGE_URL)

        # Get pose points
        keypoints = get_pose_points(image)

        if not keypoints:
            logger.error("No pose keypoints detected")
            return 1

        # Print detected keypoints
        logger.info(f"Detected {len(keypoints)} keypoints:")
        for name, point in keypoints.items():
            logger.info(f"  {name}: {point}")

        # Visualize keypoints
        # Convert to BGR for OpenCV drawing
        display_img = cv2.cvtColor(image.copy(), cv2.COLOR_RGB2BGR)

        # Draw keypoints
        for name, point in keypoints.items():
            cv2.circle(display_img, point, 5, (0, 255, 0), -1)
            cv2.putText(
                display_img,
                name,
                (point[0] + 10, point[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        # Convert back to RGB for displaying with matplotlib
        display_img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)

        # Display the image with keypoints
        plt.figure(figsize=(10, 10))
        plt.imshow(display_img_rgb)
        plt.title("Detected Pose Keypoints")
        plt.axis("off")
        plt.show()

        return 0

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
