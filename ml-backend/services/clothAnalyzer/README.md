# Cloth Analyzer Service

A microservice that analyzes clothing items from images using Azure AI Vision and OpenAI services.

## Overview

This service provides an API for analyzing clothing items from images and extracting key attributes such as:
- Type (top, bottom, outerwear, footwear, accessory)
- Color
- Pattern
- Fabric type
- Detailed description

The service leverages Azure OpenAI's vision capabilities to provide comprehensive clothing analysis with high accuracy.

## Getting Started

### Prerequisites

- Python 3.9+
- Azure OpenAI API credentials
- Docker (optional)

### Installation

#### Local Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd clothAnalyzer
   ```

2. Create a virtual environment (optional):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create a .env file
   echo "AZURE_AI_ENDPOINT=your_azure_endpoint" > .env
   echo "AZURE_AI_KEY=your_azure_key" >> .env
   ```

5. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

#### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t cloth-analyzer .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 \
     -e AZURE_AI_ENDPOINT=your_azure_endpoint \
     -e AZURE_AI_KEY=your_azure_key \
     cloth-analyzer
   ```

### Kubernetes Deployment

Deploy to Kubernetes using the provided deployment.yaml file:

```bash
kubectl apply -f deployment.yaml
```

## API Endpoints

### Analyze Clothing

Example request body for production:
```
curl -X POST http://[service-ip]/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://media.istockphoto.com/id/950050590/photo/violet-summer-skirt-with-buttons-isolated-on-white.jpg?s=1024x1024&w=is&k=20&c=T_AH29vBBlKlOL68S40O25HxRwZERy2puiU4zvteic4="}'
```
Response:
```json
{
  "type": "top",
  "color": "red",
  "pattern": "solid",
  "fabric": "cotton",
  "description": "A solid red short-sleeved t-shirt with a round neckline",
  "image_url": "https://cdn2.vectorstock.com/i/1000x1000/68/56/cloth-vector-28966856.jpg",
  "created_at": 1711180431
}
```

## File Structure

```
clothAnalyzer/
├── src/
│   ├── __init__.py
│   ├── cloth_analyzer.py  # Main analyzer class using Azure AI
│   └── utils.py           # Utility functions and logging
├── tests/
│   ├── data/
│   └── test_cloth_analyzer.py
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── deployment.yaml        # Kubernetes deployment
└── README.md              # This file
```

## How It Works

The service uses:
1. Azure OpenAI's vision capabilities to analyze clothing items
2. FastAPI for the web service framework
3. Pydantic for data validation and serialization

The analysis process:
1. Receives an image URL via the API
2. Sends the image to Azure OpenAI for analysis
3. Processes and formats the response
4. Returns structured clothing attributes

## Testing

Tests are automated in git CI/CD.

## License

This project is licensed under the MIT License - see the LICENSE file for details.