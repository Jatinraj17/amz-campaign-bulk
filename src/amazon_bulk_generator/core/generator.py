from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
import re
from itertools import zip_longest

@dataclass
class CampaignSettings:
    """Data class for campaign settings"""
    daily_budget: float
    start_date: datetime
    match_types: List[str]  # Valid values: MATCH_TYPE_EXACT, MATCH_TYPE_PHRASE, MATCH_TYPE_BROAD
    bids: Dict[str, float]  # Default bids per match type
    keyword_bids: Dict[str, float] = None  # Optional keyword-specific bids
    bid_adjustment: str = ""  # No default bid adjustment
    campaign_name_template: str = "SP_match_type_KW_sku"
    ad_group_name_template: str = "AG_match_type_sku"
    placement: str = ""  # No default placement
    keyword_group_size: int = None  # New field for keyword grouping
    sku_group_size: int = None  # New field for SKU grouping

class BulkSheetGenerator:
    """Class to handle the generation of Amazon Ads bulk sheets"""
    
    # Constants for consistent value usage
    PLACEMENT_TOP_OF_SEARCH = "top-of-search"
    TARGETING_TYPE = "MANUAL"
    BIDDING_STRATEGY = "Dynamic bids - down only"
    STATE = "enabled"
    OPERATION = "Create"
    PRODUCT = "Sponsored Products"
    DATE_FORMAT = "%Y%m%d"

    # Entity types
    ENTITY_CAMPAIGN = "Campaign"
    ENTITY_AD_GROUP = "Ad Group"
    ENTITY_BIDDING_ADJUSTMENT = "Bidding Adjustment"
    ENTITY_PRODUCT_AD = "Product Ad"
    ENTITY_KEYWORD = "Keyword"

    # Match types
    MATCH_TYPE_EXACT = "exact"
    MATCH_TYPE_PHRASE = "phrase"
    MATCH_TYPE_BROAD = "broad"
    
    def __init__(self):
        # Headers exactly as provided by Amazon
        self.headers = [
            'Product',
            'Entity',
            'Operation',
            'Campaign ID',
            'Ad Group ID',
            'Portfolio ID',
            'Ad ID',
            'Keyword ID',
            'Product Targeting ID',
            'Campaign Name',
            'Ad Group Name',
            'Start Date',
            'End Date',
            'Targeting Type',
            'State',
            'Daily Budget',
            'SKU',
            'Ad Group Default Bid',
            'Bid',
            'Keyword Text',
            'Native Language Keyword',
            'Native Language Locale',
            'Match Type',
            'Bidding Strategy',
            'Placement',
            'Percentage',
            'Product Targeting Expression'
        ]

    def _group_keywords(self, keywords: List[str], group_size: int) -> List[List[str]]:
        """Group keywords into specified sizes"""
        if not group_size or group_size <= 0:
            return [[kw] for kw in keywords]  # Each keyword in its own group
        
        # Split keywords into groups of specified size
        keyword_groups = []
        for i in range(0, len(keywords), group_size):
            group = keywords[i:i + group_size]
            keyword_groups.append(group)
        return keyword_groups

    def _group_skus(self, skus: List[str], group_size: int) -> List[List[str]]:
        """Group SKUs into specified sizes"""
        if not group_size or group_size <= 0:
            return [[sku] for sku in skus]  # Each SKU in its own group
        
        # Split SKUs into groups of specified size
        sku_groups = []
        for i in range(0, len(skus), group_size):
            group = skus[i:i + group_size]
            sku_groups.append(group)
        return sku_groups

    def generate_bulk_sheet(self, keywords: List[str], skus: List[str], settings: CampaignSettings) -> pd.DataFrame:
        """Generate bulk sheet from inputs"""
        rows = []
        start_date = settings.start_date.strftime(self.DATE_FORMAT)
        
        # Group keywords if group size is specified
        keyword_groups = self._group_keywords(keywords, settings.keyword_group_size)
        
        # Group SKUs if group size is specified
        sku_groups = self._group_skus(skus, settings.sku_group_size)
        
        for sku_group in sku_groups:
            for keyword_group in keyword_groups:
                for match_type in settings.match_types:
                    # Generate campaign rows for the entire keyword group and sku group
                    group_rows = self._generate_campaign_rows(
                        sku_group=sku_group,
                        keywords=keyword_group,
                        match_type=match_type.lower(),
                        start_date=start_date,
                        settings=settings
                    )
                    rows.extend(group_rows)
        
        df = pd.DataFrame(rows, columns=self.headers)
        return self._format_dataframe(df)

    def _generate_campaign_name(self, template: str, sku: str, match_type: str, start_date: str) -> str:
        """Generate campaign name using template"""
        # Map of placeholders to their values
        # Handle SKU placeholder specially to avoid overly long names with grouped SKUs
        sku_parts = sku.split('_')
        if len(sku_parts) > 1:
            # For grouped SKUs, use first SKU + count
            sku_display = f"{sku_parts[0]}+{len(sku_parts)-1}"
        else:
            sku_display = sku

        replacements = {
            '[SKU]': sku_display,
            'SP': 'SP',
            'match_type': match_type,
            '[Root]': '[Root]',
            '[KW]': '[KW]'
        }
        
        # Handle date formats
        date_obj = datetime.strptime(start_date, '%Y%m%d')
        date_formats = {
            '250423': date_obj.strftime('%d%m%y'),
            '04/23/2025': date_obj.strftime('%m/%d/%Y'),
            '23-04-2025': date_obj.strftime('%d-%m-%Y'),
            'Apr 23, 2025': date_obj.strftime('%b %d, %Y')
        }
        
        # Replace date format if present
        for date_format in date_formats:
            if date_format in template:
                template = template.replace(date_format, date_formats[date_format])
        
        # Replace other placeholders
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        
        return template

    def _generate_campaign_rows(self, sku_group: List[str], keywords: List[str], match_type: str, 
                              start_date: str, settings: CampaignSettings) -> List[Dict[str, Any]]:
        """Generate all rows for a single campaign with multiple keywords and SKUs"""
        rows = []
        
        # Clean keywords for use in names
        clean_keywords = [re.sub(r'[^a-zA-Z0-9]', '_', kw).lower() for kw in keywords]
        group_identifier = clean_keywords[0]  # Use first keyword as group identifier
        
        # Create a combined SKU string for the group
        combined_sku = "_".join(sku_group)
        
        # Generate a unique campaign ID using the combined SKU and group identifier
        campaign_id = f"{combined_sku}_{match_type}_{group_identifier}"
        
        # Generate base names
        base_campaign_name = self._generate_campaign_name(
            settings.campaign_name_template, 
            combined_sku, 
            match_type,
            start_date
        )
        
        base_ad_group_name = self._generate_campaign_name(
            settings.ad_group_name_template,
            combined_sku,
            match_type,
            start_date
        )
        
        # Base row template with all fields in correct order
        base_row = {
            'Product': self.PRODUCT,
            'Entity': '',
            'Operation': self.OPERATION,
            'Campaign ID': campaign_id,
            'Ad Group ID': '',
            'Portfolio ID': '',
            'Ad ID': '',
            'Keyword ID': '',
            'Product Targeting ID': '',
            'Campaign Name': '',
            'Ad Group Name': '',
            'Start Date': '',
            'End Date': '',
            'Targeting Type': '',
            'State': self.STATE,
            'Daily Budget': '',
            'SKU': '',
            'Ad Group Default Bid': '',
            'Bid': '',
            'Keyword Text': '',
            'Native Language Keyword': '',
            'Native Language Locale': '',
            'Match Type': '',
            'Bidding Strategy': '',
            'Placement': '',
            'Percentage': '',
            'Product Targeting Expression': ''
        }
        
        # Campaign row
        campaign_row = base_row.copy()
        campaign_row.update({
            'Entity': self.ENTITY_CAMPAIGN,
            'Campaign Name': f"{base_campaign_name}_{group_identifier}",
            'Start Date': start_date,
            'Targeting Type': self.TARGETING_TYPE,
            'Daily Budget': settings.daily_budget,
            'Bidding Strategy': self.BIDDING_STRATEGY,
            'State': self.STATE
        })
        rows.append(campaign_row)
        
        # Ad Group row
        ad_group_row = base_row.copy()
        ad_group_row.update({
            'Entity': self.ENTITY_AD_GROUP,
            'Ad Group ID': campaign_id,
            'Ad Group Name': f"{base_ad_group_name}_{group_identifier}",
            'Ad Group Default Bid': settings.bids[match_type],
            'State': self.STATE
        })
        rows.append(ad_group_row)
        
        # Bidding Adjustment row (only if placement and bid_adjustment are provided)
        if settings.placement and settings.bid_adjustment:
            bidding_adjustment_row = base_row.copy()
            bidding_adjustment_row.update({
                'Entity': self.ENTITY_BIDDING_ADJUSTMENT,
                'Ad Group ID': campaign_id,
                'Placement': settings.placement,
                'Percentage': settings.bid_adjustment,
                'State': self.STATE
            })
            rows.append(bidding_adjustment_row)
        
        # Product Ad rows for each SKU in the group
        for sku in sku_group:
            product_ad_row = base_row.copy()
            product_ad_row.update({
                'Entity': self.ENTITY_PRODUCT_AD,
                'Ad Group ID': campaign_id,
                'SKU': sku,
                'State': self.STATE
            })
            rows.append(product_ad_row)
        
        # Keyword rows
        for keyword in keywords:
            # Get bid for this keyword (use default if no specific bid)
            keyword_bid = settings.keyword_bids.get(keyword, settings.bids[match_type]) if settings.keyword_bids else settings.bids[match_type]
            
            keyword_row = base_row.copy()
            keyword_row.update({
                'Entity': self.ENTITY_KEYWORD,
                'Ad Group ID': campaign_id,
                'Bid': keyword_bid,
                'Keyword Text': keyword,
                'Match Type': match_type.lower(),
                'State': self.STATE
            })
            rows.append(keyword_row)
        
        return rows

    def _format_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format the DataFrame for proper display and export"""
        # Convert empty strings to None for better Excel export
        df = df.replace('', None)
        
        # Format numeric columns
        numeric_columns = ['Daily Budget', 'Bid', 'Ad Group Default Bid']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
            df[col] = df[col].map(lambda x: f'{x:.2f}' if pd.notnull(x) else None)
        
        return df

    def get_example_data(self) -> Dict[str, List[str]]:
        """Get example data for demonstration"""
        return {
            'keywords': [
                'gaming keyboard',
                'wireless mouse',
                'laptop stand'
            ],
            'skus': [
                'SKU001',
                'SKU002'
            ]
        }

    @staticmethod
    def load_keyword_bids(csv_path: str) -> Dict[str, float]:
        """Load keyword-specific bids from a CSV file.
        
        The CSV file should have two columns:
        - Keyword: The exact keyword text
        - Bid: The bid amount for that keyword
        
        Returns:
            Dict[str, float]: Dictionary mapping keywords to their specific bids
        """
        df = pd.read_csv(csv_path)
        if 'Keyword' not in df.columns or 'Bid' not in df.columns:
            raise ValueError("CSV must contain 'Keyword' and 'Bid' columns")
        
        # Convert bids to float
        df['Bid'] = pd.to_numeric(df['Bid'], errors='coerce')
        
        # Remove any rows with invalid bids
        df = df.dropna(subset=['Bid'])
        
        # Create dictionary with keyword as key and bid as float value
        return dict(zip(df['Keyword'], df['Bid'].astype(float)))
