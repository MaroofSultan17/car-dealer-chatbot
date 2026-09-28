from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
CARS_FILE = DATA_DIR / "car.csv"
DEALERS_FILE = DATA_DIR / "dealer.csv"