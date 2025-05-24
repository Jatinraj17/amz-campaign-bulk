"""
Amazon Ads Bulk Campaign Generator
--------------------------------

A tool for generating Amazon Advertising campaigns in bulk.
"""

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.parent

# Template directory
TEMPLATE_DIR = ROOT_DIR / 'templates'

# Output directory
OUTPUT_DIR = ROOT_DIR / 'output'

# Ensure directories exist
TEMPLATE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Version
__version__ = '1.0.0'

# Import main classes for easier access
from .core.generator import BulkSheetGenerator, CampaignSettings
from .core.validators import (
    validate_keywords,
    validate_skus,
    validate_campaign_settings,
    validate_name_template
)
from .web.app import BulkCampaignApp

__all__ = [
    'BulkSheetGenerator',
    'CampaignSettings',
    'validate_keywords',
    'validate_skus',
    'validate_campaign_settings',
    'validate_name_template',
    'BulkCampaignApp'
]
