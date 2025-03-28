"""
Simple test script for the FaceAnalyzer on a single url image.
"""

import json
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.face_analyzer import FaceAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_image_url")


def test_image_url():
    """Test face analysis on a single blob image."""

    # Get the full URL with token
    full_url = "https://img.freepik.com/free-photo/portrait-white-man-isolated_53876-40306.jpg?ga=GA1.1.499157807.1742564961&semt=ais_hybrid"
    logger.info(f"Testing image from url: {full_url}")

    try:
        # Initialize analyzer
        analyzer = FaceAnalyzer()

        print(f"\n{'=' * 50}")
        print(f"Starting analysis of blob image")
        print(f"{'=' * 50}")

        # Analyze image
        result = analyzer.analyze(full_url)

        # Print results
        print("\nResults:")
        print("--------")

        # Print summary
        print("\nSummary:")
        print("--------")
        if "error" in result and result["error"]:
            print(f"❌ Analysis failed: {result['error']}")
        else:
            print(f"✅ User ID: {result['user_id']}")
            print(f"✅ Face Shape: {result['face_shape']}")
            print(f"✅ Eye Shape: {result['eye_shape']}")
            print(f"✅ Skin Tone: {result['skin_tone']}")
            print(f"✅ Hair Color: {result['hair_color']}")

        return result

    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return None


if __name__ == "__main__":
    logger.info("Starting single blob image test")
    result = test_image_url()

    # Print final status
    status = "✅ Success" if result and "error" not in result else "❌ Failed"
    print(f"\n{'=' * 50}")
    print(f"Test result: {status}")
    print(f"{'=' * 50}")

    logger.info("Single blob image test completed")
