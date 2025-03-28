# Outfit Analyzer Service

The Outfit Analyzer is an AI-powered service that generates personalized outfit recommendations based on a user's wardrobe, physical characteristics, and a specified occasion.

## Project Structure

```bash
outfitAnalyzer/
├── src/
│   ├── code/
│   │   ├── __init__.py
│   │   ├── ai_search.py             # AI-powered fashion reference search
│   │   ├── outfit_service.py        # Core outfit recommendation service
│   │   ├── outfit_suggestions.py    # Outfit suggestion generation
│   │   ├── outfit_with_wardrobe.py  # Matches suggested outfits with user's wardrobe
│   │   └── utils.py                 # Utility functions and logging
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── http_exceptions.py       # Custom HTTP exceptions
│   ├── templates/                   # Jinja2 templates
│   │   ├── fashion-prompt-template.j2     # Template for search queries
│   │   └── fashion-summary-template.j2    # Template for outfit suggestions
│   ├── __init__.py  
│   └──config.py                       # Configuration settings
├── tests/
│   ├── data/
│   │   ├── user_features.json       # Test user profile data
│   │   └── wardrobe.json            # Test wardrobe items
│   ├── __init__.py
│   └── test_app_service.py
├── app.py                          # FastAPI application
├── requirements.txt                # Python dependencies
├── deployment.yaml                 # Kubernetes deployment
├── Dockerfile                      # Docker configuration
└── README.md                       # This file
```

## Features

- **AI-Powered Outfit Recommendations**: Uses Azure OpenAI to generate personalized outfit suggestions
- **Semantic Fashion Search**: Leverages Azure AI Search for finding relevant fashion advice
- **Wardrobe Matching**: Intelligently matches suggested outfits with items from the user's actual wardrobe
- **Occasion-Specific Recommendations**: Tailors outfit recommendations to specific occasions (business meetings, casual events, etc.)
- **Personalized Styling**: Takes into account user's physical features, style preferences, and body characteristics

## Configuration

The service uses a centralized configuration module (`config.py`) that loads required settings from environment variables. All components of the application read configuration values from this module for consistent settings management.

### Required Environment Variables

The following environment variables must be set for the service to function properly:

#### Azure OpenAI Configuration
- `AZURE_OPENAI_ENDPOINT`: The endpoint URL for your Azure OpenAI service
- `AZURE_OPENAI_KEY`: Your API key for the Azure OpenAI service
- `AZURE_OPENAI_DEPLOYMENT_NAME`: The deployment name of your Azure OpenAI model

#### Azure AI Search Configuration
- `AZURE_SEARCH_ENDPOINT`: The endpoint URL for your Azure AI Search service
- `AZURE_SEARCH_KEY`: Your API key for Azure AI Search
- `AZURE_SEARCH_INDEX`: The name of your search index (defaults to "magzine_lite")

### Template Configuration

The service uses Jinja2 templates for generating search queries and outfit suggestions. The templates are located in the `src/templates` directory:

- `fashion-prompt-template.j2`: Template for generating search queries
- `fashion-summary-template.j2`: Template for generating outfit suggestions

### Data Directory

The service uses a `data` directory for storing intermediate results during processing. This directory is automatically created if it doesn't exist.

## API Reference

### Generate Outfit Recommendation

Endpoint for generating personalized outfit recommendations based on user features, wardrobe, and occasion.

#### Request Body

```json
{
  "user_id": "user-1234",
  "occasion": "business meeting",
  "user_features": {
    "height_cm": 175,
    "weight_kg": 70,
    "age": 32,
    "gender": "male",
    "style": "professional",
    "body_shape": "athletic",
    "body_proportion": "balanced",
    "face_shape": "oval",
    "eye_shape": "almond",
    "skin_tone": "medium warm",
    "hair_color": "brown"
  },
  "wardrobe": [
    {
      "user_id": "user-1234",
      "item_id": "item-00001",
      "type": "Top",
      "color": "White",
      "pattern": "mono",
      "fabric": "cotton",
      "description": "White cotton button-down shirt",
      "image_url": "https://storage.example.com/user-1234/wardrobe/item-00001.jpg",
      "created_at": 1710864000000
    },
    {
      "user_id": "user-1234",
      "item_id": "item-00011",
      "type": "Bottom",
      "color": "Navy",
      "pattern": "mono",
      "fabric": "cotton",
      "description": "Navy chino pants",
      "image_url": "https://storage.example.com/user-1234/wardrobe/item-00011.jpg",
      "created_at": 1711728000000
    }
    // Additional wardrobe items...
  ]
}
```

#### Response

