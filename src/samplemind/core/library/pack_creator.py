"""
Sample Pack Creator (Phase 13.4)

Professional sample pack organization and distribution:
- Pack structure and metadata
- Template systems (drums, melodic, effects, loops)
- Batch sample organization
- Pack distribution and sharing
"""

import json
import logging
import shutil
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PackTemplate(str, Enum):
    """Sample pack templates"""
    DRUMS = "drums"           # Kick, snare, hihat, percussion, fills
    MELODIC = "melodic"       # Synths, instruments, leads, pads
    EFFECTS = "effects"       # FX, transitions, impacts, transitions
    LOOPS = "loops"            # One-shots, loops, grooves, rhythms
    CUSTOM = "custom"         # User-defined template


@dataclass
class PackMetadata:
    """Sample pack metadata"""
    name: str                          # Pack name
    version: str = "1.0.0"             # Semantic versioning
    author: str = "Unknown"            # Pack creator name
    description: str = ""              # Pack description
    genre: str = ""                    # Primary genre
    bpm: Optional[float] = None        # Suggested tempo
    key: Optional[str] = None          # Musical key
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_date: str = field(default_factory=lambda: datetime.now().isoformat())
    sample_count: int = 0              # Number of samples
    total_size_mb: float = 0.0         # Total pack size
    license: str = "Creative Commons"  # License type
    tags: List[str] = field(default_factory=list)
    cover_art: Optional[Path] = None   # Cover image path

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        if self.cover_art:
            data['cover_art'] = str(self.cover_art)
        return data

    def save_json(self, output_path: Path) -> None:
        """Save metadata as JSON"""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Saved pack metadata to {output_path}")


@dataclass
class SampleInfo:
    """Information about a single sample"""
    filename: str
    duration_seconds: float
    sample_rate: int
    bit_depth: int
    channels: int
    bpm: Optional[float] = None
    key: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: str = ""
    file_size_mb: float = 0.0


class SamplePackCreator:
    """
    Create and manage professional sample packs.

    Example:
        creator = SamplePackCreator()
        pack = creator.create_pack(
            name="Techno Essentials",
            template=PackTemplate.DRUMS,
            author="Producer Name"
        )
        pack.add_samples_from_folder(Path("./drum_samples"))
        pack.export(Path("./output"), format="zip")
    """

    # Pack template structure definitions
    TEMPLATE_STRUCTURE = {
        PackTemplate.DRUMS: {
            "folders": ["kicks", "snares", "hihats", "percussion", "fills"],
            "description": "Drum and percussion samples"
        },
        PackTemplate.MELODIC: {
            "folders": ["synths", "strings", "leads", "pads", "basses"],
            "description": "Melodic and harmonic samples"
        },
        PackTemplate.EFFECTS: {
            "folders": ["transitions", "impacts", "risers", "drops", "fills"],
            "description": "Sound effects and transitions"
        },
        PackTemplate.LOOPS: {
            "folders": ["drums", "music", "bass", "melody", "grooves"],
            "description": "Loops and grooves"
        },
        PackTemplate.CUSTOM: {
            "folders": [],
            "description": "Custom pack structure"
        }
    }

    def __init__(self):
        """Initialize pack creator"""
        logger.info("Sample Pack Creator initialized")

    def create_pack(
        self,
        name: str,
        template: PackTemplate = PackTemplate.CUSTOM,
        author: str = "Unknown",
        description: str = "",
        output_dir: Optional[Path] = None,
    ) -> "SamplePack":
        """
        Create a new sample pack.

        Args:
            name: Pack name
            template: Pack template structure
            author: Pack author/creator name
            description: Pack description
            output_dir: Base output directory

        Returns:
            SamplePack object
        """
        if output_dir is None:
            output_dir = Path.cwd() / "packs"

        pack_dir = output_dir / name.replace(" ", "_").lower()
        pack_dir.mkdir(parents=True, exist_ok=True)

        # Create metadata
        metadata = PackMetadata(
            name=name,
            author=author,
            description=description,
            version="1.0.0"
        )

        # Create pack
        pack = SamplePack(
            name=name,
            pack_dir=pack_dir,
            template=template,
            metadata=metadata
        )

        # Create folder structure
        pack.create_structure()

        logger.info(f"Created pack: {name} (template: {template.value})")
        return pack

    def create_from_folder(
        self,
        name: str,
        source_folder: Path,
        template: PackTemplate = PackTemplate.CUSTOM,
        author: str = "Unknown",
        output_dir: Optional[Path] = None,
    ) -> "SamplePack":
        """
        Create pack from existing folder structure.

        Args:
            name: Pack name
            source_folder: Folder with samples
            template: Pack template
            author: Pack author
            output_dir: Base output directory

        Returns:
            SamplePack with samples from folder
        """
        # Create empty pack
        pack = self.create_pack(name, template, author, output_dir=output_dir)

        # Add samples from folder
        pack.add_samples_from_folder(source_folder)

        return pack


