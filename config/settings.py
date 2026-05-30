"""Application configuration defaults."""
from pathlib import Path
import os

APP_NAME = "API LeakProof"
APP_VERSION = "0.1.0"

# Paths
DATA_DIR = Path.home() / ".api-leakproof"
DB_PATH = DATA_DIR / "leakproof.db"
CONFIG_PATH = DATA_DIR / "config.json"

# Proxy defaults
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080

# Monitor defaults
CHECK_INTERVAL_MINUTES = 5
ALERT_COOLDOWN_SECONDS = 60

# Severity thresholds
COST_GAP_WARNING = 0.01       # $
COST_GAP_CRITICAL = 1.00      # $
CONSECUTIVE_CRITICAL = 3      # consecutive checks with gap > 0

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)
