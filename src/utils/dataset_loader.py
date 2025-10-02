"""
Dataset Loader Module
=====================
Handles loading and preprocessing of the unclaimed musical work rights dataset.
Optimized for large files (6+ GB).
"""

import pandas as pd
import os
from typing import Optional, Set
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import *


class DatasetLoader:
    """Handles loading and preprocessing of TSV dataset."""
    
    def __init__(self, filepath: Path = DATASET_PATH):
        """
        Initialize the dataset loader.
        
        Args:
            filepath: Path to the TSV file
        """
        self.filepath = filepath
        self.df = None
        self.isrc_column = None
        
        # Create data directory if it doesn't exist
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
    def check_file_exists(self) -> bool:
        """Check if dataset file exists and display info."""
        if not self.filepath.exists():
            print(f"❌ Dataset file not found: {self.filepath}")
            print(f"📁 Expected location: {self.filepath.parent}")
            print(f"💡 Tip: Download the TSV file and place it in the 'data/' folder")
            return False
        
        file_size = self.filepath.stat().st_size
        file_size_gb = file_size / (1024**3)
        
        if file_size_gb >= 1:
            print(f"✅ Dataset found: {self.filepath.name} ({file_size_gb:.2f} GB)")
        else:
            file_size_mb = file_size / (1024**2)
            print(f"✅ Dataset found: {self.filepath.name} ({file_size_mb:.2f} MB)")
            
        return True
    
    def _identify_isrc_column(self, sample_df: pd.DataFrame) -> Optional[str]:
        """Identify the ISRC column from sample data."""
        isrc_columns = [col for col in sample_df.columns if 'isrc' in col.lower()]
        
        if not isrc_columns:
            print("⚠️  Warning: No ISRC column found in dataset")
            print(f"📋 Available columns: {list(sample_df.columns)}")
            return None
            
        isrc_col = isrc_columns[0]
        print(f"🔑 Found ISRC column: '{isrc_col}'")
        return isrc_col
    
    def _get_essential_columns(self, all_columns: list) -> list:
        """Filter columns to keep only essential ones."""
        if not OPTIMIZE_COLUMNS:
            return all_columns
            
        essential_cols = [
            col for col in all_columns 
            if any(keyword in col.lower() for keyword in ESSENTIAL_KEYWORDS)
        ]
        
        if not essential_cols:
            # Fallback: keep first 10 columns
            essential_cols = all_columns[:10]
            
        return essential_cols
    
    def load(self) -> bool:
        """
        Load the dataset with memory optimization.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.check_file_exists():
                return False
                
            print("📊 Analyzing dataset structure...")
            
            # Peek at file structure
            df_peek = pd.read_csv(self.filepath, sep='\t', nrows=1000, low_memory=False)
            
            # Identify ISRC column
            self.isrc_column = self._identify_isrc_column(df_peek)
            
            if not self.isrc_column:
                print("⚠️  Loading without ISRC optimization...")
                self.df = pd.read_csv(self.filepath, sep='\t', low_memory=False)
                return True
            
            # Get essential columns
            essential_cols = self._get_essential_columns(list(df_peek.columns))
            print(f"📦 Loading {len(essential_cols)} essential columns (memory optimization)")
            
            if VERBOSE:
                print(f"   Columns: {', '.join(essential_cols[:5])}{'...' if len(essential_cols) > 5 else ''}")
            
            # Load in chunks
            print("📥 Loading data in chunks...")
            chunks = []
            total_rows = 0
            isrc_set: Set[str] = set()
            
            chunk_iterator = pd.read_csv(
                self.filepath,
                sep='\t',
                usecols=essential_cols,
                chunksize=CHUNK_SIZE,
                low_memory=False,
                dtype={self.isrc_column: str}
            )
            
            for i, chunk in enumerate(chunk_iterator):
                # Clean ISRC codes
                chunk['ISRC_CLEAN'] = (
                    chunk[self.isrc_column]
                    .fillna('')
                    .str.strip()
                    .str.upper()
                )
                
                # Filter rows without ISRC if configured
                if FILTER_NO_ISRC:
                    chunk = chunk[chunk['ISRC_CLEAN'] != '']
                
                if not chunk.empty:
                    chunks.append(chunk)
                    isrc_set.update(chunk['ISRC_CLEAN'].unique())
                    total_rows += len(chunk)
                
                # Progress update
                if VERBOSE and (i + 1) % 5 == 0:
                    print(f"   Processed {total_rows:,} rows with valid ISRC codes...")
            
            # Combine chunks
            print("🔄 Combining data...")
            self.df = pd.concat(chunks, ignore_index=True)
            
            # Create index for fast lookups
            print("🗂️  Creating ISRC index for fast lookups...")
            self.df = self.df.set_index('ISRC_CLEAN', drop=False)
            
            memory_mb = self.df.memory_usage(deep=True).sum() / (1024**2)
            
            print(f"✅ Dataset loaded and optimized:")
            print(f"   📊 Records with valid ISRC: {len(self.df):,}")
            print(f"   🔑 Unique ISRC codes: {len(isrc_set):,}")
            print(f"   💾 Memory usage: ~{memory_mb:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading dataset: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the loaded dataframe."""
        return self.df
    
    def search_isrc(self, isrc: str) -> pd.DataFrame:
        """
        Search for a specific ISRC code.
        
        Args:
            isrc: ISRC code to search for
            
        Returns:
            DataFrame with matching records
        """
        if self.df is None:
            return pd.DataFrame()
            
        isrc_clean = isrc.strip().upper()
        
        if isrc_clean in self.df.index:
            result = self.df.loc[isrc_clean]
            if isinstance(result, pd.Series):
                result = result.to_frame().T
            return result
        
        return pd.DataFrame()