class SamplePack:
    """
    Represents a single sample pack.
    """

    def __init__(
        self,
        name: str,
        pack_dir: Path,
        template: PackTemplate,
        metadata: PackMetadata,
    ):
        """Initialize sample pack"""
        self.name = name
        self.pack_dir = pack_dir
        self.template = template
        self.metadata = metadata
        self.samples: Dict[str, SampleInfo] = {}

        self.pack_dir.mkdir(parents=True, exist_ok=True)

    def create_structure(self) -> None:
        """Create folder structure for template"""
        template_config = SamplePackCreator.TEMPLATE_STRUCTURE[self.template]

        for folder in template_config["folders"]:
            folder_path = self.pack_dir / folder
            folder_path.mkdir(exist_ok=True)
            logger.info(f"Created folder: {folder_path}")

    def add_samples_from_folder(
        self,
        source_folder: Path,
        organize_by_type: bool = True,
    ) -> int:
        """
        Add samples from a folder to the pack.

        Args:
            source_folder: Folder containing audio files
            organize_by_type: Organize samples by template folders

        Returns:
            Number of samples added
        """
        source_folder = Path(source_folder)
        if not source_folder.exists():
            logger.warning(f"Source folder not found: {source_folder}")
            return 0

        # Find all audio files
        audio_extensions = [".wav", ".mp3", ".flac", ".m4a", ".aiff"]
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(source_folder.glob(f"**/*{ext}"))

        if not audio_files:
            logger.warning(f"No audio files found in {source_folder}")
            return 0

        added_count = 0
        for audio_file in audio_files:
            try:
                # Get sample info
                sample_info = self._analyze_sample(audio_file)

                # Determine destination folder
                if organize_by_type and self.template != PackTemplate.CUSTOM:
                    dest_folder = self._categorize_sample(audio_file, sample_info)
                else:
                    dest_folder = self.pack_dir

                # Copy file
                dest_path = dest_folder / audio_file.name
                shutil.copy2(audio_file, dest_path)

                # Store sample info
                self.samples[audio_file.name] = sample_info
                added_count += 1
                logger.info(f"Added sample: {audio_file.name}")

            except Exception as e:
                logger.error(f"Failed to add sample {audio_file.name}: {e}")

        # Update metadata
        self.metadata.sample_count = len(self.samples)
        self._calculate_total_size()

        logger.info(f"Added {added_count} samples to pack")
        return added_count

    def add_sample(
        self,
        file_path: Path,
        destination_folder: Optional[str] = None,
    ) -> bool:
        """
        Add a single sample to the pack.

        Args:
            file_path: Path to audio file
            destination_folder: Destination folder within pack (optional)

        Returns:
            True if successful
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"Sample file not found: {file_path}")
            return False

        try:
            # Get sample info
            sample_info = self._analyze_sample(file_path)

            # Determine destination
            if destination_folder:
                dest_dir = self.pack_dir / destination_folder
            else:
                dest_dir = self.pack_dir

            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / file_path.name

            # Copy file
            shutil.copy2(file_path, dest_path)

            # Store info
            self.samples[file_path.name] = sample_info
            self.metadata.sample_count = len(self.samples)
            self._calculate_total_size()

            logger.info(f"Added sample: {file_path.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add sample: {e}")
            return False

    def _analyze_sample(self, file_path: Path) -> SampleInfo:
        """Analyze audio sample to extract info"""
        try:
            import librosa
            import soundfile as sf

            # Load audio file info
            info = sf.info(str(file_path))
            audio, sr = librosa.load(str(file_path), sr=None, mono=False)

            # Get duration
            duration = len(audio) / sr if audio.ndim == 1 else audio.shape[1] / sr

            # Get sample info
            sample_info = SampleInfo(
                filename=file_path.name,
                duration_seconds=duration,
                sample_rate=info.samplerate,
                bit_depth=info.subtype_info.split("_")[-1] if "_" in info.subtype_info else "16",
                channels=info.channels,
                file_size_mb=file_path.stat().st_size / (1024 * 1024)
            )

            # Try to extract tempo using librosa
            try:
                onset_env = librosa.onset.onset_strength(y=audio if audio.ndim == 1 else audio[0],
                                                        sr=sr)
                tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0]
                sample_info.bpm = tempo
            except:
                pass

            return sample_info

        except Exception as e:
            logger.warning(f"Could not analyze sample {file_path.name}: {e}")
            # Return minimal info
            return SampleInfo(
                filename=file_path.name,
                duration_seconds=0.0,
                sample_rate=44100,
                bit_depth=16,
                channels=2,
                file_size_mb=file_path.stat().st_size / (1024 * 1024)
            )

    def _categorize_sample(self, file_path: Path, sample_info: SampleInfo) -> Path:
        """Categorize sample to appropriate folder"""
        filename_lower = file_path.name.lower()

        # Simple heuristic-based categorization
        if self.template == PackTemplate.DRUMS:
            if "kick" in filename_lower or "bass drum" in filename_lower:
                return self.pack_dir / "kicks"
            elif "snare" in filename_lower:
                return self.pack_dir / "snares"
            elif "hihat" in filename_lower or "hat" in filename_lower:
                return self.pack_dir / "hihats"
            elif "perc" in filename_lower or "tom" in filename_lower:
                return self.pack_dir / "percussion"
            elif "fill" in filename_lower:
                return self.pack_dir / "fills"

        elif self.template == PackTemplate.MELODIC:
            if "synth" in filename_lower or "pad" in filename_lower:
                return self.pack_dir / "pads"
            elif "lead" in filename_lower:
                return self.pack_dir / "leads"
            elif "bass" in filename_lower:
                return self.pack_dir / "basses"
            elif "string" in filename_lower:
                return self.pack_dir / "strings"

        elif self.template == PackTemplate.EFFECTS:
            if "transition" in filename_lower or "trans" in filename_lower:
                return self.pack_dir / "transitions"
            elif "impact" in filename_lower or "hit" in filename_lower:
                return self.pack_dir / "impacts"
            elif "rise" in filename_lower:
                return self.pack_dir / "risers"
            elif "drop" in filename_lower:
                return self.pack_dir / "drops"

        # Default to main pack directory
        return self.pack_dir

    def _calculate_total_size(self) -> None:
        """Calculate total pack size"""
        total_size = 0
        for root, dirs, files in self.pack_dir.walk():
            for file in files:
                file_path = Path(root) / file
                total_size += file_path.stat().st_size

        self.metadata.total_size_mb = total_size / (1024 * 1024)

    def save_metadata(self) -> None:
        """Save pack metadata as JSON"""
        metadata_path = self.pack_dir / "pack.json"
        self.metadata.updated_date = datetime.now().isoformat()
        self.metadata.save_json(metadata_path)

    def export(
        self,
        output_path: Path,
        format: str = "zip",
        include_metadata: bool = True,
    ) -> Path:
        """
        Export pack to file.

        Args:
            output_path: Output directory
            format: Export format (zip, tar, dir)
            include_metadata: Include metadata JSON

        Returns:
            Path to exported pack
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save metadata
        if include_metadata:
            self.save_metadata()

        if format == "zip":
            return self._export_zip(output_path)
        elif format == "tar":
            return self._export_tar(output_path)
        elif format == "dir":
            return self._export_dir(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_zip(self, output_dir: Path) -> Path:
        """Export pack as ZIP"""
        output_file = output_dir / f"{self.name.replace(' ', '_')}.zip"

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.pack_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.pack_dir.parent)
                    zf.write(file_path, arcname)

        logger.info(f"Exported pack to ZIP: {output_file}")
        logger.info(f"Pack size: {output_file.stat().st_size / (1024 * 1024):.1f} MB")
        return output_file

    def _export_tar(self, output_dir: Path) -> Path:
        """Export pack as TAR.GZ"""
        import tarfile

        output_file = output_dir / f"{self.name.replace(' ', '_')}.tar.gz"

        with tarfile.open(output_file, 'w:gz') as tf:
            tf.add(self.pack_dir, arcname=self.pack_dir.name)

        logger.info(f"Exported pack to TAR.GZ: {output_file}")
        logger.info(f"Pack size: {output_file.stat().st_size / (1024 * 1024):.1f} MB")
        return output_file

    def _export_dir(self, output_dir: Path) -> Path:
        """Export pack as directory"""
        dest_dir = output_dir / self.name.replace(" ", "_")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        shutil.copytree(self.pack_dir, dest_dir)

        logger.info(f"Exported pack to directory: {dest_dir}")
        return dest_dir

    def get_summary(self) -> Dict:
        """Get pack summary"""
        return {
            "name": self.name,
            "template": self.template.value,
            "sample_count": self.metadata.sample_count,
            "total_size_mb": self.metadata.total_size_mb,
            "author": self.metadata.author,
            "version": self.metadata.version,
            "created": self.metadata.created_date,
            "pack_path": str(self.pack_dir)
        }


__all__ = [
    "SamplePackCreator",
    "SamplePack",
    "PackTemplate",
    "PackMetadata",
    "SampleInfo",
]
