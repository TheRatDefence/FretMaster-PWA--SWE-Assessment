"""
Configuration file for FretMaster PWA
Contains paths and settings used throughout the application
"""

from pathlib import Path
import os

# Project structure paths
PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / 'database' / 'fretmaster.db'
DIAGRAM_PATH = PROJECT_ROOT / 'static' / 'diagrams'
STATIC_PATH = PROJECT_ROOT / 'static'
TEMPLATES_PATH = PROJECT_ROOT / 'templates'

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# Musical notation preferences
PREFER_SHARPS = True
