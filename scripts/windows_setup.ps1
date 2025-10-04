# SampleMind AI v6 - Windows Automated Setup Script
# Supports: Windows 10 (1809+), Windows 11
#
# Usage:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\scripts\windows_setup.ps1
#

# Requires PowerShell 5.1+
#Requires -Version 5.1

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green "✓ $args" }
function Write-Info { Write-ColorOutput Cyan "→ $args" }
function Write-Warning { Write-ColorOutput Yellow "⚠ $args" }
function Write-Error { Write-ColorOutput Red "✗ $args" }
function Write-Header { Write-ColorOutput Blue $args }

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Header "╔════════════════════════════════════════════════════════════╗"
Write-Header "║      🪟 SampleMind AI v6 - Windows Setup Wizard 🪟      ║"
Write-Header "╚════════════════════════════════════════════════════════════╝"
Write-Output ""

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Detect Windows version
function Get-WindowsInfo {
    Write-Info "Detecting Windows version..."

    $os = Get-CimInstance Win32_OperatingSystem
    $version = $os.Version
    $caption = $os.Caption
    $build = $os.BuildNumber

    Write-Success "Windows Version: $caption"
    Write-Success "Build: $build"
    Write-Success "Architecture: $env:PROCESSOR_ARCHITECTURE"

    return @{
        Version = $version
        Caption = $caption
        Build = $build
    }
}

# Check for Chocolatey
function Test-Chocolatey {
    return $null -ne (Get-Command choco -ErrorAction SilentlyContinue)
}

# Install Chocolatey
function Install-Chocolatey {
    Write-Header "`n🍫 Installing Chocolatey Package Manager..."

    if (Test-Chocolatey) {
        Write-Success "Chocolatey already installed"
        $chocoVersion = choco --version
        Write-Info "Version: $chocoVersion"
        return
    }

    Write-Info "Installing Chocolatey..."

    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey installed successfully"
    } catch {
        Write-Error "Failed to install Chocolatey: $_"
        Write-Warning "Please install manually from: https://chocolatey.org/install"
        return $false
    }

    return $true
}

# Install system dependencies
function Install-SystemDependencies {
    Write-Header "`n📦 Installing system dependencies..."

    # Check if Chocolatey is available
    if (-not (Test-Chocolatey)) {
        Write-Error "Chocolatey not available. Cannot install dependencies."
        return $false
    }

    Write-Info "Installing Python 3.11..."
    choco install python311 -y --force

    Write-Info "Installing FFmpeg..."
    choco install ffmpeg -y

    Write-Info "Installing Git..."
    choco install git -y

    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    Write-Success "System dependencies installed"
    return $true
}

# Setup Python virtual environment
function Setup-PythonEnvironment {
    Write-Header "`n🐍 Setting up Python environment..."

    Set-Location $ProjectRoot

    # Find Python 3.11
    $pythonPaths = @(
        "C:\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "C:\Program Files\Python311\python.exe"
    )

    $pythonExe = $null
    foreach ($path in $pythonPaths) {
        if (Test-Path $path) {
            $pythonExe = $path
            break
        }
    }

    if (-not $pythonExe) {
        # Try to find from PATH
        $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    }

    if (-not $pythonExe) {
        Write-Error "Python 3.11 not found. Please install Python 3.11 from python.org"
        return $false
    }

    $pythonVersion = & $pythonExe --version
    Write-Info "Python found: $pythonVersion"
    Write-Info "Python path: $pythonExe"

    # Create virtual environment
    if (-not (Test-Path ".venv")) {
        Write-Info "Creating virtual environment..."
        & $pythonExe -m venv .venv
    } else {
        Write-Info "Virtual environment already exists"
    }

    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"

    # Upgrade pip
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet

    Write-Success "Python environment ready"
    return $true
}

# Install Python packages
function Install-PythonPackages {
    Write-Header "`n📚 Installing Python packages..."

    # Activate venv
    & ".\.venv\Scripts\Activate.ps1"

    # Install from requirements.txt
    if (Test-Path "requirements.txt") {
        Write-Info "Installing from requirements.txt..."
        pip install -r requirements.txt --quiet
    }

    # Install additional packages
    Write-Info "Installing AI packages..."
    pip install google-generativeai openai mutagen --quiet

    Write-Success "Python packages installed"
    return $true
}

