from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
import re

# Amazon's validation limits
MAX_KEYWORD_LENGTH = 80  # Maximum allowed length for keywords
MAX_SKU_LENGTH = 40  # Maximum allowed length for SKUs
MAX_TEMPLATE_LENGTH = 128  # Maximum allowed length for campaign/ad group name templates
MIN_DAILY_BUDGET = 1.0  # Minimum allowed daily budget in dollars
MIN_BID_AMOUNT = 0.02  # Minimum allowed bid amount in dollars
MIN_BID_ADJUSTMENT = 0  # Minimum allowed bid adjustment percentage
MAX_BID_ADJUSTMENT = 900  # Maximum allowed bid adjustment percentage
DEFAULT_MIN_VALUE = 0.01  # Default minimum value for numeric inputs

# Validation defaults and results
DEFAULT_EMPTY_SET = set()  # For set operations
DEFAULT_EMPTY_LIST = []  # For list operations
DEFAULT_EMPTY_DICT = {}  # For dictionary operations
VALIDATION_SUCCESS = (True, None)  # Standard success response
VALIDATION_FAILURE = lambda msg: (False, msg)  # Standard failure response

# Error messages
NUMERIC_ERROR = "Invalid value for {}: must be greater than {}"
INVALID_NUMBER_ERROR = "Invalid numeric value for {}"
PAST_DATE_ERROR = "Start date cannot be in the past"
EMPTY_LIST_ERROR = "No {} provided"
EMPTY_ITEM_ERROR = "Empty value found in {}"
LENGTH_ERROR = "Invalid length for {}: '{}' exceeds maximum length of {}"
INVALID_CHARS_ERROR = "Invalid characters in {}: {}"
TEMPLATE_LENGTH_ERROR = "{} exceeds maximum length"
BID_ADJUSTMENT_RANGE_ERROR = "Bid adjustment must be between {}% and {}%"

# Field names and formats
DAILY_BUDGET_FIELD = "Daily budget"
BID_FIELD_TEMPLATE = "Bid for {}"
KEYWORD_FIELD = "Keyword"
SKU_FIELD = "SKU"
MATCH_TYPE_FIELD = "Match type"
PLACEMENT_FIELD = "Placement"
PERCENTAGE_FIELD = "Percentage"
START_DATE_FIELD = "Start Date"
PRODUCT_TYPE = "Sponsored Products"

# Valid values
VALID_PLACEMENT = "top-of-search"

# Format constants
PERCENTAGE_SUFFIX = "%"  # For bid adjustment validation
EMPTY_STRING = ""  # For consistent empty string usage
DATE_FORMAT = "%Y%m%d"  # Amazon's required date format

# Field name variations
KEYWORD_SINGULAR = "keyword"
SKU_SINGULAR = "SKU"
KEYWORDS_PLURAL = "keywords"
SKUS_PLURAL = "SKUs"

# Match type values
MATCH_TYPE_EXACT = "exact"
MATCH_TYPE_PHRASE = "phrase"
MATCH_TYPE_BROAD = "broad"

# Template and formatting
NAME_TEMPLATE_SUFFIX = "name template"
MATCH_TYPE_PLACEHOLDER = "match_type"
SKU_PLACEHOLDER = "sku"
TEMPLATE_NAME_FORMAT = "{} {}"  # For combining type and suffix
PLACEHOLDER_SEPARATOR = ", "  # For joining placeholders in error messages
LIST_SEPARATOR = ", "  # For joining list items in error messages
CAMPAIGN_TEMPLATE_TYPE = "campaign"  # For template validation
AD_GROUP_TEMPLATE_TYPE = "ad group"  # For template validation

# Template parts
VALID_TEMPLATE_PARTS = {
    'SKU': '[SKU]',
    'MATCH_TYPE': 'match_type',
    'AD_TYPE': 'SP',
    'ROOT': '[Root]',
    'KEYWORD': '[KW]',
    'AG': 'AG'
}

# Settings dictionary keys
SETTINGS_MATCH_TYPES_KEY = "match_types"
SETTINGS_DAILY_BUDGET_KEY = "daily_budget"
SETTINGS_BIDS_KEY = "bids"
SETTINGS_BID_ADJUSTMENT_KEY = "bid_adjustment"
SETTINGS_PLACEMENT_KEY = "placement"
SETTINGS_START_DATE_KEY = "start_date"

# Regex patterns for validation
KEYWORD_PATTERN = r'^[\w\s\-\']+$'  # Allows alphanumeric, spaces, hyphens, and apostrophes
SKU_PATTERN = r'^[a-zA-Z0-9_\-.,></":\;+=]+$'  # Allows alphanumeric and specified special characters
TEMPLATE_PATTERN = r'^[\w\-_]*$'  # Allows alphanumeric, hyphens, and underscores