```json
{
  "user_id": "user-1234",
  "occasion": "business meeting",
  "best_match": {
    "outfit_name": "matching1",
    "total_score": 32.5,
    "items": [
      {
        "user_id": "user-1234",
        "item_id": "item-00001",
        "type": "Top",
        "color": "White",
        "pattern": "mono",
        "fabric": "cotton",
        "description": "White cotton button-down shirt",
        "image_url": "https://storage.example.com/user-1234/wardrobe/item-00001.jpg",
        "created_at": 1710864000000,
        "match_score": 8.5,
        "suggestion": {
          "type": "Top",
          "description": "Crisp white button-down shirt",
          "color": "White",
          "fabric": "cotton",
          "pattern": "mono"
        }
      },
      // Additional matched items...
    ]
  },
  "all_matches": [
    // All outfit matches with scores and details...
  ]
}
```

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with the required environment variables:
   ```bash
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT="https://your-azure-openai-endpoint.com"
   AZURE_OPENAI_KEY="your-azure-openai-key"
   AZURE_OPENAI_DEPLOYMENT_NAME="your-model-deployment-name"
   
   # Azure AI Search Configuration
   AZURE_SEARCH_ENDPOINT="https://your-azure-search-endpoint.com"
   AZURE_SEARCH_KEY="your-azure-search-key"
   AZURE_SEARCH_INDEX="your-search-index-name"
   ```

3. Verify your environment setup:
   ```bash
   python check_env.py
   ```

4. Run the service:
   ```bash
   uvicorn app:app --reload
   ```

5. Test the service:
   ```bash
   python tests/test_app_service.py
   ```

## Deployment

### Docker

Build and run the Docker container:

```bash
docker build -t outfit-analyzer:latest .
docker run -p 8000:8000
  -e AZURE_OPENAI_ENDPOINT="https://your-endpoint.com"
  -e AZURE_OPENAI_KEY="your-key"
  -e AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"
  -e AZURE_SEARCH_ENDPOINT="https://your-search.com"
  -e AZURE_SEARCH_KEY="your-search-key"
  outfit-analyzer:latest
```

### Kubernetes

Deploy to Kubernetes:

```bash
# Create secrets for Azure services
kubectl create secret generic azure-ai-service-secrets \
  --from-literal=AZURE_OPENAI_ENDPOINT="https://your-azure-openai-endpoint.com" \
  --from-literal=AZURE_OPENAI_KEY="your-azure-openai-key" \
  --from-literal=AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name" \
  --from-literal=AZURE_SEARCH_ENDPOINT="https://your-azure-search-endpoint.com" \
  --from-literal=AZURE_SEARCH_KEY="your-azure-search-key" \
  --from-literal=AZURE_SEARCH_INDEX="your-search-index"

# Apply deployment configuration
kubectl apply -f deployment.yaml
```

Make sure your `deployment.yaml` includes the correct environment variable references:

```yaml
env:
  - name: AZURE_OPENAI_ENDPOINT
    valueFrom:
      secretKeyRef:
        name: azure-ai-service-secrets
        key: AZURE_OPENAI_ENDPOINT
  - name: AZURE_OPENAI_KEY
    valueFrom:
      secretKeyRef:
        name: azure-ai-service-secrets
        key: AZURE_OPENAI_KEY
  # Add remaining environment variables...
```

## Example Usage

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-1234",
    "occasion": "business meeting",
    "user_features": {
      "height_cm": 175,
      "weight_kg": 70,
      "age": 32,
      "gender": "male",
      "style": "professional",
      "body_shape": "athletic"
    },
    "wardrobe": [
      {
        "user_id": "user-1234",
        "item_id": "item-00001",
        "type": "Top",
        "color": "White",
        "pattern": "mono",
        "fabric": "cotton",
        "description": "White cotton button-down shirt",
        "image_url": "https://storage.example.com/user-1234/wardrobe/item-00001.jpg"
      },
      {
        "user_id": "user-1234",
        "item_id": "item-00011",
        "type": "Bottom",
        "color": "Navy",
        "pattern": "mono",
        "fabric": "cotton",
        "description": "Navy chino pants",
        "image_url": "https://storage.example.com/user-1234/wardrobe/item-00011.jpg"
      }
    ]
  }'
```

## Troubleshooting

### Common Issues

1. **Connection Errors to Azure Services**:
   - Verify that your API keys are correct
   - Check network connectivity from your deployment to Azure services
   - Ensure your Azure resources allow access from your deployment's IP address

2. **API Key Format Issues**:
   - Azure OpenAI keys should be in the format of a long string without spaces
   - Make sure there are no trailing spaces in your environment variables

3. **Missing Environment Variables**:
   - Run the `check_env.py` script to verify all required variables are set
   - In Kubernetes, check that all secrets are correctly created and mounted

4. **Template Errors**:
   - Ensure the template directory path is correct
   - Verify that template files exist in the expected location


## Testing

Tests are automated in GitHub CI/CD.

## License

This project is licensed under the MIT License - see the LICENSE file for details.