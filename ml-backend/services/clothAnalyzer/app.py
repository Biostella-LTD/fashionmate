import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from src.cloth_analyzer import ClothAnalyzer
from src.utils import logger

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")


# Define input model
class ImageUrl(BaseModel):
    url: HttpUrl


class ClothAnalysisResponse(BaseModel):
    type: str
    color: str
    pattern: str
    fabric: str
    description: str
    image_url: HttpUrl
    created_at: int


# Create FastAPI app
app = FastAPI(
    title="Cloth Analyzer",
    description="API for analyzing cloth images",
    version="1.0.0",
)


analyzer = ClothAnalyzer(
    openai_api_key=AZURE_OPENAI_KEY,
    openai_endpoint=AZURE_OPENAI_ENDPOINT,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    openai_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": f"{app.title} v{app.version} is running"}


@app.post("/analyze")
async def analyze_clothing(image_data: ImageUrl):
    try:
        image_url = str(image_data.url)

        logger.info(f"Analyzing cloth image from URL: {image_url}")

        result = analyzer.analyze_image(
            image_url,
            prompt="Analyze this image and return the following information in JSON format:\n"
            "1. type - one from top, bottom, outwear, footwear, accessory\n"
            "2. color - Detailed color description\n"
            "3. pattern - Pattern or design characteristics\n"
            "4. fabric - Fabric type\n"
            "5. description - Overall description",
        )

        validated_response = ClothAnalysisResponse(**result)
        return validated_response

    except Exception as e:
        logger.exception(e)
        return {"status_code": "422", "message": f"{str(e)}"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"{app.title} v{app.version} starting on {port=}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
