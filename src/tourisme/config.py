"""Chemins du projet"""
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

DATA_RAW = RACINE / "data" / "raw"
DATA_PROCESSED = RACINE / "data" / "processed"

RAW_FILE = DATA_RAW / "data_tourisme.json"