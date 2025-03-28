"""
Test module for the body analyzer.
Tests the body shape and proportion analysis from an image URL.
"""
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the body analyzer
from src.body_analyzer import BodyAnalyzer
from src.utils import logger

# Test image URL
IMAGE_URL = "https://media.istockphoto.com/id/523150985/photo/full-body-portrait-of-a-handsome-young-man-smiling.jpg?s=612x612&w=0&k=20&c=dWBzZLrPBOkzk3LG7CKMUPCMe40cWclIidOvNg2_mVw="

body_analyzer = BodyAnalyzer()



def test_analyze_basic():
    """Test basic body analysis function."""
    # Analyze the test image
    result = body_analyzer.analyze(IMAGE_URL)

    # Check that result contains expected fields
    assert "body_shape" in result
    assert "body_proportion" in result

    # Log the results
    logger.info(f"Body shape: {result['body_shape']}")
    logger.info(f"Body proportion: {result['body_proportion']}")

    # Result should be a valid shape and proportion (not Error or Unknown)
    assert result["body_shape"] !=  "Error"
    assert result["body_proportion"] !=  "Error"

def test_analyze_with_details():
    """Test detailed body analysis function."""
    # Analyze the test image with details
    result = body_analyzer.analyze_with_details(IMAGE_URL)

    # Check basic fields
    assert "body_shape" in result
    assert "body_proportion" in result

    # Check for detail fields
    if result["body_shape"] != "Unknown" and result["body_shape"] != "Error":
        assert "shape_details" in result
        assert "description" in result["shape_details"]
        assert "clothing_tips" in result["shape_details"]

    if (
        result["body_proportion"] != "Unknown"
        and result["body_proportion"] != "Error"
    ):
        assert "proportion_details" in result
        assert "description" in result["proportion_details"]
        assert "clothing_tip" in result["proportion_details"]

    # Log detailed results
    logger.info(f"{result=}")


def main():
    """Run the tests."""
    test_analyze_basic()
    test_analyze_with_details()


if __name__ == "__main__":
    main()
