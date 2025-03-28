# Face Analyzer Service

A microservice that analyzes facial features from images to extract key attributes of a person's face.

## Overview

This service provides an API for analyzing facial features from images and extracting key attributes such as:
- Face shape (Oval, Round, Square, Oblong)
- Eye shape (Almond, Round, Upturned, Downturned, etc.)
- Skin tone
- Hair color

The service uses computer vision techniques and facial landmark detection to provide accurate facial analysis.

## Getting Started

### Prerequisites

- Python 3.9+
- OpenCV
- dlib (with facial landmark predictor)
- Docker (optional)

### Installation

#### Local Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd faceAnalyzer
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

4. Download the shape predictor model:
   ```bash
   mkdir -p src/model
   # Download the model file and place it in src/model/
   # shape_predictor_68_face_landmarks.dat
   ```

5. Set up environment variables:
   ```bash
   # Create a .env file
   echo "PREDICTOR_PATH=src/model/shape_predictor_68_face_landmarks.dat" > .env
   echo "BLOB_TOKEN=your_azure_blob_token" >> .env
   ```

6. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

#### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t face-analyzer .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 \
     -e PREDICTOR_PATH=/app/src/model/shape_predictor_68_face_landmarks.dat \
     face-analyzer
   ```

### Kubernetes Deployment

Deploy to Kubernetes using the provided deployment.yaml file:

```bash
kubectl apply -f deployment.yaml
```

## API Endpoints

### Analyze Face

Analyzes facial features and characteristics.

```bash
curl -X POST http://0.0.0.0:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://as1.ftcdn.net/v2/jpg/04/66/44/64/1000_F_466446411_VYFCWgiDL7LkWsdcRaG3aX8aCfe7jpMu.jpg"}'
```

**Response:**
```json
{
    "user_id": "Unknown",
    "face_shape": "Round",
    "eye_shape": "Downturned",
    "skin_tone": "Tan Warm",
    "hair_color": "Blonde"
}
```

## File Structure

```
faceAnalyzer/
├── src/
│   ├── __init__.py
│   ├── analysis_exceptions.py  # Custom exceptions
│   ├── face_analyzer.py     # Main analyzer class
│   ├── face_shape.py    # Face shape detection
│   ├── eye_shape.py     # Eye shape detection
│   ├── skin_tone.py     # Skin tone analysis
│   ├── hair_color.py    # Hair color detection
│   ├── utils.py         # Utility functions
│   ├── model/
│       └── shape_predictor_68_face_landmarks.dat  # Facial landmark model 
├── tests/
│   ├── __init__.py
│   └── test_face_analyzer.py
├── app.py                   # FastAPI application
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── deployment.yaml          # Kubernetes deployment
└── README.md                # This file
```

## How It Works

The face analysis process follows these steps:

1. **Image Download**: Service downloads an image from the provided URL
2. **Face Detection**: Locates faces in the image
3. **Landmark Detection**: Identifies 68 facial landmarks on the detected face
4. **Feature Analysis**:
   - Uses landmark relationships to determine face shape
   - Analyzes eye landmarks for eye shape
   - Samples skin pixels to determine skin tone
   - Analyzes hair region to determine hair color
5. **Response Generation**: Returns structured facial attributes

## Testing

Run the test script to verify analyzer functionality:

```bash
python -m tests.test_face_analyzer
```

The tests include sample images of different face shapes and features to validate the analysis accuracy.

## Azure Blob Storage Integration

The service supports analyzing images stored in Azure Blob Storage. Use the configuration module to securely handle blob URLs and tokens.

## License

This project is licensed under the MIT License - see the LICENSE file for details.