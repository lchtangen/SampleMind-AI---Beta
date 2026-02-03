import sys
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from samplemind.core.library.pack_creator import (
    PackMetadata,
    PackTemplate,
    SampleInfo,
    SamplePack,
    SamplePackCreator,
)


class TestPackCreator:
    @pytest.fixture
    def mock_path_cls(self):
        """Mock the Path class imported in pack_creator"""
        with patch("samplemind.core.library.pack_creator.Path") as mock:
            yield mock

    @pytest.fixture
    def mock_shutil(self):
        with patch("samplemind.core.library.pack_creator.shutil") as mock:
            yield mock

    def test_pack_metadata(self):
        metadata = PackMetadata(
            name="Test Pack",
            author="Test Author",
            description="Test Description"
        )
        assert metadata.name == "Test Pack"
        assert metadata.author == "Test Author"
        assert metadata.version == "1.0.0"

        data = metadata.to_dict()
        assert data["name"] == "Test Pack"
        assert "created_date" in data

    def test_create_pack_structure(self, mock_path_cls):
        # Setup the mock Path behavior
        # When Path.cwd() is called
        mock_cwd = MagicMock()
        mock_path_cls.cwd.return_value = mock_cwd

        # When output_dir / name is called
        mock_pack_dir = MagicMock()
        # Mock the / operator chain: cwd / "packs" / "name"
        # We need to be careful with how the code does it:
        # output_dir = Path.cwd() / "packs"
        # pack_dir = output_dir / name...

        mock_packs_dir = MagicMock()
        mock_cwd.__truediv__.return_value = mock_packs_dir
        mock_packs_dir.__truediv__.return_value = mock_pack_dir

        # Also need Path(output_dir) if output_dir is passed? No, code uses Path.cwd().

        creator = SamplePackCreator()
        pack = creator.create_pack(
            name="Drum Pack",
            template=PackTemplate.DRUMS,
            author="Tester"
        )

        assert pack.name == "Drum Pack"
        assert pack.template == PackTemplate.DRUMS

        # Check if mkdir was called on the final pack directory
        assert mock_pack_dir.mkdir.called

        # Check subfolders
        # The loop does folder_path = self.pack_dir / folder
        # So pack_dir / "kicks" should be called
        assert mock_pack_dir.__truediv__.call_count >= 5

    def test_analyze_sample(self):
        # Mock librosa and soundfile using sys.modules because they are imported inside the function
        mock_librosa = MagicMock()
        mock_sf = MagicMock()

        # Setup return values
        mock_sf.info.return_value.samplerate = 44100
        mock_sf.info.return_value.channels = 2
        mock_sf_info_subtype = MagicMock()
        # Mock string split for subtype
        mock_sf.info.return_value.subtype_info = "PCM_24"

        mock_audio = np.zeros((2, 88200)) # 2 sec stereo
        mock_librosa.load.return_value = (mock_audio, 44100)
        mock_librosa.onset.onset_strength.return_value = np.zeros(100)
        mock_librosa.feature.tempo.return_value = [120.0]

        with patch.dict(sys.modules, {'librosa': mock_librosa, 'soundfile': mock_sf}):
            # Setup dummy SamplePack
            pack_dir = MagicMock()
            pack = SamplePack("Test", pack_dir, PackTemplate.CUSTOM, MagicMock())

            file_path = MagicMock()
            file_path.name = "test.wav"
            file_path.__str__.return_value = "test.wav"
            file_path.stat.return_value.st_size = 1024 * 1024

            info = pack._analyze_sample(file_path)

            assert info.filename == "test.wav"
            assert info.duration_seconds == 2.0
            assert info.sample_rate == 44100
            assert info.bpm == 120.0

    def test_add_sample_success(self, mock_path_cls, mock_shutil):
        # Setup SamplePack
        pack_dir = MagicMock()
        pack = SamplePack("Test", pack_dir, PackTemplate.CUSTOM, MagicMock())

        # Turn off real analysis
        pack._analyze_sample = Mock()
        pack._analyze_sample.return_value = SampleInfo(
            filename="test.wav", duration_seconds=1.0,
            sample_rate=44100, bit_depth=16, channels=2
        )

        # The code calls file_path = Path(file_path)
        # So we need mock_path_cls to return a mock when verified
        # Or simpler: pass a string and let mock_path_cls(string) return a mock

        mock_file_path_obj = MagicMock()
        mock_file_path_obj.exists.return_value = True
        mock_file_path_obj.name = "test.wav"

        # When Path("some/path") is called, return our mock object
        mock_path_cls.return_value = mock_file_path_obj

        # But wait, constructor is called.

        success = pack.add_sample("path/to/test.wav")

        assert success is True
        assert len(pack.samples) == 1
        assert "test.wav" in pack.samples
        assert mock_shutil.copy2.called

    def test_add_samples_from_folder(self, mock_path_cls, mock_shutil):
        # Setup SamplePack
        pack_dir = MagicMock()
        pack = SamplePack("Test", pack_dir, PackTemplate.CUSTOM, MagicMock())
        pack._analyze_sample = Mock()
        pack._analyze_sample.return_value = SampleInfo(
            filename="kick.wav", duration_seconds=1.0,
            sample_rate=44100, bit_depth=16, channels=2
        )

        # Setup source folder mock
        mock_source_obj = MagicMock()
        mock_source_obj.exists.return_value = True

        # Files found in glob
        file1 = MagicMock(); file1.name = "kick.wav"
        file2 = MagicMock(); file2.name = "snare.wav"

        # glob side effects for different extensions
        mock_source_obj.glob.side_effect = [[file1, file2], [], [], [], []]

        # When Path(source_folder) is called
        mock_path_cls.return_value = mock_source_obj

        count = pack.add_samples_from_folder("source_dir")

        assert count == 2
        assert len(pack.samples) == 2
