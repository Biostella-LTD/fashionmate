"""
Centralized configuration for the Outfit Analyzer service.
All environment variables and settings should be accessed through this module.
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


# Azure OpenAI Completion configuration (might be separate service)
AZURE_OPENAI_COMPLETION_ENDPOINT = os.getenv(
    "AZURE_OPENAI_COMPLETION_ENDPOINT", AZURE_OPENAI_ENDPOINT
)
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", AZURE_OPENAI_KEY)
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT_NAME", AZURE_OPENAI_DEPLOYMENT
)

# Azure Search configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")

# Template configuration
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
SEARCH_TEMPLATE = os.getenv("SEARCH_TEMPLATE", "fashion-prompt-template.j2")
SUMMARY_TEMPLATE = os.getenv("SUMMARY_TEMPLATE", "fashion-summary-template.j2")

# Data paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
