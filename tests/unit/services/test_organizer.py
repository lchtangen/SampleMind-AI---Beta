import shutil
from pathlib import Path

import pytest

from samplemind.services.organizer import OrganizationEngine


@pytest.fixture
def temp_library(tmp_path):
    # Create some dummy files
    files = ["beat.wav", "synths.mp3", "vocal.wav"]
    for f in files:
        (tmp_path / f).touch()
    return tmp_path

@pytest.mark.asyncio
async def test_organize_file_dry_run(temp_library):
    organizer = OrganizationEngine(dry_run=True)
    file_path = temp_library / "beat.wav"
    metadata = {"genre": "Techno", "bpm": 130, "key": "Cm"}

    result = await organizer.organize_file(
        file_path,
        metadata,
        pattern="{genre}/{bpm}/{filename}",
        root_dir=temp_library
    )

    assert result.success
    assert result.destination == temp_library / "Techno/130/beat.wav"
    assert file_path.exists() # Should still exist in source
    assert not result.destination.exists() # Should NOT exist in dest (dry run)

@pytest.mark.asyncio
async def test_organize_file_move(temp_library):
    organizer = OrganizationEngine(dry_run=False)
    file_path = temp_library / "synths.mp3"
    metadata = {"genre": "Ambient", "bpm": 90}

    result = await organizer.organize_file(
        file_path,
        metadata,
        pattern="{genre}/{bpm}/{filename}",
        root_dir=temp_library
    )

    assert result.success
    assert result.destination == temp_library / "Ambient/90/synths.mp3"
    assert not file_path.exists() # Should move
    assert result.destination.exists()

@pytest.mark.asyncio
async def test_collision_handling(temp_library):
    organizer = OrganizationEngine(dry_run=False)

    # Create a file that will collide
    dest_dir = temp_library / "Techno"
    dest_dir.mkdir()
    (dest_dir / "beat.wav").touch() # Existing file

    file_path = temp_library / "beat.wav"
    metadata = {"genre": "Techno"}

    result = await organizer.organize_file(
        file_path,
        metadata,
        pattern="{genre}/{filename}",
        root_dir=temp_library
    )

    assert result.success
    assert result.destination.name == "beat_1.wav"
    assert (dest_dir / "beat_1.wav").exists()
