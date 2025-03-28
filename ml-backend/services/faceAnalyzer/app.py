import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from src.face_analyzer import FaceAnalyzer
from src.utils import logger

# Get path to the predictor file
PREDICTOR_PATH = os.getenv("PREDICTOR_PATH")

# Initialize the FaceAnalyzer
analyzer = FaceAnalyzer(PREDICTOR_PATH)

# Create FastAPI app
app = FastAPI(
    title="Face Analyzer API",
    description="API for analyzing facial features from images",
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
class ImageUrl(BaseModel):
    url: HttpUrl


# Define response model
class FaceAnalysisResponse(BaseModel):
    face_shape: str
    eye_shape: str
    skin_tone: str
    hair_color: str
    face_image_url: HttpUrl


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": "Face Analyzer API is running"}


@app.post("/analyze")
async def analyze_face(image_data: ImageUrl):
    """
    Analyze facial features from an image URL

    - **url**: URL of the image to analyze (must be accessible)

    Returns face shape, eye shape, skin tone, and hair color analysis
    """
    # Convert pydantic HttpUrl to string
    image_url = str(image_data.url)

    try:
    # Analyze the image
        result = analyzer.analyze(image_url)
        validated_response = FaceAnalysisResponse(**result)
        return validated_response
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"status_code": "422", "message": f"{str(e)}"}



@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    # Check if the predictor file exists
    if analyzer.landmark_predictor_path is not None:
        predictor_path = str(analyzer.landmark_predictor_path )
    else:
        predictor_path = "not_found"

    status =  "healthy" if predictor_path != "not_found" else "unhealthy"

    return {
        "status": status,
        "message": f"{app.title} v{app.version} running, predictor_path = {predictor_path}",
    }


# Run the app with uvicorn when executed directly
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))

    # Run the app with uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
