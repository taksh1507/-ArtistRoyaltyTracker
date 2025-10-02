"""
Configuration Settings
======================
Central configuration file for the Music Rights Analysis project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SRC_DIR = BASE_DIR / "src"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Dataset Configuration
DATASET_FILENAME = "unclaimedmusicalworkrightshares.tsv"
DATASET_PATH = DATA_DIR / DATASET_FILENAME

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Analysis Configuration
DEFAULT_ARTIST = "Coldplay"  # Change this to analyze different artists
CHUNK_SIZE = 500000  # Rows to process at once for large files
MAX_RETRIES = 3  # API retry attempts
RATE_LIMIT_DELAY = 0.1  # Seconds between API calls

# Output Configuration
OUTPUT_FILENAME = "artist_unclaimed_report.xlsx"
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILENAME

# Performance Configuration
MEMORY_EFFICIENT = True  # Use memory-efficient loading for large files
OPTIMIZE_COLUMNS = True  # Only load essential columns
FILTER_NO_ISRC = True  # Remove rows without ISRC during loading

# Essential columns to keep (for memory optimization)
ESSENTIAL_KEYWORDS = ['isrc', 'title', 'artist', 'work', 'share', 'right', 'resource', 'duration']

# Logging Configuration
LOG_LEVEL = "INFO"
VERBOSE = True  # Show detailed progress updates
