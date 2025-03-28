"""
Tests for the ClothAnalyzer
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.cloth_analyzer import ClothAnalyzer
from src.utils import logger

load_dotenv()
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
key = os.environ.get("AZURE_OPENAI_KEY")


def test_image_url():
    """Test face analysis on a single blob image."""

    # Get the full URL with token
    image_url = "https://media.istockphoto.com/id/950050590/photo/violet-summer-skirt-with-buttons-isolated-on-white.jpg?s=1024x1024&w=is&k=20&c=T_AH29vBBlKlOL68S40O25HxRwZERy2puiU4zvteic4="
    logger.info(f"Testing image from url: {image_url}")

    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
    AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")


    analyzer = ClothAnalyzer(
        openai_api_key=AZURE_OPENAI_KEY,
        openai_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_version=AZURE_OPENAI_API_VERSION,
        openai_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
    )


    result = analyzer.analyze_image(
        image_url,
        prompt="Analyze this image and return the following information in JSON format:\n"
        "1. color - Detailed color description\n"
        "2. pattern - Pattern or design characteristics\n"
        "3. fabric - Fabric type\n"
        "4. brand - Possible brand (use 'unknown' if not determined)\n"
        "5. description - Overall description",
    )
    logger.info(f"{result=}")
    if not result:
        raise ValueError("No result was returned")
