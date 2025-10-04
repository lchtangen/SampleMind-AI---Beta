#!/usr/bin/env python3
"""
SampleMind AI v6 - Setup Verification Script
Verify all components are working correctly
"""

import sys
from pathlib import Path
import os

# Color codes for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_env_vars():
    """Check environment variables"""
    print(f"\n{BLUE}📋 Checking Environment Variables...{RESET}")

    required_vars = {
        'GOOGLE_AI_API_KEY': 'Gemini 2.5 Pro API Key',
        'OPENAI_API_KEY': 'OpenAI GPT-5 API Key'
    }

    all_present = True
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"  {GREEN}✓{RESET} {var} ({description})")
        else:
            print(f"  {RED}✗{RESET} {var} ({description}) - NOT SET")
            all_present = False

    return all_present

def check_dependencies():
    """Check required Python packages"""
    print(f"\n{BLUE}📦 Checking Dependencies...{RESET}")

    required_packages = [
        ('google.generativeai', 'Google Generative AI'),
        ('openai', 'OpenAI'),
        ('librosa', 'Librosa (Audio Processing)'),
        ('soundfile', 'SoundFile'),
        ('scipy', 'SciPy'),
        ('numpy', 'NumPy'),
        ('rich', 'Rich (Terminal UI)'),
        ('typer', 'Typer (CLI)'),
        ('questionary', 'Questionary (Interactive prompts)'),
        ('mutagen', 'Mutagen (Audio metadata)'),
    ]

    all_present = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  {GREEN}✓{RESET} {description}")
        except ImportError:
            print(f"  {RED}✗{RESET} {description} - NOT INSTALLED")
            all_present = False

    return all_present

def check_project_structure():
    """Check project file structure"""
    print(f"\n{BLUE}📁 Checking Project Structure...{RESET}")

    required_files = [
        'main.py',
        'demo_gemini_cli.py',
        'src/samplemind/core/engine/audio_engine.py',
        'src/samplemind/integrations/google_ai_integration.py',
        'src/samplemind/integrations/ai_manager.py',
        'src/samplemind/interfaces/cli/menu.py',
        '.env',
        'GEMINI_CLI_GUIDE.md',
        'SETUP_COMPLETE.md',
    ]

    all_present = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  {GREEN}✓{RESET} {file_path}")
        else:
            print(f"  {RED}✗{RESET} {file_path} - MISSING")
            all_present = False

    return all_present

def check_test_audio():
    """Check test audio samples"""
    print(f"\n{BLUE}🎵 Checking Test Audio Samples...{RESET}")

    test_dir = Path('test_audio_samples')
    if test_dir.exists():
        audio_files = list(test_dir.glob('*.wav'))
        if audio_files:
            print(f"  {GREEN}✓{RESET} Found {len(audio_files)} test audio files:")
            for audio_file in audio_files[:5]:  # Show max 5
                print(f"    • {audio_file.name}")
            return True
        else:
            print(f"  {YELLOW}⚠{RESET} No .wav files in test_audio_samples/")
            return False
    else:
        print(f"  {RED}✗{RESET} test_audio_samples/ directory not found")
        return False

def test_imports():
    """Test key imports"""
    print(f"\n{BLUE}🔧 Testing Key Imports...{RESET}")

    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))

        print(f"  {BLUE}Testing audio engine...{RESET}")
        from samplemind.core.engine.audio_engine import AudioEngine
        print(f"  {GREEN}✓{RESET} Audio Engine")

        print(f"  {BLUE}Testing Google AI integration...{RESET}")
        from samplemind.integrations.google_ai_integration import GoogleAIMusicProducer
        print(f"  {GREEN}✓{RESET} Google AI Integration")

        print(f"  {BLUE}Testing AI Manager...{RESET}")
        from samplemind.integrations.ai_manager import SampleMindAIManager
        print(f"  {GREEN}✓{RESET} AI Manager")

        print(f"  {BLUE}Testing CLI...{RESET}")
        from samplemind.interfaces.cli.menu import SampleMindCLI
        print(f"  {GREEN}✓{RESET} CLI Interface")

        return True

    except Exception as e:
        print(f"  {RED}✗{RESET} Import failed: {str(e)}")
        return False

def test_gemini_connection():
    """Test Gemini API connection"""
    print(f"\n{BLUE}🤖 Testing Gemini API Connection...{RESET}")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            print(f"  {RED}✗{RESET} GOOGLE_AI_API_KEY not set")
            return False

        import google.generativeai as genai
        genai.configure(api_key=api_key)

        print(f"  {BLUE}Creating Gemini model...{RESET}")
        model = genai.GenerativeModel('gemini-2.5-pro')

        print(f"  {BLUE}Testing simple prompt...{RESET}")
        response = model.generate_content("Say 'Hello from Gemini!' in JSON format: {\"message\": \"...\"}")

        if response and response.text:
            print(f"  {GREEN}✓{RESET} Gemini API connection successful!")
            print(f"  {GREEN}✓{RESET} Response: {response.text[:100]}")
            return True
        else:
            print(f"  {RED}✗{RESET} No response from Gemini")
            return False

    except Exception as e:
        print(f"  {RED}✗{RESET} Gemini test failed: {str(e)}")
        return False

def print_summary(checks):
    """Print final summary"""
    print(f"\n{'='*60}")
    print(f"{BLUE}📊 VERIFICATION SUMMARY{RESET}")
    print(f"{'='*60}\n")

    total = len(checks)
    passed = sum(checks.values())
    failed = total - passed

    for check_name, status in checks.items():
        icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"  {icon} {check_name}")

    print(f"\n{'='*60}")

    if passed == total:
        print(f"{GREEN}✅ ALL CHECKS PASSED! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}🎉 Your setup is complete and ready to use!{RESET}\n")
        print(f"{BLUE}Next steps:{RESET}")
        print(f"  1. Run demo: {YELLOW}python demo_gemini_cli.py{RESET}")
        print(f"  2. Start CLI: {YELLOW}python main.py{RESET}")
        print(f"  3. Quick analyze: {YELLOW}python main.py analyze test_audio_samples/test_chord_120bpm.wav{RESET}\n")
        return True
    else:
        print(f"{RED}❌ VERIFICATION FAILED ({passed}/{total} checks passed){RESET}\n")
        print(f"{YELLOW}Please fix the failed checks above.{RESET}\n")
        return False

def main():
    """Run all verification checks"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  🎵 SampleMind AI v6 - Setup Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    checks = {
        'Environment Variables': check_env_vars(),
        'Python Dependencies': check_dependencies(),
        'Project Structure': check_project_structure(),
        'Test Audio Samples': check_test_audio(),
        'Module Imports': test_imports(),
        'Gemini API Connection': test_gemini_connection(),
    }

    success = print_summary(checks)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
