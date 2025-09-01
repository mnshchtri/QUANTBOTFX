"""
Data Configuration for TrimurtiFX
Handles data source selection, caching, and consistent data handling
"""

import os
import json
import pandas as pd
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Available data sources"""
    LOCAL = "local"
    API = "api"
    HYBRID = "hybrid"  # Use local if available, fallback to API

class DataConfig:
    """Configuration for data handling across the application"""
    
    def __init__(self):
        self.data_source = self._get_data_source()
        self.cache_dir = "storage/data_cache"
        self.cache_timeout = 3600  # 1 hour
        self._ensure_cache_dir()
    
    def _get_data_source(self) -> DataSource:
        """Get data source from environment or default to API"""
        env_source = os.getenv("TRIMURTIFX_DATA_SOURCE", "api").lower()
        
        if env_source == "local":
            return DataSource.LOCAL
        elif env_source == "hybrid":
            return DataSource.HYBRID
        else:
            return DataSource.API
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.data_cache_dir, exist_ok=True)
    
    @property
    def data_cache_dir(self) -> str:
        """Get data cache directory"""
        return self.cache_dir
    
    def get_cache_path(self, instrument: str, timeframe: str, days_back: int) -> str:
        """Get cache file path for data"""
        filename = f"{instrument}_{timeframe}_{days_back}d.csv"
        return os.path.join(self.data_cache_dir, filename)
    
    def is_cached_data_available(self, instrument: str, timeframe: str, days_back: int) -> bool:
        """Check if cached data is available and fresh"""
        cache_path = self.get_cache_path(instrument, timeframe, days_back)
        
        if not os.path.exists(cache_path):
            return False
        
        # Check if cache is fresh
        file_time = os.path.getmtime(cache_path)
        if (datetime.now().timestamp() - file_time) > self.cache_timeout:
            return False
        
        return True
    
    def load_cached_data(self, instrument: str, timeframe: str, days_back: int) -> Optional[pd.DataFrame]:
        """Load data from cache"""
        cache_path = self.get_cache_path(instrument, timeframe, days_back)
        
        try:
            df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            logger.info(f"📁 Loaded cached data: {len(df)} candles for {instrument} {timeframe}")
            return df
        except Exception as e:
            logger.warning(f"⚠️ Error loading cached data: {e}")
            return None
    
    def save_data_to_cache(self, df: pd.DataFrame, instrument: str, timeframe: str, days_back: int):
        """Save data to cache"""
        cache_path = self.get_cache_path(instrument, timeframe, days_back)
        
        try:
            df.to_csv(cache_path)
            logger.info(f"💾 Cached data: {len(df)} candles for {instrument} {timeframe}")
        except Exception as e:
            logger.error(f"⚠️ Error caching data: {e}")
    
    def get_data_loading_strategy(self, instrument: str, timeframe: str, days_back: int) -> str:
        """Determine data loading strategy based on configuration"""
        if self.data_source == DataSource.LOCAL:
            return "local_only"
        elif self.data_source == DataSource.API:
            return "api_only"
        elif self.data_source == DataSource.HYBRID:
            if self.is_cached_data_available(instrument, timeframe, days_back):
                return "local_first"
            else:
                return "api_with_cache"
        else:
            return "api_only"
    
    def get_available_instruments(self) -> List[str]:
        """Get available instruments based on data source"""
        if self.data_source == DataSource.LOCAL:
            # Check what's available in cache
            instruments = []
            if os.path.exists(self.data_cache_dir):
                for file in os.listdir(self.data_cache_dir):
                    if file.endswith('.csv'):
                        instrument = file.split('_')[0]
                        if instrument not in instruments:
                            instruments.append(instrument)
            return instruments if instruments else ["GBP_JPY", "EUR_USD", "USD_JPY"]
        else:
            # API instruments
            return ["GBP_JPY", "EUR_USD", "USD_JPY", "GBP_USD", "EUR_JPY"]
    
    def get_available_timeframes(self) -> Dict[str, str]:
        """Get available timeframes"""
        return {
            "1 Minute": "M1",
            "5 Minutes": "M5", 
            "15 Minutes": "M15",
            "30 Minutes": "M30",
            "1 Hour": "H1",
            "4 Hours": "H4",
            "Daily": "D1"
        }
    
    def get_data_info(self) -> Dict[str, Any]:
        """Get information about current data configuration"""
        return {
            "data_source": self.data_source.value,
            "cache_dir": self.data_cache_dir,
            "cache_timeout": self.cache_timeout,
            "available_instruments": self.get_available_instruments(),
            "available_timeframes": self.get_available_timeframes()
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear all cached data"""
        try:
            if os.path.exists(self.data_cache_dir):
                for file in os.listdir(self.data_cache_dir):
                    if file.endswith('.csv'):
                        os.remove(os.path.join(self.data_cache_dir, file))
                logger.info("🗑️ Cache cleared successfully")
                return {"status": "success", "message": "Cache cleared successfully"}
            else:
                return {"status": "info", "message": "Cache directory does not exist"}
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {"status": "error", "message": f"Error clearing cache: {str(e)}"}
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data"""
        cache_info = {
            "cache_dir": self.data_cache_dir,
            "cache_timeout": self.cache_timeout,
            "cached_files": [],
            "total_files": 0,
            "total_size_mb": 0
        }
        
        if os.path.exists(self.data_cache_dir):
            total_size = 0
            for file in os.listdir(self.data_cache_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(self.data_cache_dir, file)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    cache_info["cached_files"].append({
                        "filename": file,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
            
            cache_info["total_files"] = len(cache_info["cached_files"])
            cache_info["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        return cache_info

# Global data config instance
_data_config = None

def get_data_config() -> DataConfig:
    """Get global data configuration instance"""
    global _data_config
    if _data_config is None:
        _data_config = DataConfig()
    return _data_config

def set_data_source(source: str) -> Dict[str, Any]:
    """Set data source (local, api, hybrid)"""
    valid_sources = ["local", "api", "hybrid"]
    if source.lower() not in valid_sources:
        return {"status": "error", "message": f"Invalid data source. Must be one of: {valid_sources}"}
    
    os.environ["TRIMURTIFX_DATA_SOURCE"] = source.lower()
    global _data_config
    _data_config = None  # Reset to reload config
    logger.info(f"Data source set to: {source}")
    return {"status": "success", "message": f"Data source set to: {source}"}

def get_data_source_info() -> Dict[str, Any]:
    """Get current data source information"""
    config = get_data_config()
    return config.get_data_info() 