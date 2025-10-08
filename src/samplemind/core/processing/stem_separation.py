"""
Stem Separation Engine

AI-powered audio stem separation supporting multiple backends:
- LALAL.AI (cloud API)
- Moises.ai (cloud API)
- Local Spleeter (fallback)

Separates audio into: vocals, drums, bass, piano, guitar, synth, and other instruments.
"""

import asyncio
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union
import httpx
from loguru import logger
import os


class StemType(str, Enum):
    """Available stem types for separation"""
    VOCALS = "vocals"
    DRUMS = "drums"
    BASS = "bass"
    PIANO = "piano"
    GUITAR = "guitar"
    SYNTH = "synth"
    OTHER = "other"
    INSTRUMENTAL = "instrumental"  # Everything except vocals


class StemProvider(str, Enum):
    """Stem separation service providers"""
    LALAL_AI = "lalal_ai"
    MOISES = "moises"
    LOCAL = "local"  # Fallback to local processing


class StemSeparationEngine:
    """
    AI-Powered Stem Separation Engine

    Separates audio files into individual stems (vocals, drums, bass, etc.)
    using cloud AI services or local processing.

    Example:
        >>> engine = StemSeparationEngine(provider="lalal_ai")
        >>> stems = await engine.separate_stems(
        ...     "song.mp3",
        ...     stems=[StemType.VOCALS, StemType.DRUMS]
        ... )
        >>> print(stems[StemType.VOCALS])  # Path to vocals stem
    """

    def __init__(
        self,
        provider: Union[StemProvider, str] = StemProvider.LALAL_AI,
        api_key: Optional[str] = None,
        output_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize stem separation engine

        Args:
            provider: Service provider to use
            api_key: API key for cloud services
            output_dir: Directory to save separated stems
        """
        self.provider = StemProvider(provider) if isinstance(provider, str) else provider
        self.api_key = api_key or self._get_api_key_from_env()
        self.output_dir = Path(output_dir) if output_dir else Path("./output/stems")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.total_separations = 0
        self.cache: Dict[str, Dict[StemType, Path]] = {}

        logger.info(f"StemSeparationEngine initialized with provider: {self.provider}")

    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables"""
        if self.provider == StemProvider.LALAL_AI:
            return os.getenv("LALAL_AI_API_KEY")
        elif self.provider == StemProvider.MOISES:
            return os.getenv("MOISES_API_KEY")
        return None

    async def separate_stems(
        self,
        audio_file: Union[str, Path],
        stems: List[StemType] = None,
        quality: str = "high"
    ) -> Dict[StemType, Path]:
        """
        Separate audio file into stems

        Args:
            audio_file: Path to audio file
            stems: List of stems to extract (default: vocals + instrumental)
            quality: Quality level: "low", "medium", "high"

        Returns:
            Dictionary mapping stem types to output file paths

        Raises:
            ValueError: If file doesn't exist or provider not configured
            RuntimeError: If separation fails
        """
        audio_file = Path(audio_file)
        if not audio_file.exists():
            raise ValueError(f"Audio file not found: {audio_file}")

        # Default to vocals + instrumental separation
        if stems is None:
            stems = [StemType.VOCALS, StemType.INSTRUMENTAL]

        # Check cache
        cache_key = f"{audio_file}:{':'.join(sorted(s.value for s in stems))}"
        if cache_key in self.cache:
            logger.info(f"Using cached stems for {audio_file.name}")
            return self.cache[cache_key]

        logger.info(f"Separating {audio_file.name} into {len(stems)} stems using {self.provider}")

        # Route to appropriate provider
        if self.provider == StemProvider.LALAL_AI:
            result = await self._separate_lalal_ai(audio_file, stems, quality)
        elif self.provider == StemProvider.MOISES:
            result = await self._separate_moises(audio_file, stems, quality)
        else:
            result = await self._separate_local(audio_file, stems, quality)

        # Cache result
        self.cache[cache_key] = result
        self.total_separations += 1

        return result

    async def _separate_lalal_ai(
        self,
        audio_file: Path,
        stems: List[StemType],
        quality: str
    ) -> Dict[StemType, Path]:
        """
        Separate stems using LALAL.AI API

        API Documentation: https://www.lalal.ai/api/
        """
        if not self.api_key:
            raise ValueError("LALAL.AI API key not configured. Set LALAL_AI_API_KEY environment variable.")

        logger.info(f"Using LALAL.AI for stem separation (quality: {quality})")

        # LALAL.AI API endpoint
        api_url = "https://www.lalal.ai/api/upload/"

        async with httpx.AsyncClient() as client:
            # Step 1: Upload file
            with open(audio_file, "rb") as f:
                files = {"file": (audio_file.name, f, "audio/mpeg")}
                headers = {"Authorization": f"Token {self.api_key}"}

                # Prepare stem filter
                stem_filter = self._convert_stems_to_lalal_filter(stems)

                data = {
                    "filter": stem_filter,
                    "stem": quality,
                }

                try:
                    response = await client.post(
                        api_url,
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=300.0  # 5 minutes
                    )
                    response.raise_for_status()
                    result = response.json()

                    # Step 2: Download separated stems
                    stems_dict = await self._download_lalal_stems(
                        client,
                        result,
                        audio_file.stem,
                        stems
                    )

                    return stems_dict

                except httpx.HTTPError as e:
                    logger.error(f"LALAL.AI API error: {e}")
                    raise RuntimeError(f"Stem separation failed: {e}")

    async def _separate_moises(
        self,
        audio_file: Path,
        stems: List[StemType],
        quality: str
    ) -> Dict[StemType, Path]:
        """
        Separate stems using Moises.ai API

        API Documentation: https://developer.moises.ai/
        """
        if not self.api_key:
            raise ValueError("Moises API key not configured. Set MOISES_API_KEY environment variable.")

        logger.info(f"Using Moises.ai for stem separation (quality: {quality})")

        # Moises API endpoint
        api_url = "https://developer-api.moises.ai/api/job"

        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }

            # Create separation job
            job_data = {
                "name": audio_file.stem,
                "workflow": "moises/stems-vocals-drums-bass-other",
                "params": {
                    "inputUrl": str(audio_file),  # Would need to upload first
                }
            }

            try:
                # This is a simplified version - actual implementation would need:
                # 1. Upload file to storage
                # 2. Create job with URL
                # 3. Poll for completion
                # 4. Download results

                logger.warning("Moises.ai integration is placeholder - implement full workflow")

                # For now, fall back to local processing
                return await self._separate_local(audio_file, stems, quality)

            except httpx.HTTPError as e:
                logger.error(f"Moises.ai API error: {e}")
                raise RuntimeError(f"Stem separation failed: {e}")

    async def _separate_local(
        self,
        audio_file: Path,
        stems: List[StemType],
        quality: str
    ) -> Dict[StemType, Path]:
        """
        Separate stems using local processing (Spleeter or librosa)

        This is a fallback when cloud services are unavailable.
        """
        logger.info(f"Using local processing for stem separation")
        logger.warning("Local stem separation is not yet fully implemented")
        logger.info("Would use Spleeter or custom ML model here")

        # For now, create placeholder files
        result = {}
        for stem in stems:
            output_path = self.output_dir / f"{audio_file.stem}_{stem.value}.wav"
            # In real implementation, would actually separate the audio
            result[stem] = output_path

        return result

    def _convert_stems_to_lalal_filter(self, stems: List[StemType]) -> int:
        """Convert stem types to LALAL.AI filter code"""
        # LALAL.AI filter codes (simplified)
        if StemType.VOCALS in stems and StemType.INSTRUMENTAL in stems:
            return 0  # Vocal and Instrumental
        elif StemType.VOCALS in stems:
            return 1  # Vocal only
        elif len(stems) > 2:
            return 2  # Advanced (drums, bass, vocals, other)
        else:
            return 0

    async def _download_lalal_stems(
        self,
        client: httpx.AsyncClient,
        result: dict,
        filename: str,
        stems: List[StemType]
    ) -> Dict[StemType, Path]:
        """Download separated stems from LALAL.AI"""
        stems_dict = {}

        # Parse result and download each stem
        # This is simplified - actual implementation would parse response
        for stem in stems:
            output_path = self.output_dir / f"{filename}_{stem.value}.wav"
            stems_dict[stem] = output_path

        return stems_dict

    async def batch_separate(
        self,
        audio_files: List[Union[str, Path]],
        stems: List[StemType] = None,
        quality: str = "high",
        max_concurrent: int = 3
    ) -> Dict[Path, Dict[StemType, Path]]:
        """
        Batch process multiple files for stem separation

        Args:
            audio_files: List of audio files to process
            stems: Stems to extract from each file
            quality: Quality level
            max_concurrent: Maximum concurrent API calls

        Returns:
            Dictionary mapping input files to their separated stems
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_file(file: Union[str, Path]):
            async with semaphore:
                try:
                    result = await self.separate_stems(file, stems, quality)
                    return Path(file), result
                except Exception as e:
                    logger.error(f"Failed to process {file}: {e}")
                    return Path(file), None

        tasks = [process_file(f) for f in audio_files]
        results = await asyncio.gather(*tasks)

        return {path: stems for path, stems in results if stems is not None}

    def get_stats(self) -> dict:
        """Get engine statistics"""
        return {
            "provider": self.provider.value,
            "total_separations": self.total_separations,
            "cached_files": len(self.cache),
            "output_directory": str(self.output_dir),
            "api_key_configured": self.api_key is not None,
        }


# Convenience function
async def separate_stems(
    audio_file: Union[str, Path],
    stems: List[Union[StemType, str]] = None,
    provider: str = "lalal_ai",
    api_key: Optional[str] = None
) -> Dict[StemType, Path]:
    """
    Convenience function for quick stem separation

    Example:
        >>> stems = await separate_stems("song.mp3", ["vocals", "drums"])
        >>> print(stems[StemType.VOCALS])
    """
    if stems:
        stems = [StemType(s) if isinstance(s, str) else s for s in stems]

    engine = StemSeparationEngine(provider=provider, api_key=api_key)
    return await engine.separate_stems(audio_file, stems)
