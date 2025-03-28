import os
import traceback
from typing import Any, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryType,
    VectorizedQuery,
)
from jinja2 import Environment, FileSystemLoader
from openai import AzureOpenAI
from src.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_INDEX,
    AZURE_SEARCH_KEY,
    TEMPLATE_DIR,
)

from ..exceptions import BadRequestError, ServerError
from .utils import logger

OPENAI_API_VERSION = "2024-02-15-preview"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_FIELD_NAME = "content_vector"
VECTOR_QUERY_KNN = 3
SEMANTIC_CONFIG_NAME = "semantic_search_v1"
EXHAUSTIVE = False
N_TOP_CONTENTS = 10


def generate_search_query(
    user_features: Dict[str, Any],
    occasion: str,
    template_name: str = "fashion-prompt-template.j2",
) -> str:
    """Generate a search query based on user features using the template"""
    try:
        logger.info(f"Generating search query for occasion: {occasion}")
        logger.debug(f"Template directory: {TEMPLATE_DIR}")
        logger.debug(f"Template name: {template_name}")

        # Set up Jinja environment and load template
        jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = jinja_env.get_template(template_name)

        logger.info("Template loaded successfully")

        # Render the template
        query_text = template.render(user_features=user_features, occasion=occasion)

        logger.debug(
            f"Generated query text: {query_text[:100]}..."
        )  # Log the first 100 chars

        if not query_text:
            logger.error("Generated query text is empty")
            raise BadRequestError(
                "query_generation", "Failed to generate query from template"
            )

        logger.info(f"Successfully generated search query of length {len(query_text)}")
        return query_text

    except Exception as e:
        logger.error(f"Error generating search query: {str(e)}")
        logger.error(traceback.format_exc())
        raise BadRequestError(
            "query_generation", f"Error generating search query: {str(e)}"
        )


def generate_embedding(query_text: str) -> List[float]:
    """Generate embeddings for the query text using Azure OpenAI"""
    try:
        # Log configuration data
        logger.info("Generating embeddings using Azure OpenAI")
        logger.debug(f"AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
        logger.debug(f"OPENAI_API_VERSION: {OPENAI_API_VERSION}")
        logger.debug(f"Using embedding model: {EMBEDDING_MODEL}")
        logger.debug(f"Query text length: {len(query_text)}")

        # Check if the API key is set
        if not AZURE_OPENAI_KEY:
            logger.error("AZURE_OPENAI_KEY is not set or empty")
            raise ValueError("AZURE_OPENAI_KEY is not set or empty")

        # Configure the Azure OpenAI client
        logger.info("Initializing Azure OpenAI client")
        azure_openai = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version=OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

        logger.info("Azure OpenAI client initialized successfully")

        # Generate embeddings
        logger.info("Calling embeddings.create API")
        response = azure_openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query_text,
        )

        logger.info("Successfully received embedding response")
        embeddings = response.data[0].embedding

        logger.info(f"Generated embeddings of dimension: {len(embeddings)}")
        return embeddings

    except ValueError as e:
        logger.error(f"Value error generating embeddings: {str(e)}")
        logger.error(traceback.format_exc())
        raise ServerError("embedding_generation", f"Configuration error: {str(e)}")
    except ConnectionError as e:
        logger.error(f"Connection error with Azure OpenAI: {str(e)}")
        logger.error(traceback.format_exc())
        raise ServerError(
            "embedding_generation", f"Connection error to Azure OpenAI: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        logger.error(traceback.format_exc())
        raise ServerError(
            "embedding_generation", f"Error generating embeddings: {str(e)}"
        )


def search_fashion_references(
    query_text: str, question_vector: List[float]
) -> List[Dict[str, Any]]:
    """Search for fashion references using both text and vector search"""
    try:
        logger.info("Searching for fashion references")
        logger.debug(f"AZURE_SEARCH_ENDPOINT: {AZURE_SEARCH_ENDPOINT}")
        logger.debug(f"AZURE_SEARCH_INDEX: {AZURE_SEARCH_INDEX}")
        logger.debug(f"Vector dimension: {len(question_vector)}")

        # Check if the API key is set
        if not AZURE_SEARCH_KEY:
            logger.error("AZURE_SEARCH_KEY is not set or empty")
            raise ValueError("AZURE_SEARCH_KEY is not set or empty")

        # Create an Azure AI Search client
        logger.info("Initializing Azure AI Search client")
        search_client = SearchClient(
            AZURE_SEARCH_ENDPOINT,
            AZURE_SEARCH_INDEX,
            AzureKeyCredential(AZURE_SEARCH_KEY),
        )

        logger.info("Azure AI Search client initialized successfully")

        # Create a vectorized query
        logger.info("Creating vectorized query")
        vector_query = VectorizedQuery(
            vector=question_vector,
            k_nearest_neighbors=VECTOR_QUERY_KNN,
            fields=VECTOR_FIELD_NAME,
            exhaustive=EXHAUSTIVE,
        )

        logger.info("Executing search query")
        # Perform a hybrid search (text and vector) with semantic ranking
        results = search_client.search(
            search_text=query_text,
            vector_queries=[vector_query],
            select=["id", "content"],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name=SEMANTIC_CONFIG_NAME,
            query_caption=QueryCaptionType.EXTRACTIVE,
            query_answer=QueryAnswerType.EXTRACTIVE,
            top=N_TOP_CONTENTS,
        )

        logger.info("Search query executed successfully")

        # Process search results
        context_data = []
        count = 0

        logger.info("Processing search results")
        for result in results:
            count += 1
            context_data.append(
                {
                    "id": result.get("id", ""),
                    "content": result["content"],
                    "searcher_score": result["@search.score"],
                }
            )

        logger.info(f"Retrieved {count} search results")
        if count > 0:
            logger.debug(
                f"First result: {context_data[0]['id']}, score: {context_data[0]['searcher_score']}"
            )

        return context_data

    except ValueError as e:
        logger.error(f"Value error in search: {str(e)}")
        logger.error(traceback.format_exc())
        raise ServerError("search_execution", f"Configuration error: {str(e)}")
    except ConnectionError as e:
        logger.error(f"Connection error with Azure AI Search: {str(e)}")
        logger.error(traceback.format_exc())
        raise ServerError(
            "search_execution", f"Connection error to Azure AI Search: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error searching for fashion references: {str(e)}")
        logger.error(traceback.format_exc())
        raise ServerError(
            "search_execution", f"Error searching for fashion references: {str(e)}"
        )
