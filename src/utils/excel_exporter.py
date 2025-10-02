"""
Excel Exporter Module
=====================
Handles exporting analysis results to Excel format.
"""

import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import *


class ExcelExporter:
    """Handles Excel export functionality."""
    
    @staticmethod
    def export(df_catalog: pd.DataFrame, df_matches: pd.DataFrame, 
               summary: dict, artist_name: str, output_path: Path = OUTPUT_PATH) -> bool:
        """
        Export analysis results to Excel file.
        
        Args:
            df_catalog: Artist catalog DataFrame
            df_matches: Matches DataFrame
            summary: Analysis summary dictionary
            artist_name: Name of the analyzed artist
            output_path: Path to save the Excel file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"📊 Exporting results to Excel: {output_path.name}")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Sheet 1: Artist Catalog
                if not df_catalog.empty:
                    catalog_export = df_catalog[[
                        'track_name', 'album_name', 'release_date', 
                        'isrc', 'album_type', 'track_number'
                    ]].copy()
                    
                    catalog_export = catalog_export.sort_values(
                        by=['release_date', 'album_name', 'track_number'],
                        ascending=[False, True, True]
                    )
                    
                    catalog_export.to_excel(writer, sheet_name='Artist Catalog', index=False)
                    print(f"   📋 Sheet 1: Artist Catalog ({len(catalog_export):,} tracks)")
                
                # Sheet 2: Matches (Unclaimed Tracks)
                if not df_matches.empty:
                    # Sort by unclaimed percentage (highest first)
                    matches_export = df_matches.copy()
                    
                    if 'unclaimed_UnclaimedRightSharePercentage' in matches_export.columns:
                        matches_export = matches_export.sort_values(
                            by='unclaimed_UnclaimedRightSharePercentage',
                            ascending=False
                        )
                    
                    matches_export.to_excel(writer, sheet_name='Matches', index=False)
                    print(f"   🎯 Sheet 2: Matches ({len(matches_export):,} tracks)")
                    
                    # Calculate potential value
                    if 'unclaimed_UnclaimedRightSharePercentage' in matches_export.columns:
                        total_unclaimed = matches_export['unclaimed_UnclaimedRightSharePercentage'].sum()
                        print(f"   💰 Total unclaimed rights: {total_unclaimed:.2f}%")
                else:
                    # Create empty sheet with headers
                    empty_df = pd.DataFrame(columns=[
                        'track_name', 'album_name', 'release_date', 'isrc'
                    ])
                    empty_df.to_excel(writer, sheet_name='Matches', index=False)
                    print("   🎯 Sheet 2: Matches (0 tracks - no matches found)")
                
                # Sheet 3: Summary
                ExcelExporter._create_summary_sheet(writer, summary, artist_name, df_catalog, df_matches)
                print("   📝 Sheet 3: Summary")
                
                # Sheet 4: Notes
                ExcelExporter._create_notes_sheet(writer, artist_name)
                print("   📄 Sheet 4: Notes")
            
            print(f"✅ Excel report created: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _create_summary_sheet(writer, summary: dict, artist_name: str, 
                             df_catalog: pd.DataFrame, df_matches: pd.DataFrame):
        """Create summary sheet with key metrics."""
        summary_data = {
            'Metric': [
                'Artist Name',
                'Analysis Date',
                'Total Tracks in Catalog',
                'Tracks with ISRC Codes',
                'Matches Found in Unclaimed Database',
                'Match Rate (%)',
                'Unique Albums',
                'Average Unclaimed Rights (%)',
                'Dataset Source',
                'Spotify Market'
            ],
            'Value': [
                artist_name,
                summary.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                summary.get('total_tracks', 0),
                summary.get('tracks_with_isrc', 0),
                summary.get('matches_found', 0),
                f"{summary.get('match_rate', 0):.2f}",
                summary.get('unique_albums', 0),
                f"{summary.get('avg_unclaimed_percentage', 0):.2f}" if 'avg_unclaimed_percentage' in summary else 'N/A',
                'unclaimedmusicalworkrightshares.tsv',
                'United States (US)'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    @staticmethod
    def _create_notes_sheet(writer, artist_name: str):
        """Create notes sheet with methodology and assumptions."""
        notes_data = {
            'Section': [
                'Analysis Overview',
                'Data Sources',
                'Methodology',
                'ISRC Matching',
                'Limitations',
                'API Configuration',
                'Data Quality',
                'Next Steps',
                'Recommendations'
            ],
            'Details': [
                f'This report analyzes unclaimed musical work rights for {artist_name}. '
                'It cross-references the artist\'s Spotify catalog with the MLC unclaimed works database.',
                
                'Spotify Web API for artist catalog data; '
                'MLC (Mechanical Licensing Collective) unclaimed musical works database (TSV format)',
                
                '1. Fetch complete artist discography from Spotify including all albums, singles, EPs, and compilations. '
                '2. Extract ISRC codes for each track. '
                '3. Cross-reference ISRC codes against unclaimed rights database. '
                '4. Identify matches and calculate unclaimed percentages.',
                
                'ISRC (International Standard Recording Code) is used as the unique identifier. '
                'Matching is case-insensitive and whitespace-trimmed. '
                'Only exact ISRC matches are considered.',
                
                'Tracks without ISRC codes cannot be matched. '
                'Covers, remixes, and live versions may have different ISRCs. '
                'The unclaimed database may not be comprehensive or up-to-date. '
                'Some tracks may appear on multiple albums (duplicates removed).',
                
                f'Spotify Market: US; '
                f'Rate limiting: {RATE_LIMIT_DELAY}s delay between API calls; '
                f'Max retries: {MAX_RETRIES}',
                
                'Data was loaded and processed with memory optimization for large files. '
                'Only essential columns retained to reduce memory footprint. '
                'Rows without ISRC codes filtered during loading.',
                
                'If matches are found: Review the unclaimed rights percentages and consider claiming. '
                'Research historical payment data for matched tracks. '
                'Contact MLC or music rights organization for claiming process.',
                
                'Regular monitoring recommended as unclaimed database is updated periodically. '
                'Consider analyzing additional artists under the same label or management. '
                'Review release dates to prioritize newer tracks with higher streaming potential.'
            ]
        }
        
        notes_df = pd.DataFrame(notes_data)
        notes_df.to_excel(writer, sheet_name='Notes', index=False)
