import os
import sys

parent = os.path.dirname
BASE_DIR = parent(parent(parent(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
