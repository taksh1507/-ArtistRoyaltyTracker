"""
Music Rights Analyzer - Main Application
=========================================

Professional music rights analysis tool for identifying unclaimed works.

Author: GitHub Copilot
Date: October 2025
License: MIT
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from src.utils import DatasetLoader, SpotifyHandler, AnalysisEngine, ExcelExporter
from config.settings import *


class MusicRightsAnalyzer:
    """Main application orchestrator."""
    
    def __init__(self, artist_name: str = DEFAULT_ARTIST, output_path: Path = OUTPUT_PATH):
        """
        Initialize the analyzer.
        
        Args:
            artist_name: Name of the artist to analyze
            output_path: Path for output Excel file
        """
        self.artist_name = artist_name
        self.output_path = output_path
        self.dataset_loader = DatasetLoader()
        self.spotify_handler = SpotifyHandler()
        self.df_catalog = None
        self.df_matches = None
        self.stats = {}
        
    def run(self) -> bool:
        """
        Execute the complete analysis workflow.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "=" * 70)
        print("🎵 MUSIC RIGHTS ANALYSIS TOOL")
        print("=" * 70)
        print(f"Artist: {self.artist_name}")
        print(f"Output: {self.output_path}")
        print("=" * 70 + "\n")
        
        # Step 1: Authenticate with Spotify
        print("🔐 Step 1/5: Authenticating with Spotify API...")
        if not self.spotify_handler.authenticate():
            return False
        print()
        
        # Step 2: Load Dataset
        print("📊 Step 2/5: Loading unclaimed rights dataset...")
        if not self.dataset_loader.load():
            return False
        print()
        
        # Step 3: Search for Artist
        print("🎤 Step 3/5: Searching for artist on Spotify...")
        artist_id = self.spotify_handler.search_artist(self.artist_name)
        if not artist_id:
            return False
        print()
        
        # Step 4: Fetch Artist Catalog
        print("💿 Step 4/5: Fetching artist catalog...")
        self.df_catalog = self.spotify_handler.get_artist_catalog(artist_id)
        if self.df_catalog.empty:
            print("❌ Failed to fetch artist catalog")
            return False
        print()
        
        # Step 5: Cross-reference and Export
        print("🔍 Step 5/5: Cross-referencing and generating report...")
        
        # Perform cross-reference
        df_unclaimed = self.dataset_loader.get_dataframe()
        self.df_matches, self.stats = AnalysisEngine.cross_reference(
            self.df_catalog, 
            df_unclaimed
        )
        
        # Generate summary
        summary = AnalysisEngine.generate_summary(
            self.df_catalog, 
            self.df_matches, 
            self.stats
        )
        
        # Export to Excel
        success = ExcelExporter.export(
            self.df_catalog,
            self.df_matches,
            summary,
            self.artist_name,
            self.output_path
        )
        
        if not success:
            return False
        
        print("\n" + "=" * 70)
        print("✨ ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📄 Report generated: {self.output_path}")
        print(f"📊 Total tracks analyzed: {self.stats.get('total_catalog_tracks', 0):,}")
        print(f"🎯 Matches found: {self.stats.get('matches_found', 0):,}")
        
        if self.stats.get('matches_found', 0) > 0:
            print(f"💰 Average unclaimed rights: {self.stats.get('avg_unclaimed_percentage', 0):.2f}%")
            print("\n⚠️  ACTION REQUIRED: Review the 'Matches' sheet in the Excel file")
            print("   to identify tracks with unclaimed rights.")
        else:
            print("\n✅ Great news! No unclaimed rights found for this artist.")
        
        print("=" * 70 + "\n")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Analyze unclaimed musical work rights for an artist'
    )
    parser.add_argument(
        '--artist',
        type=str,
        default=DEFAULT_ARTIST,
        help=f'Artist name to analyze (default: {DEFAULT_ARTIST})'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=str(OUTPUT_PATH),
        help=f'Output Excel file path (default: {OUTPUT_PATH})'
    )
    
    args = parser.parse_args()
    
    # Override output path if provided
    output_path = OUTPUT_PATH
    if args.output != str(OUTPUT_PATH):
        output_path = Path(args.output)
    
    # Create and run analyzer
    analyzer = MusicRightsAnalyzer(artist_name=args.artist, output_path=output_path)
    
    try:
        success = analyzer.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
