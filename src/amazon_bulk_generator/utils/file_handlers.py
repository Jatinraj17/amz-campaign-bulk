import pandas as pd
from typing import List, Optional
import os
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileHandler:
    """Class to handle file operations for the bulk campaign generator"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize FileHandler
        
        Args:
            base_dir: Base directory for file operations. Defaults to current directory.
        """
        self.base_dir = base_dir or os.getcwd()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        directories = ['templates', 'output', 'input']
        for directory in directories:
            dir_path = os.path.join(self.base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"Created directory: {dir_path}")

    def load_csv_data(self, file_path: str) -> List[str]:
        """
        Load data from CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of values from the first column
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.EmptyDataError: If the file is empty
        """
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                raise pd.errors.EmptyDataError("CSV file is empty")
            return df.iloc[:, 0].tolist()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"Empty CSV file: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            raise

    def save_bulk_sheet(self, df: pd.DataFrame, format: str = 'xlsx') -> str:
        """
        Save bulk sheet to file
        
        Args:
            df: DataFrame containing bulk sheet data
            format: Output format ('xlsx' or 'csv')
            
        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(self.base_dir, 'output')
        
        if format.lower() == 'xlsx':
            return self._save_excel(df, output_dir, timestamp)
        elif format.lower() == 'csv':
            return self._save_csv(df, output_dir, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_excel(self, df: pd.DataFrame, output_dir: str, timestamp: str) -> str:
        """
        Save DataFrame to Excel file
        
        Args:
            df: DataFrame to save
            output_dir: Output directory
            timestamp: Timestamp for filename
            
        Returns:
            Path to the saved file
        """
        filename = f"amazon_bulk_upload_{timestamp}.xlsx"
        output_path = os.path.join(output_dir, filename)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sponsored Products', index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Sponsored Products']
            
            # Auto-adjust columns' width
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                try:
                    max_length = max(
                        len(str(cell.value)) for cell in column if cell.value
                    )
                except ValueError:
                    max_length = 0
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        logger.info(f"Saved Excel file: {output_path}")
        return output_path

    def _save_csv(self, df: pd.DataFrame, output_dir: str, timestamp: str) -> str:
        """
        Save DataFrame to CSV file
        
        Args:
            df: DataFrame to save
            output_dir: Output directory
            timestamp: Timestamp for filename
            
        Returns:
            Path to the saved file
        """
        filename = f"amazon_bulk_upload_{timestamp}.csv"
        output_path = os.path.join(output_dir, filename)
        
        df.to_csv(output_path, index=False)
        logger.info(f"Saved CSV file: {output_path}")
        return output_path

    def get_template_path(self, template_type: str) -> str:
        """
        Get path to template file
        
        Args:
            template_type: Type of template ('keywords' or 'skus')
            
        Returns:
            Path to the template file
        """
        filename = f"{template_type}_template.csv"
        return os.path.join(self.base_dir, 'templates', filename)

    def load_template_data(self, template_type: str) -> str:
        """
        Load template file content
        
        Args:
            template_type: Type of template ('keywords' or 'skus')
            
        Returns:
            Content of the template file
        """
        template_path = self.get_template_path(template_type)
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"Template file not found: {template_path}")
            return ""
        except Exception as e:
            logger.error(f"Error loading template {template_path}: {str(e)}")
            return ""
