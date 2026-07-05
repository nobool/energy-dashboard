import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "pipeline" / "cache"

DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

SEMOPX_DELAY_S = 2.0
EIRGRID_DELAY_S = 1.5
ENTSOE_DELAY_S = 3.0

TIMEZONE = "Europe/Dublin"

CCGT_HEAT_RATE = 2.0  
CCGT_EMISSION_FACTOR = 0.4  
VOM_COST = 3.0  

DEFAULT_GAS_PRICE = 30.0    
DEFAULT_CARBON_PRICE = 70.0 