# Configure API keys
function Configure-APIKeys {
    Write-Header "`n🔑 Configuring API keys..."

    if (Test-Path ".env") {
        Write-Info ".env file already exists"
        $overwrite = Read-Host "Overwrite? (y/N)"
        if ($overwrite -ne 'y' -and $overwrite -ne 'Y') {
            Write-Info "Skipping API configuration"
            return
        }
    }

    Write-Info "Please enter your API keys (or press Enter to skip):"
    Write-Output ""

    $geminiKey = Read-Host "Gemini API Key (PRIMARY)"
    $openaiKey = Read-Host "OpenAI API Key (FALLBACK - optional)"

    if (-not $geminiKey) { $geminiKey = "your_gemini_key_here" }
    if (-not $openaiKey) { $openaiKey = "your_openai_key_here" }

    # Create .env file
    $envContent = @"
# SampleMind AI v6 - Environment Configuration

# Google AI (Gemini) API Configuration - PRIMARY
GOOGLE_AI_API_KEY=$geminiKey

# OpenAI API Configuration - FALLBACK
OPENAI_API_KEY=$openaiKey

# Music AI Configuration
DEFAULT_MODEL=gemini-2.5-pro
MUSIC_MODEL=gemini-2.5-pro
MAX_TOKENS=8192
TEMPERATURE=0.7

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
CACHE_ENABLED=true
BATCH_PROCESSING=true

# FL Studio Integration
FL_STUDIO_INTEGRATION=true
REAL_TIME_ANALYSIS=true
STREAMING_ENABLED=true

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
ENABLE_COST_OPTIMIZATION=true

# Multi-API Support
PRIMARY_API=google_ai
FALLBACK_API=openai
API_ROTATION_ENABLED=false
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8

    Write-Success "API keys configured (.env created)"
}

# Run verification
function Run-Verification {
    Write-Header "`n🔍 Running system verification..."

    & ".\.venv\Scripts\Activate.ps1"

    if (Test-Path "verify_setup.py") {
        python verify_setup.py
    } else {
        Write-Warning "Verification script not found, skipping..."
    }
}

# Create desktop shortcut
function Create-DesktopShortcut {
    Write-Header "`n🖥️ Creating desktop shortcut..."

    $createShortcut = Read-Host "Create desktop shortcut? (y/N)"
    if ($createShortcut -ne 'y' -and $createShortcut -ne 'Y') {
        return
    }

    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$Home\Desktop\SampleMind AI.lnk")
    $Shortcut.TargetPath = "$ProjectRoot\.venv\Scripts\python.exe"
    $Shortcut.Arguments = "$ProjectRoot\main.py"
    $Shortcut.WorkingDirectory = $ProjectRoot
    $Shortcut.IconLocation = "$ProjectRoot\assets\icon.ico"
    $Shortcut.Description = "AI-Powered Music Production Assistant"
    $Shortcut.Save()

    Write-Success "Desktop shortcut created"
}

