#!/usr/bin/env python3
"""
Quick test for file picker - Beta Release
Tests the fixed file picker with no multiple dialog issues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from samplemind.utils import select_file_or_folder, select_audio_file, select_directory

def main():
    print("🎵 SampleMind AI - File Picker Beta Test")
    print("=" * 60)
    print("This test will open modern Ubuntu dialogs (Zenity)")
    print("No multiple windows will appear!")
    print("=" * 60)

    print("\n📁 Test 1: File or Folder Choice")
    print("   This will open 2 dialogs:")
    print("   1. A choice dialog (file vs folder)")
    print("   2. The appropriate file/folder picker")
    print()

    result = select_file_or_folder()
    if result:
        print(f"✅ Selected: {result}")
        print(f"   Type: {'File' if result.is_file() else 'Folder'}")
        print(f"   Exists: {'Yes' if result.exists() else 'No'}")
    else:
        print("❌ Cancelled or no selection")

    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("Ready for beta release if no multiple windows appeared.")

if __name__ == "__main__":
    main()
