import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

from ..exceptions import BadRequestError, NotFoundError, ServerError

# Set up logging
log_file_dir = Path(__file__).parent.parent.parent / "logs"
if not log_file_dir.exists():
    # Create the folder (and parent directories if needed)
    log_file_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_file_dir / "outfit_analyzer.log"

# Set up module logger
logger = logging.getLogger("outfitAnalyzer")
logger.setLevel(logging.DEBUG)

# Set up rotating file handler (max size 500MB, keep 1 backup file)
max_log_size = 500 * 1024 * 1024  # 500MB
backup_count = 1
rotating_handler = RotatingFileHandler(
    log_file_path, maxBytes=max_log_size, backupCount=backup_count
)
rotating_handler.setLevel(logging.DEBUG)

# Add console handler for INFO+ messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s"
)
rotating_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(rotating_handler)
logger.addHandler(console_handler)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data

    Raises:
        NotFoundError: If file not found
        BadRequestError: If JSON is invalid
    """
    try:
        if not os.path.exists(file_path):
            raise NotFoundError("file_not_found", f"File not found: {file_path}")

        with open(file_path, "r") as f:
            data = json.load(f)

        return data

    except json.JSONDecodeError as e:
        raise BadRequestError(
            "invalid_json", f"Invalid JSON in file {file_path}: {str(e)}"
        )
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        raise ServerError("file_read_error", f"Error reading file: {str(e)}")
