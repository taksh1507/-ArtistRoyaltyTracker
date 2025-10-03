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
        Export analysis results to Excel file with exactly 3 sheets.
        
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
                    # Select and rename columns for clarity
                    catalog_export = df_catalog[[
                        'track_name', 'album_name', 'release_date', 'isrc'
                    ]].copy()
                    
                    # Rename columns to match requirements
                    catalog_export.columns = ['Track Name', 'Album Name', 'Release Date', 'ISRC Code']
                    
                    catalog_export = catalog_export.sort_values(
                        by=['Release Date', 'Album Name'],
                        ascending=[False, True]
                    )
                    
                    catalog_export.to_excel(writer, sheet_name='Artist Catalog', index=False)
                    print(f"   📋 Sheet 1: Artist Catalog ({len(catalog_export):,} tracks)")
                
                # Sheet 2: Matches (Unclaimed Tracks)
                if not df_matches.empty:
                    # Select relevant columns for matches
                    matches_columns = ['track_name', 'album_name', 'release_date', 'isrc']
                    
                    # Add unclaimed percentage if available
                    if 'unclaimed_UnclaimedRightSharePercentage' in df_matches.columns:
                        matches_columns.append('unclaimed_UnclaimedRightSharePercentage')
                    
                    # Add any other relevant unclaimed data columns
                    for col in df_matches.columns:
                        if col.startswith('unclaimed_') and col not in matches_columns:
                            matches_columns.append(col)
                    
                    matches_export = df_matches[matches_columns].copy()
                    
                    # Rename columns for clarity
                    column_rename = {
                        'track_name': 'Track Name',
                        'album_name': 'Album Name', 
                        'release_date': 'Release Date',
                        'isrc': 'ISRC Code',
                        'unclaimed_UnclaimedRightSharePercentage': 'Unclaimed Rights %'
                    }
                    matches_export.rename(columns=column_rename, inplace=True)
                    
                    # Add notes column
                    matches_export['Notes'] = 'Matched in unclaimed works database'
                    
                    # Sort by unclaimed percentage (highest first) if available
                    if 'Unclaimed Rights %' in matches_export.columns:
                        matches_export = matches_export.sort_values(
                            by='Unclaimed Rights %',
                            ascending=False
                        )
                    
                    matches_export.to_excel(writer, sheet_name='Matches', index=False)
                    print(f"   🎯 Sheet 2: Matches ({len(matches_export):,} tracks)")
                    
                    # Calculate potential value
                    if 'Unclaimed Rights %' in matches_export.columns:
                        total_unclaimed = matches_export['Unclaimed Rights %'].sum()
                        print(f"   💰 Total unclaimed rights: {total_unclaimed:.2f}%")
                else:
                    # Create empty sheet with headers
                    empty_df = pd.DataFrame(columns=[
                        'Track Name', 'Album Name', 'Release Date', 'ISRC Code', 'Notes'
                    ])
                    empty_df.to_excel(writer, sheet_name='Matches', index=False)
                    print("   🎯 Sheet 2: Matches (0 tracks - no matches found)")
                
                # Sheet 3: Notes / Observations
                ExcelExporter._create_notes_observations_sheet(writer, summary, artist_name, df_catalog, df_matches)
                print("   📝 Sheet 3: Notes / Observations")
            
            print(f"✅ Excel report created with 3 sheets: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _create_notes_observations_sheet(writer, summary: dict, artist_name: str, 
                                       df_catalog: pd.DataFrame, df_matches: pd.DataFrame):
        """Create combined Notes/Observations sheet with summary metrics and methodology."""
        
        # Combine summary metrics and observations into one comprehensive sheet
        notes_data = []
        
        # Analysis Summary Section
        notes_data.extend([
            ['ANALYSIS SUMMARY', ''],
            ['Artist Name', artist_name],
            ['Analysis Date', summary.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
            ['Total Tracks in Catalog', summary.get('total_tracks', 0)],
            ['Tracks with ISRC Codes', summary.get('tracks_with_isrc', 0)],
            ['Matches Found in Unclaimed Database', summary.get('matches_found', 0)],
            ['Match Rate (%)', f"{summary.get('match_rate', 0):.2f}"],
            ['Unique Albums', summary.get('unique_albums', 0)],
            ['Average Unclaimed Rights (%)', f"{summary.get('avg_unclaimed_percentage', 0):.2f}" if 'avg_unclaimed_percentage' in summary else 'N/A'],
            ['Dataset Source', 'unclaimedmusicalworkrightshares.tsv'],
            ['Spotify Market', 'United States (US)'],
            ['', ''],  # Empty row for separation
            
            # Methodology and Observations
            ['METHODOLOGY & OBSERVATIONS', ''],
            ['Data Sources', 'Spotify Web API for artist catalog data; MLC (Mechanical Licensing Collective) unclaimed musical works database (TSV format)'],
            ['Matching Process', 'ISRC (International Standard Recording Code) is used as the unique identifier. Matching is case-insensitive and whitespace-trimmed. Only exact ISRC matches are considered.'],
            ['Processing Approach', '1. Fetch complete artist discography from Spotify including all albums, singles, EPs, and compilations. 2. Extract ISRC codes for each track. 3. Cross-reference ISRC codes against unclaimed rights database. 4. Identify matches and calculate unclaimed percentages.'],
            ['', ''],  # Empty row for separation
            
            # Key Observations and Limitations
            ['KEY OBSERVATIONS & LIMITATIONS', ''],
            ['Missing ISRC Codes', f'Tracks without ISRC codes cannot be matched. Of {summary.get("total_tracks", 0)} total tracks, {summary.get("tracks_with_isrc", 0)} have ISRC codes ({(summary.get("tracks_with_isrc", 0) / max(summary.get("total_tracks", 1), 1) * 100):.1f}%).'],
            ['Data Quality Considerations', 'Covers, remixes, and live versions may have different ISRCs. The unclaimed database may not be comprehensive or up-to-date. Some tracks may appear on multiple albums (duplicates removed).'],
            ['API Configuration', f'Spotify Market: US; Rate limiting: {RATE_LIMIT_DELAY}s delay between API calls; Max retries: {MAX_RETRIES}'],
            ['Large Dataset Handling', 'Data was loaded and processed with memory optimization for large files. Only essential columns retained to reduce memory footprint. Rows without ISRC codes filtered during loading.'],
            ['', ''],  # Empty row for separation
            
            # Recommendations and Next Steps
            ['RECOMMENDATIONS & NEXT STEPS', ''],
            ['If Matches Found', 'Review the unclaimed rights percentages and consider claiming. Research historical payment data for matched tracks. Contact MLC or music rights organization for claiming process.'],
            ['Ongoing Monitoring', 'Regular monitoring recommended as unclaimed database is updated periodically. Consider analyzing additional artists under the same label or management.'],
            ['Priority Analysis', 'Review release dates to prioritize newer tracks with higher streaming potential. Focus on tracks with higher unclaimed percentages first.'],
            ['', ''],  # Empty row for separation
            
            # Additional Insights
            ['ADDITIONAL INSIGHTS', '']
        ])
        
        # Add match-specific insights if matches were found
        if not df_matches.empty:
            if 'unclaimed_UnclaimedRightSharePercentage' in df_matches.columns:
                total_unclaimed = df_matches['unclaimed_UnclaimedRightSharePercentage'].sum()
                avg_unclaimed = df_matches['unclaimed_UnclaimedRightSharePercentage'].mean()
                max_unclaimed = df_matches['unclaimed_UnclaimedRightSharePercentage'].max()
                
                notes_data.extend([
                    ['Total Unclaimed Rights Found', f'{total_unclaimed:.2f}%'],
                    ['Average Unclaimed Rights per Match', f'{avg_unclaimed:.2f}%'],
                    ['Highest Single Track Unclaimed Rights', f'{max_unclaimed:.2f}%'],
                ])
                
            # Add insights about release date distribution
            if 'release_date' in df_matches.columns:
                df_matches_copy = df_matches.copy()
                df_matches_copy['release_year'] = pd.to_datetime(df_matches_copy['release_date']).dt.year
                recent_matches = df_matches_copy[df_matches_copy['release_year'] >= 2020]
                
                notes_data.extend([
                    ['Matches from Recent Years (2020+)', f'{len(recent_matches)} out of {len(df_matches)} matches'],
                    ['Oldest Match Release Year', f'{df_matches_copy["release_year"].min():.0f}' if not df_matches_copy['release_year'].isna().all() else 'N/A'],
                    ['Newest Match Release Year', f'{df_matches_copy["release_year"].max():.0f}' if not df_matches_copy['release_year'].isna().all() else 'N/A']
                ])
        else:
            notes_data.extend([
                ['Match Results', 'No matches found in unclaimed works database'],
                ['Potential Reasons', 'All rights may be properly claimed, or tracks may not appear in the current unclaimed database'],
                ['Recommendation', 'Consider re-running analysis periodically as the unclaimed database is updated']
            ])
        
        # Convert to DataFrame
        notes_df = pd.DataFrame(notes_data, columns=['Category', 'Details'])
        notes_df.to_excel(writer, sheet_name='Notes - Observations', index=False)
