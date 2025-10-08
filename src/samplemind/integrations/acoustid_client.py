"""
AcoustID Integration Module

Audio fingerprinting, sample identification, and metadata enrichment
using AcoustID and MusicBrainz databases.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import acoustid
import musicbrainzngs
from loguru import logger


# Configure MusicBrainz
musicbrainzngs.set_useragent(
    "SampleMind AI",
    "2.0.0-beta",
    "https://samplemind.ai"
)


class AcoustIDClient:
    """
    AcoustID and MusicBrainz integration for audio identification.
    
    Features:
    - Audio fingerprinting with chromaprint
    - MusicBrainz metadata retrieval
    - Duplicate detection
    - Cover art download support
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AcoustID client.
        
        Args:
            api_key: AcoustID API key (optional, uses default if not provided)
        """
        # Use demo key if none provided (replace with actual key in production)
        self.api_key = api_key or "8XaBELgH"  # Demo key
        logger.info("AcoustIDClient initialized")
    
    def identify(
        self,
        audio_path: Path,
        threshold: float = 0.8
    ) -> List[Dict]:
        """
        Identify audio file using AcoustID fingerprinting.
        
        Args:
            audio_path: Path to audio file
            threshold: Minimum confidence threshold (0-1)
            
        Returns:
            List of matches with metadata
        """
        try:
            # Generate fingerprint and query AcoustID
            results = acoustid.match(self.api_key, str(audio_path))
            
            matches = []
            for score, recording_id, title, artist in results:
                if score >= threshold:
                    logger.info(f"Match found: {artist} - {title} (score: {score:.2f})")
                    
                    # Fetch detailed metadata from MusicBrainz
                    metadata = self._get_musicbrainz_metadata(recording_id)
                    
                    matches.append({
                        'score': float(score),
                        'recording_id': recording_id,
                        'title': title,
                        'artist': artist,
                        'metadata': metadata
                    })
            
            if matches:
                logger.info(f"Found {len(matches)} matches for {audio_path.name}")
            else:
                logger.warning(f"No matches found for {audio_path.name}")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error identifying audio: {e}")
            return []
    
    def _get_musicbrainz_metadata(
        self,
        recording_id: str
    ) -> Optional[Dict]:
        """
        Fetch detailed metadata from MusicBrainz.
        
        Args:
            recording_id: MusicBrainz recording ID
            
        Returns:
            Metadata dictionary or None
        """
        try:
            # Fetch recording with includes
            recording = musicbrainzngs.get_recording_by_id(
                recording_id,
                includes=['artists', 'releases', 'tags', 'ratings', 'isrcs']
            )
            
            rec = recording['recording']
            
            # Extract metadata
            metadata = {
                'mbid': recording_id,
                'title': rec.get('title'),
                'length': rec.get('length'),  # in milliseconds
                'artist': rec.get('artist-credit-phrase'),
            }
            
            # Album information
            if 'release-list' in rec and len(rec['release-list']) > 0:
                release = rec['release-list'][0]
                metadata['album'] = release.get('title')
                metadata['date'] = release.get('date')
                metadata['year'] = release.get('date', '')[:4] if 'date' in release else None
                
                # Cover art ID
                if 'id' in release:
                    metadata['release_id'] = release['id']
            
            # Tags (genres, moods)
            if 'tag-list' in rec:
                metadata['tags'] = [tag['name'] for tag in rec['tag-list']]
            
            # ISRC codes
            if 'isrc-list' in rec:
                metadata['isrc'] = [isrc for isrc in rec['isrc-list']]
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Failed to fetch MusicBrainz metadata: {e}")
            return None
    
    def get_cover_art_url(self, release_id: str) -> Optional[str]:
        """
        Get cover art URL from MusicBrainz Cover Art Archive.
        
        Args:
            release_id: MusicBrainz release ID
            
        Returns:
            Cover art URL or None
        """
        try:
            # Cover Art Archive URL format
            url = f"https://coverartarchive.org/release/{release_id}/front-500"
            return url
        except Exception as e:
            logger.error(f"Error getting cover art URL: {e}")
            return None
    
    def find_duplicates(
        self,
        directory: Path,
        threshold: float = 0.95
    ) -> List[Tuple[Path, Path]]:
        """
        Find duplicate audio files in a directory using fingerprinting.
        
        Args:
            directory: Directory to scan
            threshold: Similarity threshold for duplicates (0-1)
            
        Returns:
            List of (file1, file2) tuples representing duplicates
        """
        logger.info(f"Scanning {directory} for duplicates...")
        
        # Supported audio formats
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aiff']
        
        # Find all audio files
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(directory.rglob(f'*{ext}'))
        
        logger.info(f"Found {len(audio_files)} audio files")
        
        # Generate fingerprints
        fingerprints = {}
        for audio_file in audio_files:
            try:
                # Generate fingerprint
                duration, fp = acoustid.fingerprint_file(str(audio_file))
                fingerprints[audio_file] = (duration, fp)
            except Exception as e:
                logger.warning(f"Failed to fingerprint {audio_file.name}: {e}")
        
        # Find duplicates by comparing fingerprints
        duplicates = []
        files = list(fingerprints.keys())
        
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                file1, file2 = files[i], files[j]
                fp1 = fingerprints[file1][1]
                fp2 = fingerprints[file2][1]
                
                # Compare fingerprints (exact match for duplicates)
                if fp1 == fp2:
                    duplicates.append((file1, file2))
                    logger.info(f"Duplicate found: {file1.name} == {file2.name}")
        
        logger.info(f"Found {len(duplicates)} duplicate pairs")
        return duplicates
    
    async def identify_async(
        self,
        audio_path: Path,
        threshold: float = 0.8
    ) -> List[Dict]:
        """
        Async wrapper for audio identification.
        
        Args:
            audio_path: Path to audio file
            threshold: Confidence threshold
            
        Returns:
            List of matches
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.identify,
            audio_path,
            threshold
        )
    
    async def batch_identify(
        self,
        audio_files: List[Path],
        threshold: float = 0.8
    ) -> Dict[str, List[Dict]]:
        """
        Batch identify multiple audio files.
        
        Args:
            audio_files: List of audio files
            threshold: Confidence threshold
            
        Returns:
            Dictionary mapping files to matches
        """
        results = {}
        
        for audio_file in audio_files:
            try:
                matches = await self.identify_async(audio_file, threshold)
                results[str(audio_file)] = matches
                logger.info(f"Identified {audio_file.name}: {len(matches)} matches")
            except Exception as e:
                logger.error(f"Failed to identify {audio_file}: {e}")
                results[str(audio_file)] = []
        
        return results
    
    def enrich_metadata(
        self,
        audio_path: Path,
        auto_select: bool = True
    ) -> Optional[Dict]:
        """
        Enrich audio file metadata using best match.
        
        Args:
            audio_path: Path to audio file
            auto_select: Auto-select best match if True
            
        Returns:
            Enriched metadata or None
        """
        matches = self.identify(audio_path)
        
        if not matches:
            return None
        
        if auto_select:
            # Return best match (highest score)
            best_match = max(matches, key=lambda x: x['score'])
            logger.info(f"Auto-selected best match: {best_match['title']} (score: {best_match['score']:.2f})")
            return best_match
        
        return matches[0] if matches else None


# Convenience functions
def quick_identify(audio_path: str, api_key: Optional[str] = None) -> List[Dict]:
    """Quick audio identification."""
    client = AcoustIDClient(api_key)
    return client.identify(Path(audio_path))


def quick_duplicates(directory: str, api_key: Optional[str] = None) -> List[Tuple[Path, Path]]:
    """Quick duplicate detection."""
    client = AcoustIDClient(api_key)
    return client.find_duplicates(Path(directory))
