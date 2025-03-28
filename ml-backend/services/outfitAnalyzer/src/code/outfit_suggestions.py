import json
import re
from typing import Any, Dict, List

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from jinja2 import Environment, FileSystemLoader
from src.config import (
    AZURE_OPENAI_COMPLETION_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_KEY,
    TEMPLATE_DIR,
)

from ..exceptions import BadRequestError, ServerError
from .utils import logger


def create_openai_client() -> ChatCompletionsClient:
    """Create Azure OpenAI client for completions"""
    try:
        client = ChatCompletionsClient(
            endpoint=AZURE_OPENAI_COMPLETION_ENDPOINT,
            credential=AzureKeyCredential(AZURE_OPENAI_KEY),
        )

        return client

    except Exception as e:
        logger.error(f"Error creating OpenAI client: {str(e)}")
        raise ServerError("openai_client", f"Failed to create OpenAI client: {str(e)}")


def render_suggestion_template(
    search_results: List[Dict[str, Any]],
    user_features: Dict[str, Any],
    occasion: str,
    template_name: str = "fashion-summary-template.j2",
) -> str:
    """Render template for outfit suggestion prompt"""
    try:
        # Set up Jinja environment and load template
        jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = jinja_env.get_template(template_name)

        # Render the template
        prompt = template.render(
            search_results=search_results,
            user_features=user_features,
            occasion=occasion,
        )

        if not prompt:
            raise BadRequestError(
                "template_rendering", "Template rendering produced empty result"
            )

        return prompt

    except Exception as e:
        logger.error(f"Error rendering suggestion template: {str(e)}")
        raise BadRequestError(
            "template_rendering", f"Error rendering suggestion template: {str(e)}"
        )


def generate_outfit_suggestion(client: ChatCompletionsClient, prompt: str) -> str:
    """Generate outfit suggestion using Azure OpenAI"""
    try:
        # Call Azure OpenAI service
        response = client.complete(
            messages=[
                SystemMessage(
                    content="You are a fashion expert specialized in creating personalized outfit recommendations."
                ),
                UserMessage(content=prompt),
            ],
            max_tokens=4096,
            temperature=0.7,
            top_p=0.95,
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
        )

        suggestion = response.choices[0].message.content
        return suggestion

    except Exception as e:
        logger.error(f"Error generating outfit suggestion: {str(e)}")
        raise ServerError(
            "outfit_generation", f"Error generating outfit suggestion: {str(e)}"
        )


def parse_suggestion_response(suggestion_text: str) -> Dict[str, Any]:
    """Parse the suggestion response to extract JSON data"""
    try:
        # Look for JSON code block
        json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, suggestion_text)

        if match:
            json_str = match.group(1)
        else:
            # If no code block, try to find JSON-like structure
            json_pattern = r"(\{[\s\S]*\})"
            match = re.search(json_pattern, suggestion_text)

            if match:
                json_str = match.group(1)
            else:
                raise BadRequestError(
                    "json_parsing", "Could not find JSON data in the response"
                )

        # parse outfit items in a json format
        outfit_data = json.loads(json_str)
        return outfit_data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise BadRequestError("json_parsing", f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing suggestion response: {str(e)}")
        raise BadRequestError(
            "response_parsing", f"Error parsing suggestion response: {str(e)}"
        )
