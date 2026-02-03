import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("src"))

from samplemind.services.organizer import OrganizationEngine


async def verify():
    print("🚀 Verifying OrganizationEngine...")

    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        print(f"Created temp dir: {root}")

        # Setup files
        f1 = root / "beat1.wav"
        f1.touch()
        f2 = root / "synth.mp3"
        f2.touch()

        organizer = OrganizationEngine(dry_run=False)

        # Test 1: Simple Move
        metadata = {"genre": "Techno", "bpm": 140, "key": "Dm"}
        res1 = await organizer.organize_file(
            f1, metadata,
            pattern="{genre}/{bpm}/{filename}",
            root_dir=root
        )

        dest1 = root / "Techno/140/beat1.wav"
        assert res1.success
        assert res1.destination == dest1
        assert dest1.exists()
        assert not f1.exists()
        print("✅ Test 1 Passed: Simple Move works")

        # Test 2: Dry Run
        organizer_dry = OrganizationEngine(dry_run=True)
        meta2 = {"genre": "Ambient"}
        res2 = await organizer_dry.organize_file(
            f2, meta2,
            pattern="{genre}/{filename}",
            root_dir=root
        )
        dest2 = root / "Ambient/synth.mp3"
        assert res2.success
        assert res2.destination == dest2
        assert not dest2.exists()
        assert f2.exists()
        print("✅ Test 2 Passed: Dry Run works")

        # Test 3: Collision
        # Create a file where we want to put f2
        real_dest_dir = root / "Ambient"
        real_dest_dir.mkdir(parents=True, exist_ok=True)
        (real_dest_dir / "synth.mp3").touch()

        res3 = await organizer.organize_file(
            f2, meta2,
            pattern="{genre}/{filename}",
            root_dir=root
        )
        assert res3.success
        assert res3.destination.name == "synth_1.mp3"
        assert (real_dest_dir / "synth_1.mp3").exists()
        print("✅ Test 3 Passed: Collision Handling works")

    print("\n🎉 All Verification Tests Passed!")

if __name__ == "__main__":
    asyncio.run(verify())
