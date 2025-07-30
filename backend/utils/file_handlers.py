"""
File Handlers Module
Utility functions for file I/O operations
"""

import os
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
import zipfile
import shutil

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations for the application"""
    
    def __init__(self, base_directory: str = "data"):
        """
        Initialize file handler
        
        Args:
            base_directory: Base directory for file operations
        """
        self.base_directory = Path(base_directory)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.base_directory / "logs",
            self.base_directory / "reports", 
            self.base_directory / "test_data",
            self.base_directory / "exports",
            self.base_directory / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_json_data(self, data: Dict[str, Any], filename: str, subdirectory: str = "") -> str:
        """
        Save data as JSON file
        
        Args:
            data: Data to save
            filename: Name of the file
            subdirectory: Subdirectory to save in
            
        Returns:
            str: Path to saved file
        """
        try:
            file_path = self._get_file_path(filename, subdirectory, "json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"JSON data saved to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving JSON data: {str(e)}")
            raise
    
    def load_json_data(self, filename: str, subdirectory: str = "") -> Dict[str, Any]:
        """
        Load data from JSON file
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory to load from
            
        Returns:
            Dict: Loaded data
        """
        try:
            file_path = self._get_file_path(filename, subdirectory, "json")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"JSON data loaded from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading JSON data: {str(e)}")
            raise
    
    def save_csv_data(self, data: List[Dict[str, Any]], filename: str, subdirectory: str = "") -> str:
        """
        Save data as CSV file
        
        Args:
            data: List of dictionaries to save
            filename: Name of the file
            subdirectory: Subdirectory to save in
            
        Returns:
            str: Path to saved file
        """
        try:
            file_path = self._get_file_path(filename, subdirectory, "csv")
            
            if not data:
                logger.warning("No data to save")
                return str(file_path)
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            logger.info(f"CSV data saved to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving CSV data: {str(e)}")
            raise
    
    def load_csv_data(self, filename: str, subdirectory: str = "") -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory to load from
            
        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            file_path = self._get_file_path(filename, subdirectory, "csv")
            
            df = pd.read_csv(file_path)
            logger.info(f"CSV data loaded from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {str(e)}")
            raise
    
    def save_excel_data(self, data: Dict[str, pd.DataFrame], filename: str, subdirectory: str = "") -> str:
        """
        Save data as Excel file with multiple sheets
        
        Args:
            data: Dictionary of DataFrames (sheet_name: DataFrame)
            filename: Name of the file
            subdirectory: Subdirectory to save in
            
        Returns:
            str: Path to saved file
        """
        try:
            file_path = self._get_file_path(filename, subdirectory, "xlsx")
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Excel data saved to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving Excel data: {str(e)}")
            raise
    
    def load_excel_data(self, filename: str, subdirectory: str = "", sheet_name: Optional[str] = None) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load data from Excel file
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory to load from
            sheet_name: Specific sheet to load (None for all sheets)
            
        Returns:
            pd.DataFrame or Dict: Loaded data
        """
        try:
            file_path = self._get_file_path(filename, subdirectory, "xlsx")
            
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                logger.info(f"Excel sheet '{sheet_name}' loaded from {file_path}")
                return df
            else:
                all_sheets = pd.read_excel(file_path, sheet_name=None)
                logger.info(f"All Excel sheets loaded from {file_path}")
                return all_sheets
                
        except Exception as e:
            logger.error(f"Error loading Excel data: {str(e)}")
            raise
    
    def save_log_file(self, log_entries: List[Dict[str, Any]], filename: str) -> str:
        """
        Save log entries to file
        
        Args:
            log_entries: List of log entry dictionaries
            filename: Name of the file
            
        Returns:
            str: Path to saved file
        """
        try:
            file_path = self._get_file_path(filename, "logs", "log")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in log_entries:
                    timestamp = entry.get('timestamp', datetime.now().isoformat())
                    level = entry.get('log_level', 'INFO')
                    message = entry.get('message', '')
                    f.write(f"[{timestamp}] {level}: {message}\n")
            
            logger.info(f"Log file saved to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving log file: {str(e)}")
            raise
    
    def create_report_archive(self, report_files: List[str], archive_name: str) -> str:
        """
        Create ZIP archive of report files
        
        Args:
            report_files: List of file paths to archive
            archive_name: Name of the archive
            
        Returns:
            str: Path to created archive
        """
        try:
            archive_path = self._get_file_path(archive_name, "exports", "zip")
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in report_files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            logger.info(f"Report archive created: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Error creating report archive: {str(e)}")
            raise
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temporary files older than specified age
        
        Args:
            max_age_hours: Maximum age in hours for temp files
        """
        try:
            temp_dir = self.base_directory / "temp"
            current_time = datetime.now()
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age.total_seconds() > (max_age_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Cleaned up temp file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
    
    def get_file_info(self, filename: str, subdirectory: str = "") -> Dict[str, Any]:
        """
        Get information about a file
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory containing the file
            
        Returns:
            Dict: File information
        """
        try:
            file_path = self._get_file_path(filename, subdirectory)
            
            if not file_path.exists():
                return {"exists": False}
            
            stat = file_path.stat()
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {"exists": False, "error": str(e)}
    
    def list_files(self, subdirectory: str = "", pattern: str = "*") -> List[Dict[str, Any]]:
        """
        List files in a subdirectory
        
        Args:
            subdirectory: Subdirectory to list
            pattern: File pattern to match
            
        Returns:
            List: File information list
        """
        try:
            dir_path = self.base_directory / subdirectory
            files = []
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "path": str(file_path)
                    })
            
            return sorted(files, key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def _get_file_path(self, filename: str, subdirectory: str = "", extension: str = "") -> Path:
        """
        Get full file path
        
        Args:
            filename: Name of the file
            subdirectory: Subdirectory
            extension: File extension
            
        Returns:
            Path: Full file path
        """
        if not filename.endswith(f".{extension}") and extension:
            filename = f"{filename}.{extension}"
        
        if subdirectory:
            return self.base_directory / subdirectory / filename
        else:
            return self.base_directory / filename
    
    def validate_file_format(self, file_path: str, expected_format: str) -> bool:
        """
        Validate file format
        
        Args:
            file_path: Path to the file
            expected_format: Expected format (csv, json, xlsx, etc.)
            
        Returns:
            bool: True if format is valid
        """
        try:
            if expected_format.lower() == 'csv':
                pd.read_csv(file_path, nrows=1)
            elif expected_format.lower() == 'json':
                with open(file_path, 'r') as f:
                    json.load(f)
            elif expected_format.lower() in ['xlsx', 'xls']:
                pd.read_excel(file_path, nrows=1)
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File format validation failed: {str(e)}")
            return False
    
    def backup_file(self, file_path: str, backup_suffix: str = "_backup") -> str:
        """
        Create backup of a file
        
        Args:
            file_path: Path to the file
            backup_suffix: Suffix for backup file
            
        Returns:
            str: Path to backup file
        """
        try:
            original_path = Path(file_path)
            backup_path = original_path.with_name(f"{original_path.stem}{backup_suffix}{original_path.suffix}")
            
            shutil.copy2(original_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise 