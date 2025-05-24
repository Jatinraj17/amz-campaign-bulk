from typing import List, Dict, Any
import re
from datetime import datetime
import pandas as pd

class TextFormatter:
    """Class to handle text formatting operations"""
    
    @staticmethod
    def clean_text_input(text: str) -> List[str]:
        """
        Clean and parse text input (comma or newline separated)
        
        Args:
            text: Raw input text
            
        Returns:
            List of cleaned values
        """
        # Split by both newlines and commas
        items = text.replace('\n', ',').split(',')
        
        # Clean each item and filter out empty strings
        return [item.strip() for item in items if item.strip()]

    @staticmethod
    def format_campaign_name(prefix: str, identifier: str, match_type: str) -> str:
        """
        Format campaign name according to Amazon's requirements
        
        Args:
            prefix: Campaign name prefix
            identifier: Unique identifier (e.g., ASIN)
            match_type: Match type for the campaign
            
        Returns:
            Formatted campaign name
        """
        timestamp = datetime.now().strftime('%Y%m%d')
        # Remove any invalid characters and ensure proper formatting
        prefix = re.sub(r'[^A-Za-z0-9\-_]', '', prefix)
        identifier = re.sub(r'[^A-Za-z0-9\-_]', '', identifier)
        match_type = match_type.upper()
        
        return f"{prefix}-{identifier}-{match_type}-{timestamp}"

    @staticmethod
    def format_ad_group_name(identifier: str, match_type: str) -> str:
        """
        Format ad group name
        
        Args:
            identifier: Unique identifier (e.g., ASIN)
            match_type: Match type for the ad group
            
        Returns:
            Formatted ad group name
        """
        timestamp = datetime.now().strftime('%Y%m%d')
        return f"AG-{identifier}-{match_type}-{timestamp}"

class DataFormatter:
    """Class to handle data formatting operations"""
    
    @staticmethod
    def format_currency(value: float) -> str:
        """
        Format currency values
        
        Args:
            value: Numeric value to format
            
        Returns:
            Formatted currency string
        """
        return f"${value:.2f}"

    @staticmethod
    def format_date(date: datetime) -> str:
        """
        Format date according to Amazon's requirements
        
        Args:
            date: Date to format
            
        Returns:
            Formatted date string
        """
        return date.strftime('%m/%d/%Y')

    @staticmethod
    def format_bulk_sheet(df: pd.DataFrame) -> pd.DataFrame:
        """
        Format bulk sheet data for proper display and export
        
        Args:
            df: DataFrame to format
            
        Returns:
            Formatted DataFrame
        """
        # Create a copy to avoid modifying the original
        formatted_df = df.copy()
        
        # Replace empty strings with None
        formatted_df = formatted_df.replace('', None)
        
        # Format currency columns
        currency_columns = ['Campaign Daily Budget', 'Max Bid', 'Ad Group Default Bid']
        for col in currency_columns:
            if col in formatted_df.columns:
                formatted_df[col] = pd.to_numeric(formatted_df[col], errors='ignore')
                formatted_df[col] = formatted_df[col].map(
                    lambda x: f'${x:.2f}' if pd.notnull(x) else None
                )
        
        # Format date columns
        date_columns = ['Campaign Start Date', 'Campaign End Date']
        for col in date_columns:
            if col in formatted_df.columns:
                formatted_df[col] = pd.to_datetime(formatted_df[col], errors='ignore')
                formatted_df[col] = formatted_df[col].map(
                    lambda x: x.strftime('%m/%d/%Y') if pd.notnull(x) else None
                )
        
        return formatted_df

    @staticmethod
    def prepare_preview_data(df: pd.DataFrame, max_rows: int = 5) -> pd.DataFrame:
        """
        Prepare data for preview display
        
        Args:
            df: DataFrame to prepare
            max_rows: Maximum number of rows to include
            
        Returns:
            DataFrame prepared for preview
        """
        preview_df = df.head(max_rows).copy()
        
        # Hide some columns for better preview
        hidden_columns = [
            'Portfolio ID', 'Portfolio Name', 'Campaign End Date',
            'Placement Type', 'Increase bids by placement'
        ]
        
        for col in hidden_columns:
            if col in preview_df.columns:
                preview_df = preview_df.drop(col, axis=1)
        
        return preview_df
