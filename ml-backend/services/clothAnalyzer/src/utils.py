import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_file_dir = Path(__file__).parent.parent / "logs"
if not log_file_dir.exists():
    # Create the folder (and parent directories if needed)
    log_file_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_file_dir / "cloth_analyzer.log"

# Set up module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set up rotating file handler (max size 5MB, keep 3 backup files)
max_log_size = 500 * 1024 * 1024  # 5MB
backup_count = 1
rotating_handler = RotatingFileHandler(log_file_path, maxBytes=max_log_size, backupCount=backup_count)
rotating_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
rotating_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(rotating_handler)
