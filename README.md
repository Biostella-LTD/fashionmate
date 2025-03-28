# FASHION-MATE

A comprehensive fashion analysis platform consisting of four specialized AI-powered microservices:

1. **Cloth Analyzer** - Analyzes clothing items and attributes
2. **Body Analyzer** - Determines body shape and proportions
3. **Face Analyzer** - Identifies face shape, features, and characteristics
4. **Outfit Analyzer** - Recommends personalized outfits based on user's wardrobe

## Service Overview

| Service | Description | API Endpoint |
|---------|-------------|--------------|
| Cloth Analyzer | Identifies clothing items, materials, patterns, and colors | `/analyze` |
| Body Analyzer | Analyzes body shapes, proportions, and measurements | `/analyze` |
| Face Analyzer | Determines face shape, eye shape, skin tone, and hair color | `/analyze` |
| Outfit Analyzer | Generates outfit recommendations based on user profile | `/analyze` |

Each service has its own dedicated README with detailed documentation.


## Architecture

```
                          ┌─────────────────┐
                          │ Frontend Client │
                          └────────┬────────┘
                                   │
                   ┌───────────────┴──────────────┐
                   │                              │
            ┌──────▼─────┐                  ┌─────▼──────┐
┌───────────┤ API Gateway├────────────┐     │ Azure Blob │
│           └──────┬─────┘            │     │  Storage   │
│                  │                  │     └────────────┘
│    ┌─────────────┼─────────────┐    │
│    │             │             │    │
┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐   ┌─────────────┐
│   Face   │  │   Body   │  │  Cloth   │   │   Outfit    │
│ Analyzer │  │ Analyzer │  │ Analyzer │   │   Analyzer  │
└─────┬────┘  └─────┬────┘  └─────┬────┘   └──────┬──────┘
      │             │             │               │
┌─────▼─────────────▼─────────────▼───────────────▼─────┐
│                    Azure OpenAI                       │
└───────────────────────────────────────────────────────┘
```

## Development

Each service is maintained as a separate microservice with its own codebase, dependencies, and deployment pipeline. See the individual service READMEs for development instructions.

## Deployment

All services are containerized and deployed in Kubernetes. Environment variables, including API keys, are managed as Kubernetes secrets.

```bash
# Example for creating Azure OpenAI secrets
kubectl create secret generic azure-ai-service-secrets \
  --from-literal=AZURE_OPENAI_ENDPOINT="https://your-endpoint.com" \
  --from-literal=AZURE_OPENAI_KEY="your-key" \
  --from-literal=AZURE_SEARCH_ENDPOINT="https://your-search.com" \
  --from-literal=AZURE_SEARCH_KEY="your-search-key"
```

## Service Health Checks

All services provide a health check endpoint:

```bash
curl http://service-address/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0"
}
```