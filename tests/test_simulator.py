import pytest
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.simulator import Simulator
from src.common.csvreader import read_cores, read_budgets, read_tasks

