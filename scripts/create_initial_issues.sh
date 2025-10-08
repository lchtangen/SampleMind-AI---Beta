#!/bin/bash
# Create initial "good first issues" for SampleMind AI v6

set -e

echo "📝 Creating initial issues..."
echo ""

# Issue 1: Documentation
echo "Creating Issue #1: Add missing docstrings..."
gh issue create \
  --title "Add missing docstrings to utility functions" \
  --body "**Description:**
Add comprehensive docstrings to all functions in the file picker utility.

**Tasks:**
- Add docstrings following Google style
- Include parameter types and return types
- Add usage examples

**File:** \`src/samplemind/utils/file_picker.py\`

**Difficulty:** 🟢 Beginner
**Time:** 30-60 minutes

See \`docs/GOOD_FIRST_ISSUES.md\` Issue #1 for details." \
  --label "good first issue,beginner,documentation" \
  --milestone "Beta v0.6.0"

# Issue 2: CLI
echo "Creating Issue #2: Improve CLI help messages..."
gh issue create \
  --title "Improve CLI help messages" \
  --body "**Description:**
Make help messages more descriptive and user-friendly.

**Tasks:**
- Add examples to command descriptions
- Include expected input formats
- Clarify what each option does

**File:** \`src/samplemind/interfaces/cli/menu.py\`

**Difficulty:** 🟢 Beginner
**Time:** 1 hour

See \`docs/GOOD_FIRST_ISSUES.md\` Issue #2 for details." \
  --label "good first issue,beginner,cli" \
  --milestone "Beta v0.6.0"

# Issue 3: Documentation
echo "Creating Issue #3: Fix typos in documentation..."
gh issue create \
  --title "Fix typos in documentation" \
  --body "**Description:**
Run spell check and fix typos across documentation.

**Tools:**
\`\`\`bash
pip install codespell
codespell docs/
\`\`\`

**Difficulty:** 🟢 Beginner
**Time:** 30 minutes

See \`docs/GOOD_FIRST_ISSUES.md\` Issue #3 for details." \
  --label "good first issue,beginner,documentation" \
  --milestone "Beta v0.6.0"

# Issue 4: Code Quality
echo "Creating Issue #4: Add type hints to config module..."
gh issue create \
  --title "Add type hints to config module" \
  --body "**Description:**
Add type hints to all functions and class methods.

**File:** \`src/samplemind/config/settings.py\`

**Example:**
\`\`\`python
# Before
def load_config(path):
    return json.load(open(path))

# After
def load_config(path: Path) -> Dict[str, Any]:
    \"\"\"Load configuration from JSON file.\"\"\"
    return json.load(open(path))
\`\`\`

**Difficulty:** 🟢 Beginner
**Time:** 1 hour

See \`docs/GOOD_FIRST_ISSUES.md\` Issue #4 for details." \
  --label "good first issue,beginner,enhancement" \
  --milestone "Beta v0.6.0"

# Issue 5: Error Handling
echo "Creating Issue #5: Improve error messages in audio engine..."
gh issue create \
  --title "Improve error messages in audio engine" \
  --body "**Description:**
Make error messages more helpful for users.

**Tasks:**
- Add context to exceptions
- Suggest solutions
- Include relevant file paths

**File:** \`src/samplemind/core/engine/audio_engine.py\`

**Example:**
\`\`\`python
# Before
raise ValueError(\"Invalid audio file\")

# After
raise ValueError(
    f\"Invalid audio file: {file_path}\\n\"
    f\"Supported formats: WAV, MP3, FLAC\\n\"
    f\"Please check the file format and try again.\"
)
\`\`\`

**Difficulty:** 🟢 Beginner
**Time:** 1-2 hours

See \`docs/GOOD_FIRST_ISSUES.md\` Issue #5 for details." \
  --label "good first issue,beginner,audio" \
  --milestone "Beta v0.6.0"

echo ""
echo "✅ All 5 initial issues created successfully!"
echo ""
echo "View issues at: https://github.com/lchtangen/samplemind-ai-v2-phoenix/issues"
