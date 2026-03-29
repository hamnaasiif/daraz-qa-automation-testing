"""
Configuration for the framework
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Framework configuration"""
    
    # URLs
    BASE_URL = "https://www.daraz.pk"
    
    # Browser
    BROWSER = "chromium"
    HEADLESS = False
    
    # Timeouts
    TIMEOUT = 30000  # 30 seconds
    
    # Folders
    SCREENSHOTS_DIR = "screenshots"
    REPORTS_DIR = "reports"
    TEST_DATA_DIR = "test_data"