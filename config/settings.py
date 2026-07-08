from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_NAME = "Project Health Reporting Agent"

VERSION = "1.0.0"

AUTHOR = "Thanushree V N"

# Optional for future LLM-based narrative; current MVP uses rule-based scoring.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

INPUT_FOLDER = "data/input"

OUTPUT_FOLDER = "data/output"

LOG_FOLDER = "logs"

REPORT_FOLDER = "reports"

