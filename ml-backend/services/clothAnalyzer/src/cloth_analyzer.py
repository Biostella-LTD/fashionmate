"""
Cloth Analyzer Module

This module provides functionality for analyzing cloth images using Azure OpenAI's GPT-4 Vision model..
"""

import base64
import json
import time
from typing import Any, Dict

import cv2
import numpy as np
import requests
from openai import AzureOpenAI
from pydantic import HttpUrl

from .utils import logger


class ClothAnalyzer:
    """
    A class for analyzing images using Azure OpenAI's GPT-4 Vision model.
    """

    # Clothing item type classification mappings
    CLOTHING_CATEGORIES = {
        "shirt": ["t-shirt", "button-up", "blouse", "polo", "top", "dress shirt"],
        "pants": ["jeans", "trousers", "slacks", "chinos", "leggings"],
        "dress": ["gown", "evening dress", "sun dress", "midi dress", "maxi dress"],
        "jacket": ["coat", "blazer", "windbreaker", "cardigan", "bomber"],
        "skirt": ["mini skirt", "midi skirt", "pleated skirt", "a-line skirt"],
        "shoes": ["sneakers", "boots", "heels", "flats", "sandals", "loafers"],
    }

    def __init__(
        self,
        openai_api_key: str,
        openai_endpoint: str,
        openai_api_version: str,
        openai_deployment: str,
    ):
        self.client = AzureOpenAI(
            api_version=openai_api_version,
            azure_endpoint=openai_endpoint,
            api_key=openai_api_key,
        )
        self.deployment = openai_deployment

    def download_image(self, image_url):
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
            response.raise_for_status()

            # Convert image data to OpenCV format
            image = np.frombuffer(response.content, dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)

            if image is None:
                logger.error("Failed to decode image")
                raise ValueError("Failed to decode image")

            logger.info(f"Image downloaded successfully.")
            return image
        except Exception as e:
            logger.exception(e)

    def encode_image_to_base64(self, image: bytes) -> str:
        # return base64.b64encode(image_data).decode("utf-8")
        try:
            # Encode image to bytes in PNG format
            _, buffer = cv2.imencode(".png", image)
            base64_string = base64.b64encode(buffer).decode("utf-8")
            return base64_string
        except Exception as e:
            logger.exception(f"Error encoding image to base64: {e}")
            raise e

    def classify_clothing_category(self, analysis_result: str) -> str:
        if False:
            # Add clothing category classification
            description = analysis_result.get("description", "")
            """
            Classify clothing category based on description text.
            """
            analysis_result["category"] = "unknown"
            description_lower = description.lower()
            for category, keywords in ClothAnalyzer.CLOTHING_CATEGORIES.items():
                for keyword in keywords:
                    if keyword in description_lower:
                        analysis_result["category"] = category
                        return analysis_result
        return analysis_result

    def analyze_image(self, image_url, prompt) -> Dict[str, Any]:

        image_data = self.download_image(image_url)

        base64_image = self.encode_image_to_base64(image_data)

        logger.info(f"Analyzing image...")
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional image analysis assistant. Please analyze the provided image and return the results in JSON format.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=4096,
            temperature=0.5,
            model=self.deployment,
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content

        try:
            result_json = json.loads(result_text)
            result_json = self.classify_clothing_category(result_json)
            logger.info(f"Analysis complete.")
            result_json["image_url"] = HttpUrl(image_url)
            result_json["created_at"] = int(time.time())

            logger.info(f"Analysis {result_json=}")

            return result_json
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_content": result_text}

    def close(self) -> None:
        if self.client:
            self.client.close()
