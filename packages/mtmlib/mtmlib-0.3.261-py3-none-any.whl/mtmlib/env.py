import sys
from pathlib import Path


def init_env():
    sys.path.insert(0, str(Path("./mtmlib").absolute()))
    sys.path.insert(0, str(Path("./mtmtrain").absolute()))
