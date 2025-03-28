"""
FastAPI application for body analysis API.
Provides endpoints for body shape and proportion analysis.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Any, Dict, Optional

from src.body_analyzer import BodyAnalyzer
from src.utils import logger

# Initialize the FaceAnalyzer
analyzer = BodyAnalyzer()

# Create FastAPI app
app = FastAPI(
    title="Body Shape and Proportion Analyzer API",
    description="API for analyzing body shape and proportions from images",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define input model
class ImageRequest(BaseModel):
    url: HttpUrl


# Define response models
class BodyAnalysisResponse(BaseModel):
    body_shape: str
    body_proportion: str
    body_image_url: HttpUrl


class DetailedBodyAnalysisResponse(BodyAnalysisResponse):
    shape_details: Optional[Dict[str, Any]]
    proportion_details: Optional[Dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "body_shape": "Hourglass/Rectangle",
                "body_proportion": "Balanced",
                "shape_details": {
                    "description": "Your shoulders and hips are balanced in proportion.",
                    "characteristics": [
                        "Balanced shoulder and hip measurements",
                        "Proportional upper and lower body",
                    ],
                    "clothing_tips": [
                        "Most styles work well with your balanced proportions",
                        "Experiment with different silhouettes to determine your preference",
                    ],
                },
                "proportion_details": {
                    "description": "Your torso and legs are in balanced proportion to each other.",
                    "clothing_tip": "Most clothing styles work well for your balanced proportions.",
                },
            }
        }


class ErrorResponse(BaseModel):
    detail: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": "Body Analyzer API is running"}


@app.post("/analyze")
async def analyze_body(image_data: ImageRequest):
    """
    Analyze body shape and proportion from an image URL.

    Parameters:
    - **url**: URL of the image to analyze (must be accessible)

    Returns body shape and proportion analysis.
    """
    try:
        # Convert pydantic HttpUrl to string
        image_url = str(image_data.url)
        result = analyzer.analyze(image_url)
        validated_response = BodyAnalysisResponse(**result)
        return validated_response
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"status_code": "422", "message": f"{str(e)}"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    # Perform minimal analysis as a health check
    return {
        "status": "healthy",
        "details": {
            "api_version": "1.0.0",
            "shape_categories": [
                "Hourglass/Rectangle",
                "Pear/Triangle",
                "Inverted Triangle",
            ],
            "proportion_categories": ["Balanced", "Long Torso", "Long Legs"],
        },
    }


# Run the app with uvicorn when executed directly
if __name__ == "__main__":

    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))

    # Run the app with uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=port)
