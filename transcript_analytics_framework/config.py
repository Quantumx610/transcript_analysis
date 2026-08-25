import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# ================================================================================================
# LLM & Azure Configuration
# ================================================================================================
# Required Azure credentials
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

# Optional LLM parameters with default fallbacks
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))

# Handle max tokens (can be None if your model doesn't support it)
_max_tokens_env = os.getenv("LLM_MAX_TOKENS")
LLM_MAX_TOKENS = int(_max_tokens_env) if _max_tokens_env else None

# ================================================================================================
# Directory Paths (3-Layer Architecture)
# ================================================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Input paths
INPUT_CSV_PATH = DATA_DIR / "input" / "transcripts" /"transcripts.csv"
INPUT_SCRIPTS_DIR = DATA_DIR / "input" / "scripts"

# Output paths (Bronze, Silver, Gold Layers)
BRONZE_DIR = DATA_DIR / "output" / "bronze_raw_prompts"
SILVER_DIR = DATA_DIR / "output" / "silver_merged_json"
GOLD_DIR = DATA_DIR / "output" / "gold_flattened_csv"

# Ensure output directories exist at runtime
for folder in [BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)