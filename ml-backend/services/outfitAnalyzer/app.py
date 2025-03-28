import json
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from src.code.outfit_service import generate_outfit_recommendation

# Import outfit service and logger
from src.code.outfit_with_wardrobe import WardrobeItem
from src.code.utils import logger
from src.exceptions import (
    BadRequestError,
    HTTPError,
    NotFoundError,
    ServerError,
    ValidationError,
)


class OutfitRequest(BaseModel):
    """Request model for outfit recommendation"""

    user_id: str = Field(..., description="User's unique identifier")
    occasion: str = Field(
        ..., description="The occasion for the outfit (e.g., 'business meeting')"
    )
    user_features: Dict[str, Any] = Field(
        ..., description="User's physical and style characteristics"
    )
    wardrobe: List[WardrobeItem] = Field(
        [], description="List of user's wardrobe items"
    )


# Create FastAPI app
app = FastAPI(
    title="outfitAnalyzer Service",
    description="Fashion outfit recommendation service",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(HTTPError)
async def http_exception_handler(request: Request, exc: HTTPError):
    """Handle custom HTTP exceptions"""
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "error": "internal_error",
            "message": "Internal server error",
        },
    )


# Root endpoint for basic health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the outfit analyzer service"""
    return {
        "status": "healthy",
        "service": "outfit-analyzer",
        "version": "1.0.0",
    }


# Outfit recommendation endpoint
@app.post("/analyze")
async def recommend_outfit(request_data: OutfitRequest):
    """
    Generate outfit recommendation based on user features, occasion, and wardrobe

    This endpoint processes the user's profile, wardrobe, and the specified occasion
    to generate personalized outfit recommendations with matches from the user's
    actual wardrobe.

    Returns:
        A recommendation object containing:
        - user_id: The user's identifier
        - occasion: The occasion for the outfit
        - outfit_recommendations: List of suggested outfit combinations
        - wardrobe_matches: List of matches between suggestions and actual wardrobe items
    """
    try:
        logger.info(
            f"Received outfit recommendation request for user {request_data.user_id}"
        )
        logger.info(f"Occasion: {request_data.occasion}")

        wardrobe_items = [item for item in request_data.wardrobe]
        logger.info(f"Wardrobe items: {len(request_data.wardrobe)}")
        # Generate outfit recommendation
        recommendation = generate_outfit_recommendation(
            user_id=request_data.user_id,
            occasion=request_data.occasion,
            user_features=request_data.user_features,
            wardrobe_items=wardrobe_items,
        )

        logger.info(
            f"Successfully generated recommendation for user {request_data.user_id}"
        )
        return recommendation

    except HTTPError as e:
        # Custom HTTP exceptions are handled by the exception handler
        logger.warning(f"HTTP error in recommend_outfit: {str(e)}")
        raise
    except Exception as e:
        # Log and convert other exceptions to ServerError
        logger.error(f"Error in recommend_outfit: {str(e)}")
        raise ServerError(
            "recommend_outfit", f"Error generating outfit recommendation: {str(e)}"
        )


# Main entry point
if __name__ == "__main__":
    import uvicorn

    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))

    logger.info(f"Starting outfitAnalyzer Service on port {port}")

    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=port)
