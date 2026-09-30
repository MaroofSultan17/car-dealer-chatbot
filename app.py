import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from car_chatbot.main import app  # noqa: E402, F401
