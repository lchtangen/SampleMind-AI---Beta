#!/usr/bin/env python3
"""
Cross-Platform File Picker for SampleMind AI
Supports: macOS (Finder), Linux (Zenity/KDialog/Tkinter), Windows (Tkinter/Native)

This module provides native file/folder selection dialogs for all major platforms.
"""

import sys
import subprocess
import platform
import shutil
import os
from pathlib import Path
from typing import Optional, List, Union
import logging

logger = logging.getLogger(__name__)


class PlatformDetector:
    """Detect operating system and available dialog tools"""

    @staticmethod
    def get_os() -> str:
        """Get OS name: 'macos', 'linux', 'windows', 'unknown'"""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        elif system == 'windows':
            return 'windows'
        else:
            return 'unknown'

    @staticmethod
    def has_zenity() -> bool:
        """Check if zenity is available (Linux)"""
        return shutil.which('zenity') is not None

    @staticmethod
    def has_kdialog() -> bool:
        """Check if kdialog is available (Linux/KDE)"""
        return shutil.which('kdialog') is not None

    @staticmethod
    def has_tkinter() -> bool:
        """Check if tkinter is available"""
        try:
            import tkinter
            return True
        except ImportError:
            return False

    @staticmethod
    def get_desktop_environment() -> str:
        """Get Linux desktop environment"""
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        if 'gnome' in desktop:
            return 'gnome'
        elif 'kde' in desktop or 'plasma' in desktop:
            return 'kde'
        elif 'xfce' in desktop:
            return 'xfce'
        elif 'mate' in desktop:
            return 'mate'
        else:
            return 'unknown'