def validate_numeric_input(value: Union[float, str], field_name: str, min_value: float = DEFAULT_MIN_VALUE) -> Tuple[bool, Optional[str]]:
    """Validate numeric inputs for campaign settings"""
    try:
        value = float(value)
        if value <= min_value:
            return VALIDATION_FAILURE(NUMERIC_ERROR.format(field_name, min_value))
        return VALIDATION_SUCCESS
    except ValueError:
        return VALIDATION_FAILURE(INVALID_NUMBER_ERROR.format(field_name))

def validate_date(date: datetime) -> Tuple[bool, Optional[str]]:
    """Validate campaign start date"""
    if date < datetime.today().date():
        return VALIDATION_FAILURE(PAST_DATE_ERROR)
    try:
        # Verify the date can be formatted in Amazon's required format
        date.strftime(DATE_FORMAT)
        return VALIDATION_SUCCESS
    except ValueError:
        return VALIDATION_FAILURE(f"Invalid value: {date} specified for field: {START_DATE_FIELD}, the correct date format is {DATE_FORMAT}")

def validate_keywords(keywords: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate keywords list"""
    if not keywords:
        return VALIDATION_FAILURE(EMPTY_LIST_ERROR.format(KEYWORD_SINGULAR))
    
    for keyword in keywords:
        if not keyword.strip():
            return VALIDATION_FAILURE(EMPTY_ITEM_ERROR.format(KEYWORDS_PLURAL))
        if len(keyword) > MAX_KEYWORD_LENGTH:
            return VALIDATION_FAILURE(LENGTH_ERROR.format(KEYWORD_FIELD, keyword, MAX_KEYWORD_LENGTH))
        if not re.match(KEYWORD_PATTERN, keyword):
            return VALIDATION_FAILURE(INVALID_CHARS_ERROR.format(KEYWORD_FIELD, keyword))
    
    return VALIDATION_SUCCESS

def validate_skus(skus: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate SKUs list"""
    if not skus:
        return VALIDATION_FAILURE(EMPTY_LIST_ERROR.format(SKU_SINGULAR))
    
    for sku in skus:
        if not sku.strip():
            return VALIDATION_FAILURE(EMPTY_ITEM_ERROR.format(SKUS_PLURAL))
        if len(sku) > MAX_SKU_LENGTH:
            return VALIDATION_FAILURE(LENGTH_ERROR.format(SKU_FIELD, sku, MAX_SKU_LENGTH))
        if not re.match(SKU_PATTERN, sku):
            return VALIDATION_FAILURE(INVALID_CHARS_ERROR.format(SKU_FIELD, sku))
    
    return VALIDATION_SUCCESS

def validate_match_types(match_types: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate match types"""
    valid_match_types = {
        MATCH_TYPE_EXACT,
        MATCH_TYPE_PHRASE,
        MATCH_TYPE_BROAD
    }
    if not match_types:
        return VALIDATION_FAILURE(EMPTY_LIST_ERROR.format(MATCH_TYPE_FIELD))
    
    # Convert input match types to lowercase for comparison
    input_match_types = {mt.lower() for mt in match_types} if match_types else DEFAULT_EMPTY_SET
    invalid_types = input_match_types - valid_match_types if valid_match_types else input_match_types
    if invalid_types:
        return VALIDATION_FAILURE(INVALID_CHARS_ERROR.format(MATCH_TYPE_FIELD, LIST_SEPARATOR.join(invalid_types)))
    
    return VALIDATION_SUCCESS

def validate_name_template(template: str, template_type: str) -> Tuple[bool, Optional[str]]:
    """Validate campaign or ad group name template"""
    if not template:
        return VALIDATION_FAILURE(EMPTY_ITEM_ERROR.format(TEMPLATE_NAME_FORMAT.format(template_type, NAME_TEMPLATE_SUFFIX)))
    
    if len(template) > MAX_TEMPLATE_LENGTH:
        return VALIDATION_FAILURE(TEMPLATE_LENGTH_ERROR.format(TEMPLATE_NAME_FORMAT.format(template_type, NAME_TEMPLATE_SUFFIX)))
    
    # Different validation for campaign and ad group templates
    if template_type == CAMPAIGN_TEMPLATE_TYPE:
        # Campaign template can contain any valid parts and dates
        template_parts = template.split('_')
        
        # Common variations and aliases
        valid_variations = {
            'type': True, 'kw': True, '[kw]': True, 'match': True, 'keyword': True,
            'sp': True, 'sponsored': True, 'products': True,
            'root': True, 'group': True, 'category': True,
            'ag': True  # For ad group templates
        }
        
        # Required parts for campaign template
        required_parts = {'[SKU]': False, 'match_type': False}
        
        # Check each part
        for part in template_parts:
            if not part:  # Skip empty parts
                continue
                
            part_lower = part.lower()
            
            # Check for SKU
            if '[sku]' in part_lower:
                required_parts['[SKU]'] = True
                
            # Check for match type
            if 'match_type' in part_lower or 'match' in part_lower:
                required_parts['match_type'] = True
            
            # Skip valid parts (case-insensitive)
            if part in VALID_TEMPLATE_PARTS.values() or part.lower() in [v.lower() for v in VALID_TEMPLATE_PARTS.values()]:
                continue
                
            # Skip date formats
            if re.match(r'\d{6}|\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4}|[A-Za-z]{3}\s\d{2},\s\d{4}', part):
                continue
                
            # Skip common variations
            if part_lower in valid_variations:
                continue
                
            # Allow custom text that contains letters, numbers, hyphens, and underscores
            if not re.match(r'^[A-Za-z0-9\-_]+$', part):
                return VALIDATION_FAILURE(f"Invalid characters in custom text: {part}. Only letters, numbers, hyphens, and underscores are allowed.")
        
        # Check if all required parts are present
        missing_parts = [part for part, found in required_parts.items() if not found]
        if missing_parts:
            return VALIDATION_FAILURE(f"Missing required parts in campaign template: {', '.join(missing_parts)}")
    else:
        # Ad group template validation
        template_parts = template.split('_')
        
        # Required parts for ad group template
        required_parts = {'[SKU]': False, 'match_type': False}
        
        # Check each part
        for part in template_parts:
            if not part:  # Skip empty parts
                continue
                
            part_lower = part.lower()
            
            # Check for SKU
            if '[sku]' in part_lower:
                required_parts['[SKU]'] = True
                
            # Check for match type
            if 'match_type' in part_lower or 'match' in part_lower:
                required_parts['match_type'] = True
            
            # Skip valid parts (case-insensitive)
            if part in VALID_TEMPLATE_PARTS.values() or part.lower() in [v.lower() for v in VALID_TEMPLATE_PARTS.values()]:
                continue
                
            # Skip date formats
            if re.match(r'\d{6}|\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4}|[A-Za-z]{3}\s\d{2},\s\d{4}', part):
                continue
                
            # Allow custom text that contains letters, numbers, hyphens, and underscores
            if not re.match(r'^[A-Za-z0-9\-_]+$', part):
                return VALIDATION_FAILURE(f"Invalid characters in custom text: {part}. Only letters, numbers, hyphens, and underscores are allowed.")
        
        # Check if all required parts are present
        missing_parts = [part for part, found in required_parts.items() if not found]
        if missing_parts:
            return VALIDATION_FAILURE(f"Missing required parts in ad group template: {', '.join(missing_parts)}")
    
    return VALIDATION_SUCCESS

def validate_bid_adjustment(value: str, placement: str) -> Tuple[bool, Optional[str]]:
    """Validate bid adjustment percentage and placement"""
    # Validate placement
    if placement != VALID_PLACEMENT:
        return VALIDATION_FAILURE(f'Invalid value: "{placement}" for column: "{PLACEMENT_FIELD}"')
    
    # Validate percentage format
    if not value.endswith(PERCENTAGE_SUFFIX):
        return VALIDATION_FAILURE(f'Invalid value: "{value}" for column: "{PERCENTAGE_FIELD}"')
    
    try:
        percentage = int(value.rstrip(PERCENTAGE_SUFFIX))
        if percentage < MIN_BID_ADJUSTMENT or percentage > MAX_BID_ADJUSTMENT:
            return VALIDATION_FAILURE(BID_ADJUSTMENT_RANGE_ERROR.format(MIN_BID_ADJUSTMENT, MAX_BID_ADJUSTMENT))
        return VALIDATION_SUCCESS
    except ValueError:
        return VALIDATION_FAILURE(f'Invalid value: "{value}" for column: "{PERCENTAGE_FIELD}"')

def validate_campaign_settings(settings) -> Tuple[bool, Optional[str]]:
    """Validate campaign settings"""
    # Validate match types
    match_types_result = validate_match_types(settings.match_types)
    if not match_types_result[0]:
        return match_types_result
    
    # Validate daily budget
    budget_result = validate_numeric_input(
        settings.daily_budget, 
        DAILY_BUDGET_FIELD,
        min_value=MIN_DAILY_BUDGET
    )
    if not budget_result[0]:
        return budget_result
    
    # Validate bids
    for match_type, bid in settings.bids.items():
        bid_result = validate_numeric_input(
            bid, 
            BID_FIELD_TEMPLATE.format(match_type),
            min_value=MIN_BID_AMOUNT
        )
        if not bid_result[0]:
            return bid_result
    
    # Validate bid adjustment and placement only if both values are provided
    if settings.bid_adjustment and settings.placement:
        adjustment_result = validate_bid_adjustment(
            settings.bid_adjustment,
            settings.placement
        )
        if not adjustment_result[0]:
            return adjustment_result
    
    # Validate start date
    date_result = validate_date(settings.start_date)
    if not date_result[0]:
        return date_result
    
    # Validate campaign name template
    campaign_template_result = validate_name_template(settings.campaign_name_template, CAMPAIGN_TEMPLATE_TYPE)
    if not campaign_template_result[0]:
        return campaign_template_result
    
    # Validate ad group name template
    ad_group_template_result = validate_name_template(settings.ad_group_name_template, AD_GROUP_TEMPLATE_TYPE)
    if not ad_group_template_result[0]:
        return ad_group_template_result
    
    return VALIDATION_SUCCESS
