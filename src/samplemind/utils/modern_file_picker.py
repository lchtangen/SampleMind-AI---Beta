#!/usr/bin/env python3
"""
Modern File Picker for SampleMind AI
Clean, single-dialog file/folder selection for Ubuntu and other Linux systems
Uses only modern native dialogs (Zenity, Portal)
"""

import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, List, Literal
import logging

logger = logging.getLogger(__name__)


class ModernFilePicker:
    """
    Modern file picker using Zenity (Ubuntu/GNOME native file chooser)
    Only opens ONE dialog at a time, never multiple
    """

    def __init__(self) -> None:
        self.os_type = platform.system().lower()
        self._has_zenity = shutil.which('zenity') is not None

    def select(
        self,
        mode: Literal['file', 'folder', 'audio'] = 'file',
        title: str = "Select",
        initial_directory: Optional[Path] = None,
        multiple: bool = False
    ) -> Optional[Path] | List[Path]:
        """
        Universal file/folder selector with choice

        Args:
            mode: 'file' for any file, 'folder' for directory, 'audio' for audio files
            title: Dialog title
            initial_directory: Starting directory
            multiple: Allow multiple file selection

        Returns:
            Selected path(s) or None if cancelled
        """
        # Ask user what they want to select if not specified
        if mode == 'file':
            actual_mode = self._ask_file_or_folder()
            if not actual_mode:
                return None
        else:
            actual_mode = mode

        # Use appropriate selection method
        if actual_mode == 'folder':
            return self._select_folder(title, initial_directory)
        elif actual_mode == 'audio':
            return self._select_audio_file(title, initial_directory, multiple)
        else:  # 'file'
            return self._select_file(title, initial_directory, multiple)

    def _ask_file_or_folder(self) -> Optional[Literal['file', 'folder']]:
        """Ask user whether they want to select a file or folder"""
        if not self._has_zenity:
            choice = input("Select [F]ile or [D]irectory? (f/d): ").strip().lower()
            return 'file' if choice == 'f' else 'folder' if choice == 'd' else None

        try:
            result = subprocess.run(
                [
                    'zenity', '--list',
                    '--title=What would you like to select?',
                    '--text=Choose selection type:',
                    '--column=Type', '--column=Description',
                    'file', 'Select a file',
                    'folder', 'Select a folder/directory',
                    '--hide-column=1',
                    '--width=400',
                    '--height=200'
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and result.stdout.strip():
                choice = result.stdout.strip().lower()
                return 'file' if 'file' in choice else 'folder'

        except Exception as e:
            logger.error(f"Selection dialog failed: {e}")

        return None

    def _select_file(
        self,
        title: str = "Select File",
        initial_directory: Optional[Path] = None,
        multiple: bool = False
    ) -> Optional[Path] | List[Path]:
        """Select one or more files using Zenity"""
        if not self._has_zenity:
            return self._fallback_input_file(title)

        cmd = ['zenity', '--file-selection', f'--title={title}']

        if multiple:
            cmd.append('--multiple')
            cmd.append('--separator=\n')

        if initial_directory and initial_directory.exists():
            cmd.append(f'--filename={initial_directory}/')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and result.stdout.strip():
                if multiple:
                    paths = [Path(p.strip()) for p in result.stdout.strip().split('\n') if p.strip()]
                    return paths if paths else None
                else:
                    return Path(result.stdout.strip())

        except Exception as e:
            logger.error(f"Zenity file selection failed: {e}")

        return None

    def _select_folder(
        self,
        title: str = "Select Folder",
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Select a folder using Zenity"""
        if not self._has_zenity:
            return self._fallback_input_folder(title)

        cmd = ['zenity', '--file-selection', '--directory', f'--title={title}']

        if initial_directory and initial_directory.exists():
            cmd.append(f'--filename={initial_directory}/')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())

        except Exception as e:
            logger.error(f"Zenity folder selection failed: {e}")

        return None

    def _select_audio_file(
        self,
        title: str = "Select Audio File",
        initial_directory: Optional[Path] = None,
        multiple: bool = False
    ) -> Optional[Path] | List[Path]:
        """Select audio file(s) with file type filter"""
        if not self._has_zenity:
            return self._fallback_input_file(title)

        cmd = ['zenity', '--file-selection', f'--title={title}']

        # Add audio file filter
        audio_filter = 'Audio Files|*.wav *.mp3 *.flac *.aiff *.aif *.m4a *.ogg *.wma *.opus'
        cmd.append(f'--file-filter={audio_filter}')
        cmd.append('--file-filter=All Files|*')

        if multiple:
            cmd.append('--multiple')
            cmd.append('--separator=\n')

        if initial_directory and initial_directory.exists():
            cmd.append(f'--filename={initial_directory}/')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and result.stdout.strip():
                if multiple:
                    paths = [Path(p.strip()) for p in result.stdout.strip().split('\n') if p.strip()]
                    return paths if paths else None
                else:
                    return Path(result.stdout.strip())

        except Exception as e:
            logger.error(f"Zenity audio file selection failed: {e}")

        return None

    def _fallback_input_file(self, prompt: str) -> Optional[Path]:
        """Text input fallback if Zenity not available"""
        try:
            path_str = input(f"{prompt} - Enter file path: ").strip()
            if path_str:
                path = Path(path_str).expanduser()
                if path.exists() and path.is_file():
                    return path
                else:
                    print(f"❌ File not found: {path}")
        except (KeyboardInterrupt, EOFError):
            pass
        return None

    def _fallback_input_folder(self, prompt: str) -> Optional[Path]:
        """Text input fallback for folders"""
        try:
            path_str = input(f"{prompt} - Enter folder path: ").strip()
            if path_str:
                path = Path(path_str).expanduser()
                if path.exists() and path.is_dir():
                    return path
                else:
                    print(f"❌ Folder not found: {path}")
        except (KeyboardInterrupt, EOFError):
            pass
        return None


# Global singleton instance
_picker_instance = None


def get_picker() -> ModernFilePicker:
    """Get global file picker instance (singleton pattern)"""
    global _picker_instance
    if _picker_instance is None:
        _picker_instance = ModernFilePicker()
    return _picker_instance


# Convenience functions for easy use
def select_file_or_folder(title: str = "Select") -> Optional[Path]:
    """
    Let user choose between file or folder, then select it
    Opens ONE dialog that asks first, then another to select
    """
    picker = get_picker()
    return picker.select(mode='file', title=title)


def select_file(title: str = "Select File", multiple: bool = False) -> Optional[Path] | List[Path]:
    """Select a file (or multiple files)"""
    picker = get_picker()
    return picker._select_file(title, multiple=multiple)


def select_folder(title: str = "Select Folder") -> Optional[Path]:
    """Select a folder/directory"""
    picker = get_picker()
    return picker._select_folder(title)


def select_audio_file(title: str = "Select Audio File", multiple: bool = False) -> Optional[Path] | List[Path]:
    """Select audio file(s) with type filtering"""
    picker = get_picker()
    return picker._select_audio_file(title, multiple=multiple)


def select_audio_files(title: str = "Select Audio Files") -> List[Path]:
    """Select multiple audio files"""
    result = select_audio_file(title, multiple=True)
    if isinstance(result, list):
        return result
    elif result:
        return [result]
    else:
        return []


# Demo/Test
if __name__ == "__main__":
    print("🎵 Modern File Picker Test")
    print("=" * 60)

    picker = ModernFilePicker()
    print(f"OS: {picker.os_type}")
    print(f"Zenity available: {'✅' if picker._has_zenity else '❌'}")
    print("=" * 60)

    print("\n1. Testing file/folder choice...")
    selection = select_file_or_folder("Choose what to select")
    if selection:
        print(f"✅ Selected: {selection}")
        print(f"   Type: {'File' if selection.is_file() else 'Folder'}")
    else:
        print("❌ No selection")

    print("\n2. Testing audio file selection...")
    audio_file = select_audio_file("Choose an audio file")
    if audio_file:
        print(f"✅ Selected: {audio_file}")
    else:
        print("❌ No selection")

    print("\n3. Testing folder selection...")
    folder = select_folder("Choose a folder")
    if folder:
        print(f"✅ Selected: {folder}")
    else:
        print("❌ No selection")

    print("\n✅ Test complete!")
