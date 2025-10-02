"""
Spotify API Handler Module
===========================
Handles all interactions with the Spotify Web API.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import pandas as pd
from typing import Optional, List, Dict
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import *


class SpotifyHandler:
    """Handles Spotify API interactions."""
    
    def __init__(self):
        """Initialize Spotify API handler."""
        self.client = None
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """
        Authenticate with Spotify API using credentials.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
                print("❌ Error: Spotify credentials not found in .env file")
                print("Please ensure .env file contains:")
                print("  SPOTIFY_CLIENT_ID=your_client_id")
                print("  SPOTIFY_CLIENT_SECRET=your_client_secret")
                return False
            
            # Setup client credentials
            client_credentials_manager = SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            )
            
            self.client = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager,
                requests_timeout=10,
                retries=MAX_RETRIES
            )
            
            # Test connection
            _ = self.client.search(q='test', type='artist', limit=1)
            
            print("✅ Spotify API connection established")
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"❌ Error authenticating with Spotify: {str(e)}")
            return False
    
    def search_artist(self, artist_name: str) -> Optional[str]:
        """
        Search for an artist and return their Spotify ID.
        
        Args:
            artist_name: Name of the artist
            
        Returns:
            str: Spotify artist ID if found, None otherwise
        """
        if not self.authenticated:
            print("❌ Not authenticated with Spotify")
            return None
            
        try:
            print(f"🔍 Searching for artist: {artist_name}")
            
            results = self.client.search(q=artist_name, type='artist', limit=10)
            artists = results['artists']['items']
            
            if not artists:
                print(f"❌ Artist '{artist_name}' not found")
                return None
            
            # Try exact match first
            for artist in artists:
                if artist['name'].lower() == artist_name.lower():
                    print(f"✅ Found exact match: {artist['name']}")
                    print(f"   Spotify ID: {artist['id']}")
                    print(f"   Followers: {artist.get('followers', {}).get('total', 0):,}")
                    return artist['id']
            
            # Use closest match
            best_match = artists[0]
            print(f"📍 Using closest match: {best_match['name']}")
            print(f"   Spotify ID: {best_match['id']}")
            print(f"   Followers: {best_match.get('followers', {}).get('total', 0):,}")
            return best_match['id']
            
        except Exception as e:
            print(f"❌ Error searching for artist: {str(e)}")
            return None
    
    def get_artist_albums(self, artist_id: str) -> List[Dict]:
        """
        Get all albums for an artist.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            List of album dictionaries
        """
        albums = []
        album_types = ['album', 'single', 'compilation']
        
        for album_type in album_types:
            if VERBOSE:
                print(f"   📀 Fetching {album_type}s...")
            
            offset = 0
            limit = 50
            
            while True:
                try:
                    results = self.client.artist_albums(
                        artist_id,
                        album_type=album_type,
                        limit=limit,
                        offset=offset,
                        country='US'
                    )
                    
                    if not results['items']:
                        break
                    
                    albums.extend(results['items'])
                    
                    if len(results['items']) < limit:
                        break
                    
                    offset += limit
                    time.sleep(RATE_LIMIT_DELAY)
                    
                except Exception as e:
                    print(f"⚠️  Error fetching {album_type}s: {str(e)}")
                    break
        
        return albums
    
    def get_album_tracks(self, album_id: str) -> List[Dict]:
        """
        Get all tracks from an album.
        
        Args:
            album_id: Spotify album ID
            
        Returns:
            List of track dictionaries
        """
        try:
            results = self.client.album_tracks(album_id)
            return results['items']
        except Exception as e:
            if VERBOSE:
                print(f"⚠️  Error fetching tracks for album {album_id}: {str(e)}")
            return []
    
    def get_track_details(self, track_id: str) -> Optional[Dict]:
        """
        Get detailed information about a track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track details dictionary or None
        """
        try:
            return self.client.track(track_id)
        except Exception as e:
            if VERBOSE:
                print(f"⚠️  Error fetching track {track_id}: {str(e)}")
            return None
    
    def get_artist_catalog(self, artist_id: str) -> pd.DataFrame:
        """
        Fetch complete artist catalog with ISRC codes.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            DataFrame with artist catalog
        """
        print("🎵 Fetching artist catalog from Spotify...")
        
        catalog_data = []
        
        # Get all albums
        albums = self.get_artist_albums(artist_id)
        
        if not albums:
            print("❌ No albums found for artist")
            return pd.DataFrame()
        
        print(f"   Found {len(albums)} releases")
        
        # Process each album
        for idx, album in enumerate(albums, 1):
            if VERBOSE and idx % 10 == 0:
                print(f"   Processing release {idx}/{len(albums)}...")
            
            # Get tracks for this album
            tracks = self.get_album_tracks(album['id'])
            
            for track in tracks:
                # Get detailed track info with ISRC
                track_details = self.get_track_details(track['id'])
                
                if track_details:
                    catalog_data.append({
                        'track_name': track['name'],
                        'album_name': album['name'],
                        'release_date': album['release_date'],
                        'isrc': track_details.get('external_ids', {}).get('isrc', ''),
                        'track_id': track['id'],
                        'album_id': album['id'],
                        'album_type': album['album_type'],
                        'track_number': track.get('track_number', 0),
                        'duration_ms': track.get('duration_ms', 0)
                    })
                
                # Rate limiting
                time.sleep(RATE_LIMIT_DELAY)
        
        # Create DataFrame
        df_catalog = pd.DataFrame(catalog_data)
        
        if df_catalog.empty:
            print("❌ No tracks found in artist catalog")
            return df_catalog
        
        # Clean ISRC codes
        df_catalog['isrc_clean'] = (
            df_catalog['isrc']
            .astype(str)
            .str.strip()
            .str.upper()
            .replace('', pd.NA)
        )
        
        # Remove duplicates
        df_catalog = df_catalog.drop_duplicates(
            subset=['track_name', 'isrc_clean'],
            keep='first'
        )
        
        total_tracks = len(df_catalog)
        tracks_with_isrc = df_catalog['isrc_clean'].notna().sum()
        
        print(f"✅ Artist catalog loaded:")
        print(f"   📊 Total unique tracks: {total_tracks:,}")
        print(f"   🔑 Tracks with ISRC: {tracks_with_isrc:,}")
        print(f"   📀 Unique albums: {df_catalog['album_name'].nunique():,}")
        
        return df_catalog
