import logging
import sys

# Configure a basic logger that writes to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout
)

# Create a logger instance to be used across the application
logger = logging.getLogger("A-Vision")