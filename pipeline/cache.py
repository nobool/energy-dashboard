import pandas as pd
from pathlib import Path
from pipeline.config import CACHE_DIR

def save_to_cache(df: pd.DataFrame, filename: str):
    filepath = CACHE_DIR / filename
    df.to_pickle(filepath)

def load_from_cache(filename: str) -> pd.DataFrame:
    filepath = CACHE_DIR / filename
    if filepath.exists():
        return pd.read_pickle(filepath)
    return None
