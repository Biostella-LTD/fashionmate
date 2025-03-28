import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field

from .utils import logger


# Define request/response models for better documentation and validation
class WardrobeItem(BaseModel):
    """Model for a wardrobe item"""

    item_id: str
    type: str
    color: Optional[str] = None
    pattern: Optional[str] = None
    fabric: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[int] = None


def normalize(text: str) -> str:
    """Normalize a string: lowercase and remove non-alphanumeric characters"""
    if not text:
        return ""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def get_text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity between two strings using SequenceMatcher"""
    if not text1 or not text2:
        return 0
    return SequenceMatcher(None, normalize(text1), normalize(text2)).ratio()


def get_match_score(
    summary_item: Dict[str, Any],
    wardrobe_item: WardrobeItem,
) -> float:
    """Compute a matching score between an outfit item and a wardrobe item"""

    # Get type/category from the correct field depending on which one exists
    summary_type = summary_item.get("type", summary_item.get("category", ""))

    if normalize(wardrobe_item.type) != normalize(summary_type):
        return -1  # No match if category/type differs

    score = 1  # Start with a score of 1 because the type/category already matched

    # Color matching (2 points)
    if normalize(wardrobe_item.color) == normalize(summary_item.get("color", "")):
        score += 2

    # Pattern matching (2 points)
    if normalize(wardrobe_item.pattern) == normalize(summary_item.get("pattern", "")):
        score += 4

    # Material matching (1.5 points)
    mat1 = normalize(wardrobe_item.fabric)
    mat2 = normalize(summary_item.get("fabric", ""))
    if mat1 and mat2 and (mat1 in mat2 or mat2 in mat1):
        score += 3

    # Description similarity (up to 1.5 points)
    desc_similarity = get_text_similarity(
        wardrobe_item.description, summary_item.get("description", "")
    )
    score += desc_similarity * 1.5

    return score


def find_best_match(
    suggested_item: WardrobeItem,
    wardrobe_items: List[WardrobeItem],
    used_items: Set[str],
    matching_set_items: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Optional[Dict[str, Any]], float]:
    """Find the best matching wardrobe item for a suggested outfit piece"""
    best_item = None
    highest_score = -1

    for item in wardrobe_items:

        if item.item_id not in used_items:
            # Get type/category from the correct field
            suggested_type = suggested_item["type"]

            if normalize(item.type) == normalize(suggested_type):
                # Basic score based on attributes
                score = get_match_score(suggested_item, item)

                # If we already have items in this matching set, check for description similarity
                if matching_set_items and score > 0:
                    # Penalize if description is too similar to anything already in this matching set
                    for matched_item in matching_set_items:
                        desc_similarity = get_text_similarity(
                            item.description,
                            matched_item.description,
                        )

                        # If descriptions are very similar (>0.7), reduce the score
                        if desc_similarity > 0.7:
                            score -= desc_similarity * 2

                if score > highest_score:
                    best_item = item
                    highest_score = score

    return best_item, highest_score


def match_outfit_with_wardrobe(
    outfit_suggestion: Dict[str, Any],
    wardrobe: List[WardrobeItem],
) -> Dict[str, Any]:
    """Match suggested outfit with items from user's wardrobe"""

    outfit_matches = []
    used_items = set()  # Track used items across all outfits

    # Check if outfit has the expected structure
    if "outfit_recommendations" not in outfit_suggestion:
        logger.warning("Outfit suggestion does not have the expected structure")
        return {"error": "Invalid outfit suggestion format"}

    # Get the clothing items from the recommendation
    for outfit in outfit_suggestion["outfit_recommendations"]:
        if "clothing_items" not in outfit:
            logger.warning("Outfit suggestion does not contain clothing items")
            return {"error": "No clothing items in outfit suggestion"}

        outfit_name = outfit["outfit_name"]
        clothing_items = outfit["clothing_items"]

        matched_items = []  # Items matched for this outfit
        matched_items_objects = []  # Full item objects for similarity checks
        total_score = 0

        for item in clothing_items:
            best_match, score = find_best_match(
                item,
                wardrobe,
                used_items,
                matched_items_objects,
            )

            if best_match:
                matched_items.append(
                    {
                        "item_id": best_match.item_id,
                        "description": best_match.description,
                        "type": best_match.type,
                        "color": best_match.color,
                        "fabric": best_match.fabric,
                        "score": score,
                        "suggestion": {
                            "type": item.get("type", ""),
                            "description": item.get("description", ""),
                            "color": item.get("color", ""),
                            "fabric": item.get("fabric", ""),
                            "pattern": item.get("pattern", ""),
                        },
                    }
                )
                matched_items_objects.append(best_match)
                used_items.add(best_match.item_id)
                total_score += score
            else:
                matched_items.append(
                    {
                        "item_id": None,
                        "description": "No match found",
                        "type": item.get("type", ""),
                        "score": -1,
                        "suggestion": {
                            "type": item.get("type", ""),
                            "description": item.get("description", ""),
                            "color": item.get("color", ""),
                            "fabric": item.get("fabric", ""),
                            "pattern": item.get("pattern", ""),
                        },
                    }
                )

        outfit_matches.append(
            {
                "outfit_name": outfit_name,
                "total_score": total_score,
                "matched_items": matched_items,
            }
        )

        logger.info(
            f"Found a matching outfit of score {round(total_score,2)} for outfit: {outfit_name}"
        )
    return outfit_matches
