#!/usr/bin/env python3
"""
SampleMind AI Plugin Installer
Cross-platform DAW plugin installation and management system
Supports: FL Studio, Ableton Live
Platforms: Windows, macOS, Linux
"""

import os
import sys
import platform
import shutil
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import argparse


class Platform(Enum):
    """Supported platforms"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class DAW(Enum):
    """Supported Digital Audio Workstations"""
    FL_STUDIO = "fl_studio"
    ABLETON_LIVE = "ableton_live"


@dataclass
class PluginInfo:
    """Plugin installation information"""
    name: str
    version: str
    author: str
    website: str
    description: str


@dataclass
class InstallationPath:
    """Path information for plugin installation"""
    daw: DAW
    platform: Platform
    plugin_dir: Path
    supports_vst3: bool = False
    supports_au: bool = False


class DAWDetector:
    """Detect installed DAWs on the system"""

    def __init__(self):
        self.platform = self._detect_platform()
        self.installed_daws: Dict[DAW, Path] = {}
        self.detect_daws()

    @staticmethod
    def _detect_platform() -> Platform:
        """Detect the current operating system"""
        system = platform.system()
        if system == "Windows":
            return Platform.WINDOWS
        elif system == "Darwin":
            return Platform.MACOS
        elif system == "Linux":
            return Platform.LINUX
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def detect_daws(self) -> None:
        """Detect installed DAWs on the system"""
        if self.platform == Platform.WINDOWS:
            self._detect_windows()
        elif self.platform == Platform.MACOS:
            self._detect_macos()
        elif self.platform == Platform.LINUX:
            self._detect_linux()

    def _detect_windows(self) -> None:
        """Detect DAWs on Windows"""
        import winreg

        # FL Studio detection
        fl_paths = [
            Path("C:/Program Files/Image-Line/FL Studio 21"),
            Path("C:/Program Files (x86)/Image-Line/FL Studio 21"),
            Path("C:/Program Files/Image-Line/FL Studio 20"),
        ]

        for fl_path in fl_paths:
            if fl_path.exists():
                self.installed_daws[DAW.FL_STUDIO] = fl_path
                break

        # Ableton Live detection
        ableton_paths = [
            Path("C:/Program Files/Ableton/Live 12"),
            Path("C:/Program Files/Ableton/Live 11"),
            Path("C:/Program Files (x86)/Ableton/Live 12"),
        ]

        for ableton_path in ableton_paths:
            if ableton_path.exists():
                self.installed_daws[DAW.ABLETON_LIVE] = ableton_path
                break

    def _detect_macos(self) -> None:
        """Detect DAWs on macOS"""
        # FL Studio detection
        fl_paths = [
            Path("/Applications/FL Studio.app"),
        ]

        for fl_path in fl_paths:
            if fl_path.exists():
                self.installed_daws[DAW.FL_STUDIO] = fl_path
                break

        # Ableton Live detection
        ableton_paths = [
            Path("/Applications/Ableton Live 12.app"),
            Path("/Applications/Ableton Live 11.app"),
        ]

        for ableton_path in ableton_paths:
            if ableton_path.exists():
                self.installed_daws[DAW.ABLETON_LIVE] = ableton_path
                break

    def _detect_linux(self) -> None:
        """Detect DAWs on Linux"""
        # FL Studio detection
        fl_paths = [
            Path(os.path.expanduser("~/FL_Studio")),
            Path("/opt/fl_studio"),
        ]

        for fl_path in fl_paths:
            if fl_path.exists():
                self.installed_daws[DAW.FL_STUDIO] = fl_path
                break

        # Ableton Live detection (via snap or AppImage)
        ableton_paths = [
            Path(os.path.expanduser("~/Ableton")),
            Path("/opt/Ableton"),
        ]

        for ableton_path in ableton_paths:
            if ableton_path.exists():
                self.installed_daws[DAW.ABLETON_LIVE] = ableton_path
                break

    def is_daw_installed(self, daw: DAW) -> bool:
        """Check if a DAW is installed"""
        return daw in self.installed_daws

    def get_daw_path(self, daw: DAW) -> Optional[Path]:
        """Get installation path of a DAW"""
        return self.installed_daws.get(daw)

    def list_installed_daws(self) -> List[Tuple[DAW, Path]]:
        """List all installed DAWs"""
        return list(self.installed_daws.items())


class PluginInstaller:
    """Installs plugins to detected DAW installations"""

    def __init__(self, detector: DAWDetector):
        self.detector = detector
        self.plugins_dir = Path(__file__).parent
        self.installation_log: List[str] = []

    def get_fl_studio_plugin_paths(self) -> Dict[Platform, Path]:
        """Get FL Studio plugin installation paths"""
        return {
            Platform.WINDOWS: Path("C:/Program Files/Image-Line/FL Studio 21/Plugins/Fruity/Generators"),
            Platform.MACOS: Path(os.path.expanduser("~/Library/Application Support/Image-Line/FL Studio/Plugins/Fruity/Generators")),
            Platform.LINUX: Path(os.path.expanduser("~/.config/Image-Line/FL Studio/Plugins/Fruity/Generators")),
        }

    def get_ableton_plugin_paths(self) -> Dict[Platform, Path]:
        """Get Ableton Live plugin installation paths"""
        return {
            Platform.WINDOWS: Path(os.path.expandvars("%APPDATA%/Ableton/User Library/Presets/Instruments/Max Instrument")),
            Platform.MACOS: Path(os.path.expanduser("~/Music/Ableton User Library/Presets/Instruments/Max Instrument")),
            Platform.LINUX: Path(os.path.expanduser("~/.Ableton/User Library/Presets/Instruments/Max Instrument")),
        }

    def get_plugin_source_path(self, daw: DAW, platform: Platform) -> Optional[Path]:
        """Get the source plugin file path"""
        if daw == DAW.FL_STUDIO:
            if platform == Platform.WINDOWS:
                return self.plugins_dir / "fl_studio" / "build" / "lib" / "SampleMind_FL_Studio.dll"
            elif platform == Platform.MACOS:
                return self.plugins_dir / "fl_studio" / "build" / "lib" / "libSampleMind_FL_Studio.dylib"
            elif platform == Platform.LINUX:
                return self.plugins_dir / "fl_studio" / "build" / "lib" / "libSampleMind_FL_Studio.so"

        elif daw == DAW.ABLETON_LIVE:
            # For Ableton, we need the Max device and supporting files
            return self.plugins_dir / "ableton" / "SampleMind.amxd"

        return None

    def install_fl_studio_plugin(self) -> bool:
        """Install FL Studio plugin"""
        if not self.detector.is_daw_installed(DAW.FL_STUDIO):
            self.log("❌ FL Studio not detected on this system")
            return False

        platform_paths = self.get_fl_studio_plugin_paths()
        dest_dir = platform_paths.get(self.detector.platform)

        if not dest_dir:
            self.log(f"❌ Unsupported platform for FL Studio plugin")
            return False

        source_path = self.get_plugin_source_path(DAW.FL_STUDIO, self.detector.platform)

        if not source_path or not source_path.exists():
            self.log(f"❌ Plugin source not found: {source_path}")
            self.log(f"   Hint: Run 'cd plugins/fl_studio && mkdir build && cd build'")
            self.log(f"   Then run cmake and make to compile the plugin")
            return False

        try:
            # Create destination directory if it doesn't exist
            dest_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"📁 Created plugin directory: {dest_dir}")

            # Copy plugin file
            dest_file = dest_dir / source_path.name
            shutil.copy2(source_path, dest_file)
            self.log(f"✓ Copied {source_path.name} to {dest_dir}")

            # Verify installation
            if dest_file.exists():
                size_mb = dest_file.stat().st_size / (1024 * 1024)
                self.log(f"✓ Installation verified ({size_mb:.2f} MB)")
                return True
            else:
                self.log(f"❌ Installation verification failed")
                return False

        except PermissionError:
            self.log(f"❌ Permission denied. Try running with administrator/sudo privileges")
            return False
        except Exception as e:
            self.log(f"❌ Installation failed: {e}")
            return False

    def install_ableton_plugin(self) -> bool:
        """Install Ableton Live plugin"""
        if not self.detector.is_daw_installed(DAW.ABLETON_LIVE):
            self.log("❌ Ableton Live not detected on this system")
            return False

        platform_paths = self.get_ableton_plugin_paths()
        dest_dir = platform_paths.get(self.detector.platform)

        if not dest_dir:
            self.log(f"❌ Unsupported platform for Ableton Live plugin")
            return False

        try:
            # Copy Max device file
            amxd_source = self.plugins_dir / "ableton" / "SampleMind.amxd"
            if amxd_source.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / "SampleMind.amxd"
                shutil.copy2(amxd_source, dest_file)
                self.log(f"✓ Copied SampleMind.amxd to {dest_dir}")
            else:
                self.log(f"⚠ Max device file not found: {amxd_source}")

            # Copy communication.js
            js_source = self.plugins_dir / "ableton" / "communication.js"
            if js_source.exists():
                dest_js = dest_dir / "communication.js"
                shutil.copy2(js_source, dest_js)
                self.log(f"✓ Copied communication.js to {dest_dir}")
            else:
                self.log(f"⚠ JavaScript communication file not found: {js_source}")

            # Copy MIDI mapper
            midi_source = self.plugins_dir / "ableton" / "midi_mapper.maxpat"
            if midi_source.exists():
                dest_midi = dest_dir / "midi_mapper.maxpat"
                shutil.copy2(midi_source, dest_midi)
                self.log(f"✓ Copied midi_mapper.maxpat to {dest_dir}")
            else:
                self.log(f"⚠ MIDI mapper file not found: {midi_source}")

            # Verify at least one file was copied
            if dest_dir.exists() and list(dest_dir.glob("*")):
                self.log(f"✓ Ableton Live plugin installation verified")
                return True
            else:
                self.log(f"❌ Ableton Live plugin installation failed")
                return False

        except PermissionError:
            self.log(f"❌ Permission denied. Try running with administrator/sudo privileges")
            return False
        except Exception as e:
            self.log(f"❌ Installation failed: {e}")
            return False

    def uninstall_fl_studio_plugin(self) -> bool:
        """Uninstall FL Studio plugin"""
        platform_paths = self.get_fl_studio_plugin_paths()
        dest_dir = platform_paths.get(self.detector.platform)

        if not dest_dir:
            self.log(f"❌ Unsupported platform")
            return False

        plugin_file = dest_dir / "SampleMind_FL_Studio.dll"
        if self.detector.platform == Platform.MACOS:
            plugin_file = dest_dir / "libSampleMind_FL_Studio.dylib"
        elif self.detector.platform == Platform.LINUX:
            plugin_file = dest_dir / "libSampleMind_FL_Studio.so"

        try:
            if plugin_file.exists():
                plugin_file.unlink()
                self.log(f"✓ Removed FL Studio plugin: {plugin_file}")
                return True
            else:
                self.log(f"⚠ Plugin file not found: {plugin_file}")
                return False

        except PermissionError:
            self.log(f"❌ Permission denied")
            return False
        except Exception as e:
            self.log(f"❌ Uninstall failed: {e}")
            return False

    def uninstall_ableton_plugin(self) -> bool:
        """Uninstall Ableton Live plugin"""
        platform_paths = self.get_ableton_plugin_paths()
        dest_dir = platform_paths.get(self.detector.platform)

        if not dest_dir:
            self.log(f"❌ Unsupported platform")
            return False

        try:
            files_removed = 0

            # Remove Max device
            amxd_file = dest_dir / "SampleMind.amxd"
            if amxd_file.exists():
                amxd_file.unlink()
                self.log(f"✓ Removed SampleMind.amxd")
                files_removed += 1

            # Remove communication.js
            js_file = dest_dir / "communication.js"
            if js_file.exists():
                js_file.unlink()
                self.log(f"✓ Removed communication.js")
                files_removed += 1

            # Remove MIDI mapper
            midi_file = dest_dir / "midi_mapper.maxpat"
            if midi_file.exists():
                midi_file.unlink()
                self.log(f"✓ Removed midi_mapper.maxpat")
                files_removed += 1

            if files_removed > 0:
                self.log(f"✓ Ableton Live plugin uninstalled ({files_removed} files removed)")
                return True
            else:
                self.log(f"⚠ No plugin files found to remove")
                return False

        except PermissionError:
            self.log(f"❌ Permission denied")
            return False
        except Exception as e:
            self.log(f"❌ Uninstall failed: {e}")
            return False

    def verify_installations(self) -> Dict[DAW, bool]:
        """Verify installed plugins are working"""
        results = {}

        for daw in [DAW.FL_STUDIO, DAW.ABLETON_LIVE]:
            if not self.detector.is_daw_installed(daw):
                results[daw] = False
                continue

            if daw == DAW.FL_STUDIO:
                results[daw] = self._verify_fl_studio()
            elif daw == DAW.ABLETON_LIVE:
                results[daw] = self._verify_ableton()

        return results

    def _verify_fl_studio(self) -> bool:
        """Verify FL Studio plugin installation"""
        platform_paths = self.get_fl_studio_plugin_paths()
        dest_dir = platform_paths.get(self.detector.platform)

        if not dest_dir:
            return False

        plugin_file = dest_dir / "SampleMind_FL_Studio.dll"
        if self.detector.platform == Platform.MACOS:
            plugin_file = dest_dir / "libSampleMind_FL_Studio.dylib"
        elif self.detector.platform == Platform.LINUX:
            plugin_file = dest_dir / "libSampleMind_FL_Studio.so"

        return plugin_file.exists()

    def _verify_ableton(self) -> bool:
        """Verify Ableton Live plugin installation"""
        platform_paths = self.get_ableton_plugin_paths()
        dest_dir = platform_paths.get(self.detector.platform)

        if not dest_dir:
            return False

        amxd_file = dest_dir / "SampleMind.amxd"
        return amxd_file.exists()

    def log(self, message: str) -> None:
        """Log installation message"""
        self.installation_log.append(message)
        print(message)

    def get_log(self) -> List[str]:
        """Get full installation log"""
        return self.installation_log

    def save_log(self, log_file: Path) -> None:
        """Save installation log to file"""
        with open(log_file, "w") as f:
            f.write("\n".join(self.installation_log))


def print_banner() -> None:
    """Print installation banner"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  SampleMind AI - Plugin Installer v1.0.0                  ║