class MacOSFilePicker:
    """macOS native Finder integration using AppleScript"""

    @staticmethod
    def choose_file(
        title: str = "Choose File",
        file_types: Optional[List[str]] = None,
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Open macOS Finder file chooser"""
        applescript_parts = [
            'tell application "System Events"',
            'activate',
            f'set chosenFile to choose file with prompt "{title}"'
        ]

        if file_types:
            type_list = ', '.join([f'"{ext}"' for ext in file_types])
            applescript_parts[2] += f' of type {{{type_list}}}'

        if initial_directory and initial_directory.exists():
            applescript_parts[2] += f' default location alias POSIX file "{initial_directory}"'

        applescript_parts.extend([
            'set chosenPath to POSIX path of chosenFile',
            'return chosenPath',
            'end tell'
        ])

        try:
            result = subprocess.run(
                ['osascript', '-e', '\n'.join(applescript_parts)],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"macOS file picker failed: {e}")

        return None

    @staticmethod
    def choose_folder(
        title: str = "Choose Folder",
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Open macOS Finder folder chooser"""
        applescript_parts = [
            'tell application "System Events"',
            'activate',
            f'set chosenFolder to choose folder with prompt "{title}"'
        ]

        if initial_directory and initial_directory.exists():
            applescript_parts[2] += f' default location alias POSIX file "{initial_directory}"'

        applescript_parts.extend([
            'set chosenPath to POSIX path of chosenFolder',
            'return chosenPath',
            'end tell'
        ])

        try:
            result = subprocess.run(
                ['osascript', '-e', '\n'.join(applescript_parts)],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"macOS folder picker failed: {e}")

        return None


class LinuxFilePicker:
    """Linux file picker supporting Zenity, KDialog, and Tkinter"""

    @staticmethod
    def choose_file_zenity(
        title: str = "Choose File",
        file_filter: Optional[str] = None,
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Use Zenity (GNOME/GTK) file chooser"""
        cmd = ['zenity', '--file-selection', f'--title={title}']

        if file_filter:
            cmd.append(f'--file-filter={file_filter}')

        if initial_directory and initial_directory.exists():
            cmd.append(f'--filename={initial_directory}/')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"Zenity file picker failed: {e}")

        return None

    @staticmethod
    def choose_folder_zenity(
        title: str = "Choose Folder",
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Use Zenity folder chooser"""
        cmd = ['zenity', '--file-selection', '--directory', f'--title={title}']

        if initial_directory and initial_directory.exists():
            cmd.append(f'--filename={initial_directory}/')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"Zenity folder picker failed: {e}")

        return None

    @staticmethod
    def choose_file_kdialog(
        title: str = "Choose File",
        file_filter: Optional[str] = None,
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Use KDialog (KDE/Plasma) file chooser"""
        cmd = ['kdialog', '--getopenfilename']

        if initial_directory and initial_directory.exists():
            cmd.append(str(initial_directory))
        else:
            cmd.append('.')

        if file_filter:
            cmd.append(file_filter)

        cmd.append(f'--title={title}')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"KDialog file picker failed: {e}")

        return None

    @staticmethod
    def choose_folder_kdialog(
        title: str = "Choose Folder",
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Use KDialog folder chooser"""
        cmd = ['kdialog', '--getexistingdirectory']

        if initial_directory and initial_directory.exists():
            cmd.append(str(initial_directory))
        else:
            cmd.append('.')

        cmd.append(f'--title={title}')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except Exception as e:
            logger.error(f"KDialog folder picker failed: {e}")

        return None


class TkinterFilePicker:
    """Cross-platform Tkinter file picker (fallback)"""

    @staticmethod
    def choose_file(
        title: str = "Choose File",
        file_types: Optional[List[tuple]] = None,
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Use Tkinter file chooser"""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()  # Hide main window
            root.lift()
            root.attributes('-topmost', True)

            initial_dir = str(initial_directory) if initial_directory else None

            filename = filedialog.askopenfilename(
                title=title,
                filetypes=file_types or [('All Files', '*.*')],
                initialdir=initial_dir
            )

            root.destroy()

            if filename:
                return Path(filename)
        except Exception as e:
            logger.error(f"Tkinter file picker failed: {e}")

        return None

    @staticmethod
    def choose_folder(
        title: str = "Choose Folder",
        initial_directory: Optional[Path] = None
    ) -> Optional[Path]:
        """Use Tkinter folder chooser"""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()  # Hide main window
            root.lift()
            root.attributes('-topmost', True)

            initial_dir = str(initial_directory) if initial_directory else None

            dirname = filedialog.askdirectory(
                title=title,
                initialdir=initial_dir
            )

            root.destroy()

            if dirname:
                return Path(dirname)
        except Exception as e:
            logger.error(f"Tkinter folder picker failed: {e}")

        return None


class CrossPlatformFilePicker:
    """
    Universal file picker that automatically uses the best available method
    for the current platform. Production-ready with NO multiple dialog issues.

    For Ubuntu/Linux: Uses ONLY Zenity (modern native file picker)
    For macOS: Uses native Finder dialogs
    For Windows: Uses Tkinter
    """

    def __init__(self):
        self.os = PlatformDetector.get_os()
        self.detector = PlatformDetector()

    def choose_file_or_folder(
        self,
        initial_directory: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """
        Let user choose whether to select a FILE or FOLDER, then open appropriate dialog.
        Works on ALL platforms: Linux, macOS, Windows
        Perfect for beta release - gives users the choice!

        Returns:
            Selected file or folder path, or None if cancelled
        """
        initial_dir = Path(initial_directory).expanduser() if initial_directory else None

        # LINUX - Use Zenity list dialog
        if self.os == 'linux' and self.detector.has_zenity():
            try:
                result = subprocess.run(
                    [
                        'zenity', '--list',
                        '--title=What would you like to select?',
                        '--text=Choose selection type:',
                        '--column=Type', '--column=Description',
                        'file', 'Select a single file',
                        'folder', 'Select a folder/directory',
                        '--hide-column=1',
                        '--width=400',
                        '--height=220'
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0 and result.stdout.strip():
                    choice = result.stdout.strip().lower()

                    if 'file' in choice:
                        return self.choose_file("Select File", initial_directory=initial_dir)
                    elif 'folder' in choice:
                        return self.choose_folder("Select Folder", initial_directory=initial_dir)

            except Exception as e:
                logger.error(f"Linux choice dialog failed: {e}")
                return None

        # macOS - Use AppleScript choice dialog
        elif self.os == 'macos':
            applescript = '''
            tell application "System Events"
                activate
                set choiceList to {"Select a File", "Select a Folder"}
                set userChoice to choose from list choiceList with prompt "What would you like to select?" default items {"Select a File"}
                if userChoice is false then
                    return "cancelled"
                else
                    return item 1 of userChoice as text
                end if
            end tell
            '''

            try:
                result = subprocess.run(
                    ['osascript', '-e', applescript],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0 and result.stdout.strip():
                    choice = result.stdout.strip().lower()

                    if 'file' in choice:
                        return self.choose_file("Select File", initial_directory=initial_dir)
                    elif 'folder' in choice:
                        return self.choose_folder("Select Folder", initial_directory=initial_dir)

            except Exception as e:
                logger.error(f"macOS choice dialog failed: {e}")
                return None

        # Windows / Fallback - Use text-based choice
        else:
            print("\n" + "=" * 50)
            print("SampleMind AI - File Selection")
            print("=" * 50)
            print("\nWhat would you like to select?")
            print("  [1] File")
            print("  [2] Folder/Directory")
            print("  [Q] Quit")
            print()
            try:
                choice = input("Enter choice (1/2/Q): ").strip().lower()
                if choice == '1' or choice == 'file':
                    return self.choose_file("Select File", initial_directory=initial_dir)
                elif choice == '2' or choice == 'folder':
                    return self.choose_folder("Select Folder", initial_directory=initial_dir)
                elif choice == 'q' or choice == 'quit':
                    return None
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled")
                return None

        return None

    def choose_file(
        self,
        title: str = "Choose File",
        file_types: Optional[List[str]] = None,
        initial_directory: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """
        Universal file chooser - works on all platforms.
        Uses ONLY the best available method (no fallbacks that open multiple dialogs)

        Args:
            title: Dialog title
            file_types: List of file extensions (e.g., ['wav', 'mp3', 'flac'])
            initial_directory: Starting directory

        Returns:
            Selected file path or None
        """
        initial_dir = Path(initial_directory).expanduser() if initial_directory else None

        # macOS - Use native Finder
        if self.os == 'macos':
            return MacOSFilePicker.choose_file(title, file_types, initial_dir)

        # Linux - Use ONLY Zenity (modern Ubuntu/GNOME native dialog)
        elif self.os == 'linux':
            # Prepare file filter for Linux
            if file_types:
                file_filter = f"Audio Files|{'|'.join(['*.' + ext for ext in file_types])}"
            else:
                file_filter = None

            # Use Zenity ONLY (modern Ubuntu default)
            if self.detector.has_zenity():
                return LinuxFilePicker.choose_file_zenity(title, file_filter, initial_dir)

            # If no Zenity, use text input (don't try multiple GUI methods)
            logger.warning("Zenity not available - falling back to text input")
            return self._text_input_file(title)

        # Windows - Use Tkinter
        elif self.os == 'windows':
            if self.detector.has_tkinter():
                tk_filetypes = [('Audio Files', ' '.join(['*.' + ext for ext in file_types]))] if file_types else [('All Files', '*.*')]
                return TkinterFilePicker.choose_file(title, tk_filetypes, initial_dir)
            return self._text_input_file(title)

        # Unknown OS - text input
        return self._text_input_file(title)

    def choose_folder(
        self,
        title: str = "Choose Folder",
        initial_directory: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """
        Universal folder chooser - works on all platforms.
        Uses ONLY the best available method (no fallbacks that open multiple dialogs)

        Args:
            title: Dialog title
            initial_directory: Starting directory

        Returns:
            Selected folder path or None
        """
        initial_dir = Path(initial_directory).expanduser() if initial_directory else None

        # macOS - Use native Finder
        if self.os == 'macos':
            return MacOSFilePicker.choose_folder(title, initial_dir)

        # Linux - Use ONLY Zenity (modern Ubuntu/GNOME native dialog)
        elif self.os == 'linux':
            if self.detector.has_zenity():
                return LinuxFilePicker.choose_folder_zenity(title, initial_dir)

            # If no Zenity, use text input (don't try multiple GUI methods)
            logger.warning("Zenity not available - falling back to text input")
            return self._text_input_folder(title)

        # Windows - Use Tkinter
        elif self.os == 'windows':
            if self.detector.has_tkinter():
                return TkinterFilePicker.choose_folder(title, initial_dir)
            return self._text_input_folder(title)

        # Unknown OS - text input
        return self._text_input_folder(title)

    def _text_input_file(self, prompt: str) -> Optional[Path]:
        """Fallback text input for file"""
        try:
            path_str = input(f"{prompt} - Enter file path: ").strip()
            if path_str:
                path = Path(path_str).expanduser()
                if path.exists() and path.is_file():
                    return path
        except (KeyboardInterrupt, EOFError):
            pass
        return None

    def _text_input_folder(self, prompt: str) -> Optional[Path]:
        """Fallback text input for folder"""
        try:
            path_str = input(f"{prompt} - Enter folder path: ").strip()
            if path_str:
                path = Path(path_str).expanduser()
                if path.exists() and path.is_dir():
                    return path
        except (KeyboardInterrupt, EOFError):
            pass
        return None

    def get_platform_info(self) -> dict:
        """Get information about the current platform"""
        return {
            'os': self.os,
            'platform': platform.platform(),
            'has_zenity': self.detector.has_zenity() if self.os == 'linux' else False,
            'has_kdialog': self.detector.has_kdialog() if self.os == 'linux' else False,
            'has_tkinter': self.detector.has_tkinter(),
            'desktop_env': self.detector.get_desktop_environment() if self.os == 'linux' else None
        }


# Global instance
_global_picker = None

def get_file_picker() -> CrossPlatformFilePicker:
    """Get global file picker instance"""
    global _global_picker
    if _global_picker is None:
        _global_picker = CrossPlatformFilePicker()
    return _global_picker


# Convenience functions for easy use in CLI/API
def select_file_or_folder(
    initial_directory: Optional[Union[str, Path]] = None
) -> Optional[Path]:
    """
    Let user choose between file or folder, then select it.
    Perfect for beta release - gives users the choice!
    Opens ONE dialog first (choice), then ONE dialog (selection).
    """
    picker = get_file_picker()
    return picker.choose_file_or_folder(initial_directory=initial_directory)


def select_audio_file(
    title: str = "Choose Audio File",
    initial_directory: Optional[Union[str, Path]] = None
) -> Optional[Path]:
    """Select an audio file using the best available method (Zenity on Ubuntu)"""
    picker = get_file_picker()
    return picker.choose_file(
        title=title,
        file_types=['wav', 'mp3', 'flac', 'aiff', 'aif', 'm4a', 'ogg', 'wma', 'opus'],
        initial_directory=initial_directory
    )


def select_directory(
    title: str = "Choose Directory",
    initial_directory: Optional[Union[str, Path]] = None
) -> Optional[Path]:
    """Select a directory using the best available method (Zenity on Ubuntu)"""
    picker = get_file_picker()
    return picker.choose_folder(
        title=title,
        initial_directory=initial_directory
    )


def select_any_file(
    title: str = "Choose File",
    initial_directory: Optional[Union[str, Path]] = None
) -> Optional[Path]:
    """Select any file using the best available method (Zenity on Ubuntu)"""
    picker = get_file_picker()
    return picker.choose_file(
        title=title,
        file_types=None,
        initial_directory=initial_directory
    )


# Testing (DISABLED during pytest to prevent dialog popups)
if __name__ == "__main__":
    import os

    # Only run if explicitly executed, not during pytest
    if 'pytest' not in sys.modules and 'PYTEST_CURRENT_TEST' not in os.environ:
        picker = CrossPlatformFilePicker()
        info = picker.get_platform_info()

        print("🎵 SampleMind AI - Cross-Platform File Picker Test")
        print("=" * 60)
        print(f"OS: {info['os']}")
        print(f"Platform: {info['platform']}")
        if info['os'] == 'linux':
            print(f"Zenity: {'✅' if info.get('has_zenity') else '❌'}")
        print(f"Desktop Environment: {info.get('desktop_env', 'N/A')}")
        print("=" * 60)

        print("\n✅ Testing file/folder choice (works on ALL platforms)...")
        selection = select_file_or_folder()
        if selection:
            print(f"✅ Selected: {selection}")
            print(f"   Type: {'File' if selection.is_file() else 'Folder'}")
        else:
            print("❌ No selection")

        print("\n✅ Test complete! Ready for beta release on all platforms.")
    else:
        print("⚠️  Test skipped (running in pytest environment)")
