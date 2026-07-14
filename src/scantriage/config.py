from pathlib import Path


# PATHS
PROJECT_ROOT = Path(__file__).parent.parent
LOG_ROOT = PROJECT_ROOT/"Logs"

LOG_MODEL = LOG_ROOT/"model.log"
LOG_PARSING = LOG_ROOT/"parsing.log"
LOG_MAIN = LOG_ROOT/"main.log"
