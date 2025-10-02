"""
Analysis Engine Module
======================
Handles cross-referencing and analysis logic.
"""

import pandas as pd
from typing import Tuple
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import *


class AnalysisEngine:
    """Handles cross-referencing and analysis of data."""
    
    @staticmethod
    def cross_reference(df_catalog: pd.DataFrame, df_unclaimed: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Cross-reference ISRC codes between catalog and unclaimed datasets.
        
        Args:
            df_catalog: Artist catalog DataFrame
            df_unclaimed: Unclaimed rights DataFrame
            
        Returns:
            Tuple of (matches DataFrame, statistics dict)
        """
        print("🔄 Cross-referencing ISRC codes...")
        
        if df_catalog is None or df_catalog.empty:
            print("❌ Catalog DataFrame is empty")
            return pd.DataFrame(), {}
        
        if df_unclaimed is None or df_unclaimed.empty:
            print("❌ Unclaimed DataFrame is empty")
            return pd.DataFrame(), {}
        
        # Get tracks with valid ISRC codes
        catalog_with_isrc = df_catalog[df_catalog['isrc_clean'].notna()].copy()
        
        if catalog_with_isrc.empty:
            print("⚠️  No tracks with ISRC codes in artist catalog")
            return pd.DataFrame(), {}
        
        print(f"   Checking {len(catalog_with_isrc):,} tracks against unclaimed database...")
        
        matches = []
        match_count = 0
        
        # Use indexed unclaimed DataFrame for fast lookups
        for idx, row in catalog_with_isrc.iterrows():
            isrc = row['isrc_clean']
            
            # Check if ISRC exists in unclaimed dataset
            if isrc in df_unclaimed.index:
                match_count += 1
                
                # Get unclaimed data for this ISRC
                unclaimed_data = df_unclaimed.loc[isrc]
                
                # Handle multiple rows with same ISRC
                if isinstance(unclaimed_data, pd.DataFrame):
                    # Multiple matches - take first one
                    unclaimed_data = unclaimed_data.iloc[0]
                
                # Combine catalog and unclaimed data
                match_record = {
                    'track_name': row['track_name'],
                    'album_name': row['album_name'],
                    'release_date': row['release_date'],
                    'isrc': row['isrc'],
                    'album_type': row['album_type'],
                    'duration_ms': row['duration_ms'],
                    'spotify_track_id': row['track_id']
                }
                
                # Add unclaimed data columns
                for col in df_unclaimed.columns:
                    if col not in ['ISRC_CLEAN'] and col not in match_record:
                        match_record[f'unclaimed_{col}'] = unclaimed_data.get(col, None)
                
                matches.append(match_record)
                
                if VERBOSE and match_count % 10 == 0:
                    print(f"   Found {match_count} matches so far...")
        
        # Create matches DataFrame
        df_matches = pd.DataFrame(matches)
        
        # Calculate statistics
        total_catalog = len(catalog_with_isrc)
        matches_found = len(df_matches)
        match_rate = (matches_found / total_catalog * 100) if total_catalog > 0 else 0
        
        stats = {
            'total_catalog_tracks': len(df_catalog),
            'catalog_with_isrc': total_catalog,
            'matches_found': matches_found,
            'match_rate': match_rate,
            'unique_albums': df_catalog['album_name'].nunique()
        }
        
        print(f"✅ Cross-reference complete:")
        print(f"   🎯 Matches found: {matches_found:,}")
        print(f"   📊 Catalog tracks checked: {total_catalog:,}")
        print(f"   📈 Match rate: {match_rate:.2f}%")
        
        if matches_found > 0:
            # Calculate total unclaimed percentage
            if 'unclaimed_UnclaimedRightSharePercentage' in df_matches.columns:
                avg_unclaimed = df_matches['unclaimed_UnclaimedRightSharePercentage'].mean()
                print(f"   💰 Average unclaimed rights: {avg_unclaimed:.2f}%")
                stats['avg_unclaimed_percentage'] = avg_unclaimed
        
        return df_matches, stats
    
    @staticmethod
    def generate_summary(df_catalog: pd.DataFrame, df_matches: pd.DataFrame, stats: dict) -> dict:
        """
        Generate analysis summary.
        
        Args:
            df_catalog: Artist catalog DataFrame
            df_matches: Matches DataFrame
            stats: Statistics dictionary
            
        Returns:
            Summary dictionary
        """
        summary = {
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tracks': stats.get('total_catalog_tracks', 0),
            'tracks_with_isrc': stats.get('catalog_with_isrc', 0),
            'matches_found': stats.get('matches_found', 0),
            'match_rate': stats.get('match_rate', 0),
            'unique_albums': stats.get('unique_albums', 0)
        }
        
        if not df_matches.empty and 'unclaimed_UnclaimedRightSharePercentage' in df_matches.columns:
            summary['avg_unclaimed_percentage'] = stats.get('avg_unclaimed_percentage', 0)
            summary['total_unclaimed_value'] = df_matches['unclaimed_UnclaimedRightSharePercentage'].sum()
        
        return summary
