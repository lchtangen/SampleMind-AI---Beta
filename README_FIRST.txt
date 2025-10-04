═══════════════════════════════════════════════════════════════════════════════
                    🔥 WELCOME TO SAMPLEMIND AI PHOENIX! 🔥
              Beta v2.0 - AI-Powered Music Production Platform
═══════════════════════════════════════════════════════════════════════════════


👋 HELLO! START HERE IF YOU'RE NEW!
═══════════════════════════════════════════════════════════════════════════════

This is the EASIEST way to get started with Phoenix. No technical knowledge
needed - just follow these super simple steps!


📍 STEP 1: Open Your Terminal
═══════════════════════════════════════════════════════════════════════════════

On Linux/Mac:
  • Press: Ctrl + Alt + T  (or search for "Terminal")

On Windows:
  • Search for: "PowerShell" or "Terminal"


📂 STEP 2: Go to the Phoenix Folder
═══════════════════════════════════════════════════════════════════════════════

Copy and paste this command, then press Enter:

    cd ~/Projects/samplemind-ai-v6

(If you installed Phoenix somewhere else, use that path instead)


🚀 STEP 3: Run the Magic Setup Script
═══════════════════════════════════════════════════════════════════════════════

Copy and paste this command, then press Enter:

    ./start_phoenix.sh

This script will:
  ✓ Check everything is in the right place
  ✓ Set up your environment automatically
  ✓ Install all the tools you need
  ✓ Make sure Phoenix is ready to use

It takes about 30 seconds and shows you a nice progress bar!


🎉 THAT'S IT! You're Done!
═══════════════════════════════════════════════════════════════════════════════

After the script finishes, you can start using Phoenix right away!


🎯 WHAT CAN YOU DO NOW?
═══════════════════════════════════════════════════════════════════════════════

Try These Simple Commands:
──────────────────────────

1️⃣  Get Help (shows all available commands):

    sm --help


2️⃣  Analyze a Sample (finds BPM, key, and more):

    sm analyze your-sample.wav


3️⃣  Import Your Sample Library:

    sm import folder ~/Music/Samples


4️⃣  Auto-Tag with AI (let the AI identify your sounds):

    sm tag auto kick.wav


5️⃣  Check Phoenix Version:

    sm --version


📚 LEARN MORE (OPTIONAL)
═══════════════════════════════════════════════════════════════════════════════

Want to dive deeper? Check out these guides:

📖 For Beginners:
   → Open: docs/QUICKSTART_PHOENIX_BEGINNER.md
   → Command: cat docs/QUICKSTART_PHOENIX_BEGINNER.md

📖 For Advanced Users:
   → Open: docs/PHASE_1_PHOENIX_IMPLEMENTATION.md
   → Command: cat docs/PHASE_1_PHOENIX_IMPLEMENTATION.md

📖 Full Feature List:
   → Open: docs/V6_FEATURE_INTEGRATION_MASTER_PLAN.md
   → Command: cat docs/V6_FEATURE_INTEGRATION_MASTER_PLAN.md


❓ TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

Problem: "Permission denied"
Solution: Make the script executable first:
          chmod +x start_phoenix.sh
          Then try again: ./start_phoenix.sh

Problem: "Command not found" when using 'sm'
Solution: Make sure you're in the project folder and run:
          source .venv/bin/activate
          Then try 'sm --help' again

Problem: "No such file or directory"
Solution: Check you're in the right folder:
          pwd
          (Should show: /home/yourname/Projects/samplemind-ai-v6)


💡 TIPS FOR BEGINNERS
═══════════════════════════════════════════════════════════════════════════════

Tip #1: Use Tab to Auto-Complete
  • Type "sm ana" and press TAB → it completes to "sm analyze"
  • Super helpful when you forget command names!

Tip #2: Every Command Has Built-in Help
  • Add --help to any command to see what it does
  • Example: sm import --help

Tip #3: Use Absolute Paths for Files
  • Instead of: sample.wav
  • Use: ~/Music/Samples/sample.wav
  • No more "file not found" errors!

Tip #4: Start Small
  • Don't import 10,000 samples at once on your first try
  • Start with one folder (maybe 10-50 files)
  • Once you're comfortable, go bigger!

Tip #5: Your Environment Stays Active
  • Once you run start_phoenix.sh, your environment is ready
  • You can use 'sm' commands until you close the terminal
  • To turn it off: type 'deactivate'


🔥 QUICK REFERENCE CARD (Print or Screenshot This!)
═══════════════════════════════════════════════════════════════════════════════

╔════════════════════════════════════════════════════════════════════════════╗
║                    PHOENIX ESSENTIAL COMMANDS                              ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Get Help            →  sm --help                                          ║
║  Check Version       →  sm --version                                       ║
║                                                                            ║
║  Analyze Sample      →  sm analyze sample.wav                              ║
║  Analyze Folder      →  sm analyze batch ~/Music/Samples                   ║
║                                                                            ║
║  Import Samples      →  sm import folder ~/Music/Samples                   ║
║  Import with Watch   →  sm import folder ~/Music --watch                   ║
║                                                                            ║
║  Auto-Tag (AI)       →  sm tag auto sample.wav                             ║
║  Manual Tag          →  sm tag set sample.wav --genre techno               ║
║                                                                            ║
║  Organize Library    →  sm organize by-genre ~/Music/Samples               ║
║  Smart Pack Builder  →  sm organize pack "Dark Techno" --ai                ║
║                                                                            ║
║  Show Config         →  sm config show                                     ║
║  Set Config          →  sm config set library_path ~/Music/Samples         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


🎵 EXAMPLE WORKFLOW FOR NEW PRODUCERS
═══════════════════════════════════════════════════════════════════════════════

Let's say you just downloaded a sample pack. Here's what you'd do:

Step 1: Import the pack
        sm import folder ~/Downloads/MySamplePack

Step 2: Let AI analyze and tag everything
        sm analyze batch ~/Downloads/MySamplePack
        sm tag auto ~/Downloads/MySamplePack/*.wav

Step 3: Organize by genre
        sm organize by-genre ~/Downloads/MySamplePack

Step 4: Find similar sounds
        sm analyze find-similar kick.wav

Step 5: Build a custom pack
        sm organize pack "My Techno Pack" --bpm-range 120-130

Done! Your samples are organized, tagged, and ready to use! 🎉


🌟 YOU'RE ALL SET!
═══════════════════════════════════════════════════════════════════════════════

Phoenix is designed to be simple and powerful. Don't be afraid to experiment!

You can't break anything by trying commands - worst case, you'll see an error
message that tells you what went wrong.

Have fun creating amazing music! 🔥🎶

═══════════════════════════════════════════════════════════════════════════════
                            Happy Producing! 🎵
═══════════════════════════════════════════════════════════════════════════════
