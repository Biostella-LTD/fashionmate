#!/usr/bin/env python3
"""
Test script for the FaceAnalyzer functionality.
This script tests the face analysis on sample images.
"""

import json
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import get_blob_url
from src.face_analyzer import FaceAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_analyzer")


def test_image(url, description, is_blob=False, container=None, path=None):
    """
    Test face analysis on a specific image URL.

    Args:
        url (str): URL of the image to analyze
        description (str): Description of the image for logging
        is_blob (bool): Whether this URL is an Azure Blob URL that needs token
        container (str, optional): Blob container if is_blob is True
        path (str, optional): Blob path if is_blob is True
    """
    logger.info(f"Testing image: {description}")

    # Construct the full URL with token if needed
    if is_blob and container and path:
        full_url = get_blob_url(container, path)
        logger.info(f"Using blob URL for container: {container}")
    else:
        full_url = url
        logger.info(f"URL: {url}")

    try:
        # Initialize analyzer
        analyzer = FaceAnalyzer()

        # Analyze image
        start_message = f"Starting analysis of {description}"
        print(f"\n{'=' * len(start_message)}")
        print(start_message)
        print(f"{'=' * len(start_message)}")

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


def main():
    """Main function to run tests on sample images."""
    logger.info("Starting face analyzer test")

    # Test cases with different image URLs
    test_cases = [
        {
            "container": "user-1234",
            "path": "personal/face_man.jpg",
            "is_blob": True,
            "description": "Sample Azure storage image (user-1234)",
        },
        {
            "url": "https://i.pinimg.com/564x/10/38/ab/1038ab3c56529c7159958bd312908039.jpg",
            "description": "Pinterest image - Long face example",
        },
        {
            "url": "https://www.byrdie.com/thmb/uUWgcGYB8YGq7wFt3HODlflkwZ0=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-2037036951-f0b153529cd14794b451934ad4f476ef.jpg",
            "description": "Round face example",
        },
        {
            "url": "https://theglowmemo.com/.image/t_share/MTk4NDM0ODk0MTM1Njk4OTkw/bangs-for-square-face-2200x1230.jpg",
            "description": "Square face example",
        },
        {
            "url": "https://media.allaboutvision.com/cms/caas/v1/media/432964/data/picture/5075424d6ebff39e0b163910b0b7fd22.jpg",
            "description": "Oval face example",
        },
    ]

    # Run tests for each case
    results = {}
    for i, case in enumerate(test_cases, 1):
        print(f"\n\n{'#' * 80}")
        print(f"# TEST CASE {i}: {case['description']}")
        print(f"{'#' * 80}")

        if case.get("is_blob", False):
            result = test_image(
                url=None,
                description=case["description"],
                is_blob=True,
                container=case["container"],
                path=case["path"],
            )
        else:
            result = test_image(case["url"], case["description"])

        results[case["description"]] = result

    # Print overall summary
    print(f"\n\n{'#' * 80}")
    print("# SUMMARY OF ALL TESTS")
    print(f"{'#' * 80}")

    for description, result in results.items():
        status = "✅ Success" if result and "error" not in result else "❌ Failed"
        print(f"{status}: {description}")

    logger.info("Face analyzer test completed")


if __name__ == "__main__":
    main()