║                       Professional Audio Intelligence                      ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")


def main():
    """Main installation routine"""
    parser = argparse.ArgumentParser(
        description="SampleMind AI Plugin Installer - Install plugins to your DAWs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python installer.py --install-all        Install all available plugins
  python installer.py --install fl_studio  Install only FL Studio plugin
  python installer.py --list               List installed DAWs
  python installer.py --verify             Verify plugin installations
  python installer.py --uninstall ableton  Uninstall Ableton plugin
        """,
    )

    parser.add_argument(
        "--install-all",
        action="store_true",
        help="Install all available plugins",
    )

    parser.add_argument(
        "--install",
        choices=["fl_studio", "ableton"],
        help="Install specific plugin (fl_studio or ableton)",
    )

    parser.add_argument(
        "--uninstall",
        choices=["fl_studio", "ableton"],
        help="Uninstall specific plugin",
    )

    parser.add_argument(
        "--uninstall-all",
        action="store_true",
        help="Uninstall all plugins",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List detected DAWs",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify plugin installations",
    )

    parser.add_argument(
        "--log",
        type=Path,
        help="Save installation log to file",
    )

    parser.add_argument(
        "--admin",
        action="store_true",
        help="Run with administrator/sudo privileges",
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Detect DAWs
    print("🔍 Detecting installed DAWs...")
    detector = DAWDetector()

    if detector.list_installed_daws():
        for daw, path in detector.list_installed_daws():
            daw_name = daw.value.replace("_", " ").title()
            print(f"  ✓ {daw_name}: {path}")
    else:
        print("  ⚠ No supported DAWs detected")
        return

    print()

    # Create installer
    installer = PluginInstaller(detector)

    # Handle commands
    if args.list:
        print("Installed DAWs:")
        for daw, path in detector.list_installed_daws():
            daw_name = daw.value.replace("_", " ").title()
            print(f"  • {daw_name}: {path}")

    elif args.verify:
        print("🔍 Verifying plugin installations...\n")
        results = installer.verify_installations()

        for daw, is_installed in results.items():
            daw_name = daw.value.replace("_", " ").title()
            status = "✓ Installed" if is_installed else "✗ Not installed"
            print(f"  {status}: {daw_name}")

    elif args.install:
        print(f"📦 Installing {args.install} plugin...\n")

        if args.install == "fl_studio":
            success = installer.install_fl_studio_plugin()
        else:  # ableton
            success = installer.install_ableton_plugin()

        if success:
            print("\n✅ Installation completed successfully!")
        else:
            print("\n❌ Installation failed")
            sys.exit(1)

    elif args.install_all:
        print("📦 Installing all available plugins...\n")

        success = True
        for daw, _ in detector.list_installed_daws():
            if daw == DAW.FL_STUDIO:
                print("Installing FL Studio plugin...")
                success = installer.install_fl_studio_plugin() and success
            elif daw == DAW.ABLETON_LIVE:
                print("\nInstalling Ableton Live plugin...")
                success = installer.install_ableton_plugin() and success

        print()
        if success:
            print("✅ All plugins installed successfully!")
        else:
            print("⚠ Some plugins failed to install")
            sys.exit(1)

    elif args.uninstall:
        print(f"🗑️  Uninstalling {args.uninstall} plugin...\n")

        if args.uninstall == "fl_studio":
            success = installer.uninstall_fl_studio_plugin()
        else:  # ableton
            success = installer.uninstall_ableton_plugin()

        if success:
            print("\n✅ Uninstall completed successfully!")
        else:
            print("\n❌ Uninstall failed")
            sys.exit(1)

    elif args.uninstall_all:
        print("🗑️  Uninstalling all plugins...\n")

        success = True
        for daw, _ in detector.list_installed_daws():
            if daw == DAW.FL_STUDIO:
                print("Uninstalling FL Studio plugin...")
                success = installer.uninstall_fl_studio_plugin() and success
            elif daw == DAW.ABLETON_LIVE:
                print("\nUninstalling Ableton Live plugin...")
                success = installer.uninstall_ableton_plugin() and success

        print()
        if success:
            print("✅ All plugins uninstalled successfully!")
        else:
            print("⚠ Some plugins failed to uninstall")
            sys.exit(1)

    else:
        # Default: show help and prompt for action
        print("Actions:")
        print("  1. Install all plugins (--install-all)")
        print("  2. Install specific plugin (--install fl_studio|ableton)")
        print("  3. Verify installations (--verify)")
        print("  4. Uninstall plugin (--uninstall fl_studio|ableton)")
        print("  5. List detected DAWs (--list)")
        print()
        print("Run with --help for more options")

    # Save log if requested
    if args.log:
        installer.save_log(args.log)
        print(f"\n📝 Installation log saved to {args.log}")

    print()


if __name__ == "__main__":
    main()