# Create PowerShell alias
function Create-PowerShellAlias {
    Write-Header "`n⚡ Creating PowerShell alias..."

    $createAlias = Read-Host "Add 'smai' command alias? (y/N)"
    if ($createAlias -ne 'y' -and $createAlias -ne 'Y') {
        return
    }

    $profilePath = $PROFILE

    # Create profile if it doesn't exist
    if (-not (Test-Path $profilePath)) {
        New-Item -Path $profilePath -ItemType File -Force | Out-Null
    }

    # Check if alias already exists
    $profileContent = Get-Content $profilePath -ErrorAction SilentlyContinue
    if ($profileContent -match "function.*SampleMind") {
        Write-Info "Alias already exists in profile"
        return
    }

    # Add alias function
    $aliasFunction = @"

# SampleMind AI
function Start-SampleMind {
    Set-Location "$ProjectRoot"
    & .\.venv\Scripts\Activate.ps1
    python main.py `$args
}

Set-Alias smai Start-SampleMind
"@

    Add-Content -Path $profilePath -Value $aliasFunction

    Write-Success "Alias added to PowerShell profile"
    Write-Info "Restart PowerShell or run: . `$PROFILE"
}

# Add to context menu
function Add-ContextMenu {
    Write-Header "`n📁 Adding context menu integration..."

    $addContext = Read-Host "Add 'Analyze with SampleMind AI' to right-click menu? (y/N)"
    if ($addContext -ne 'y' -and $addContext -ne 'Y') {
        return
    }

    if (-not (Test-Administrator)) {
        Write-Warning "Administrator privileges required for context menu integration"
        Write-Info "Please run this script as Administrator to enable this feature"
        return
    }

    $pythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
    $mainPy = "$ProjectRoot\main.py"

    # Create registry entries for .wav files
    $regPath = "HKEY_CLASSES_ROOT\SystemFileAssociations\.wav\shell\SampleMind"

    New-Item -Path "Registry::$regPath" -Force | Out-Null
    Set-ItemProperty -Path "Registry::$regPath" -Name "(Default)" -Value "Analyze with SampleMind AI"

    New-Item -Path "Registry::$regPath\command" -Force | Out-Null
    Set-ItemProperty -Path "Registry::$regPath\command" -Name "(Default)" -Value "`"$pythonExe`" `"$mainPy`" analyze `"%1`""

    Write-Success "Context menu integration added"
    Write-Info "Right-click any .wav file > Analyze with SampleMind AI"
}

# Show next steps
function Show-NextSteps {
    Write-Output ""
    Write-Header "╔════════════════════════════════════════════════════════════╗"
    Write-Header "║              ✅ Setup Complete! 🎉                        ║"
    Write-Header "╚════════════════════════════════════════════════════════════╝"
    Write-Output ""
    Write-ColorOutput Green "Next steps:"
    Write-Output ""
    Write-Output "  1. $(Write-ColorOutput Yellow 'Activate environment:')"
    Write-Output "     $(Write-ColorOutput Cyan '.\.venv\Scripts\Activate.ps1')"
    Write-Output ""
    Write-Output "  2. $(Write-ColorOutput Yellow 'Run demo:')"
    Write-Output "     $(Write-ColorOutput Cyan 'python demo_gemini_cli.py')"
    Write-Output ""
    Write-Output "  3. $(Write-ColorOutput Yellow 'Start interactive CLI:')"
    Write-Output "     $(Write-ColorOutput Cyan 'python main.py')"
    Write-Output ""
    Write-Output "  4. $(Write-ColorOutput Yellow 'Analyze audio:')"
    Write-Output "     $(Write-ColorOutput Cyan 'python main.py analyze C:\Music\song.wav')"
    Write-Output ""
    Write-ColorOutput Yellow "📚 Documentation:"
    Write-Output "  • Quick Start: $(Write-ColorOutput Cyan 'Get-Content QUICKSTART.md')"
    Write-Output "  • Windows Guide: $(Write-ColorOutput Cyan 'Get-Content WINDOWS_GUIDE.md')"
    Write-Output "  • CLI Guide: $(Write-ColorOutput Cyan 'Get-Content GEMINI_CLI_GUIDE.md')"
    Write-Output ""
    Write-ColorOutput Yellow "🔧 Troubleshooting:"
    Write-Output "  • Logs: $(Write-ColorOutput Cyan '$env:APPDATA\SampleMind\Logs\')"
    Write-Output "  • Issues: $(Write-ColorOutput Cyan 'https://github.com/yourusername/samplemind-ai-v6/issues')"
    Write-Output ""
}

# Main setup flow
function Main {
    Write-Info "Starting automated setup..."
    Write-Output ""

    # Check administrator status
    if (Test-Administrator) {
        Write-Success "Running with Administrator privileges"
    } else {
        Write-Warning "Not running as Administrator - some features will be limited"
    }

    # Get Windows info
    $windowsInfo = Get-WindowsInfo

    # Install Chocolatey
    $chocoResult = Install-Chocolatey
    if (-not $chocoResult) {
        Write-Warning "Continuing without Chocolatey..."
    }

    # Install system dependencies
    Install-SystemDependencies

    # Setup Python environment
    $pythonResult = Setup-PythonEnvironment
    if (-not $pythonResult) {
        Write-Error "Failed to setup Python environment"
        return
    }

    # Install Python packages
    Install-PythonPackages

    # Configure API keys
    Configure-APIKeys

    # Run verification
    Run-Verification

    # Optional features
    Create-DesktopShortcut
    Create-PowerShellAlias
    Add-ContextMenu

    # Show next steps
    Show-NextSteps

    Write-ColorOutput Green "🎉 Installation complete!"
}

# Run main
try {
    Main
} catch {
    Write-Error "Setup failed: $_"
    Write-Output $_.ScriptStackTrace
}
