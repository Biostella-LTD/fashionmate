# Body Analyzer Service

A microservice that analyzes body shape and proportions from images using MediaPipe pose detection.

## Overview

This service provides an API for determining body shape classifications and proportions based on uploaded images. It uses MediaPipe for pose detection and custom algorithms to analyze body shapes and proportions.

Body shape classifications:
- Hourglass/Rectangle
- Pear/Triangle
- Inverted Triangle

Body proportion classifications:
- Balanced
- Long Torso
- Long Legs

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (optional)

### Installation

#### Local Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bodyAnalyzer
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

4. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

#### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t body-analyzer .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 body-analyzer
   ```

### Kubernetes Deployment

Deploy to Kubernetes using the provided deployment.yaml file:

```bash
kubectl apply -f deployment.yaml
```

## API Endpoints

### Basic Analysis

Example request body for production:
```
curl -X POST http://135.224.234.241/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://media.istockphoto.com/id/523150985/photo/full-body-portrait-of-a-handsome-young-man-smiling.jpg?s=612x612&w=0&k=20&c=dWBzZLrPBOkzk3LG7CKMUPCMe40cWclIidOvNg2_mVw="}'
```
Response:
```json
{
  "body_shape":"Inverted Triangle",
  "body_proportion":"Long Legs"
}
```

## File Structure

```
bodyAnalyzer/
├── src/
│   ├── __init__.py
│   ├── analysis_exceptions.py
│   ├── body_analyzer.py
│   ├── body_proportions.py
│   ├── body_shape.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_body_analyzer.py
│   ├── test_body_analyzer_service.py
│   └── test_mediapipe.py
├── logs/
├── app.py                # FastAPI application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── deployment.yaml       # Kubernetes deployment
└── README.md             # This file
```

## Testing

Tests are automated in GitHub CI/CD.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
