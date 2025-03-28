import json
import os
from typing import Any, Dict, List, Optional

from src.code.outfit_with_wardrobe import WardrobeItem
from src.config import DATA_DIR

from ..exceptions import BadRequestError
from .ai_search import (
    generate_embedding,
    generate_search_query,
    search_fashion_references,
)
from .outfit_suggestions import (
    create_openai_client,
    generate_outfit_suggestion,
    parse_suggestion_response,
    render_suggestion_template,
)
from .outfit_with_wardrobe import match_outfit_with_wardrobe
from .utils import logger

# Set the occasion for testing
OCCASION = "networking event"


def generate_outfit_recommendation(
    user_id: str,
    occasion: str,
    user_features: Dict[str, Any],
    wardrobe_items: WardrobeItem,
    data_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate outfit recommendation for a user

    Args:
        user_id: User's unique identifier
        occasion: The occasion for the outfit
        user_features: User's physical and style characteristics
        wardrobe_items: List of user's wardrobe items
        data_dir: Directory to save intermediate results

    Returns:
        Complete outfit recommendation with wardrobe matches
    """
    try:
        logger.info(
            f"Generating outfit recommendation for user {user_id}, occasion: {occasion}"
        )

        # Set up data directory for saving intermediates
        if not data_dir:
            data_dir = DATA_DIR
        os.makedirs(data_dir, exist_ok=True)

        # Step 1: Find relevant fashion advice using AI search
        logger.info("Step 1: Finding relevant fashion advice")
        query_text = generate_search_query(user_features, occasion)
        query_embedding = generate_embedding(query_text)  # Generate embeddings
        search_results = search_fashion_references(query_text, query_embedding)

        # Check if we have search results
        if not search_results:
            logger.warning(" --> No relevant fashion advice found")
            raise BadRequestError(
                "search_results", "No relevant fashion advice found for this occasion"
            )
        else:
            logger.info(f" --> Found {len(search_results)} relevant fashion references")

        # Step 2: Create outfit suggestion
        logger.info("Step 2: Creating outfit suggestion")
        client = create_openai_client()  # Create OpenAI client
        prompt = render_suggestion_template(search_results, user_features, occasion)
        suggestion_text = generate_outfit_suggestion(client, prompt)
        outfit_suggestion = parse_suggestion_response(suggestion_text)

        # Check if we have a valid outfit suggestion with the expected structure
        if not outfit_suggestion:
            logger.warning(" --> Empty outfit suggestion generated")
            raise BadRequestError(
                "outfit_suggestion", "Failed to generate outfit suggestion"
            )
        else:
            logger.info(" --> Generated outfit suggestions (multiple outfit found)")

        # Step 3: Match outfit with wardrobe
        logger.info("Step 3: Matching outfit with wardrobe")
        outfit_matches = match_outfit_with_wardrobe(outfit_suggestion, wardrobe_items)

        # FIND THE HIGHEST SCORE "total_score"
        highest_score_outfit = max(outfit_matches, key=lambda x: x["total_score"])
        # GET THE LIST OF item_ids FROM matched_items
        best_item_ids = [
            item["item_id"] for item in highest_score_outfit["matched_items"]
        ]
        # GET full wardrobe items based on best_item_ids
        best_items = [item for item in wardrobe_items if item.item_id in best_item_ids]
        # Step 4: Prepare the final recommendation
        recommendation = {
            "user_id": user_id,
            "occasion": occasion,
            "outfit": best_items,
        }
        logger.info(" --> best outfit generated.")
        return recommendation

    except Exception as e:
        logger.exception(f" --> Error generating outfit recommendation: {str(e)}")
        raise
