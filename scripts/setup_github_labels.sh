#!/bin/bash
# Create GitHub Labels for SampleMind AI v6
# Repository: lchtangen/samplemind-ai-v2-phoenix

set -e

echo "🏷️  Creating GitHub Labels..."
echo ""

# Type Labels
echo "Creating Type labels..."
gh label create "bug" --color "d73a4a" --description "Something isn't working" --force
gh label create "enhancement" --color "a2eeef" --description "New feature or request" --force
gh label create "documentation" --color "0075ca" --description "Documentation improvements" --force
gh label create "question" --color "d876e3" --description "Questions or support" --force
gh label create "good first issue" --color "7057ff" --description "Good for newcomers" --force
gh label create "help wanted" --color "008672" --description "Extra attention needed" --force

# Priority Labels
echo "Creating Priority labels..."
gh label create "priority: critical" --color "b60205" --description "Critical issues" --force
gh label create "priority: high" --color "d93f0b" --description "High priority" --force
gh label create "priority: medium" --color "fbca04" --description "Medium priority" --force
gh label create "priority: low" --color "0e8a16" --description "Low priority" --force

# Difficulty Labels
echo "Creating Difficulty labels..."
gh label create "beginner" --color "c5def5" --description "Beginner friendly" --force
gh label create "intermediate" --color "bfd4f2" --description "Some experience needed" --force
gh label create "advanced" --color "7fc8ff" --description "Significant experience" --force

# Status Labels
echo "Creating Status labels..."
gh label create "in progress" --color "fbca04" --description "Work in progress" --force
gh label create "needs review" --color "0075ca" --description "Ready for review" --force
gh label create "blocked" --color "d73a4a" --description "Blocked by dependencies" --force
gh label create "wontfix" --color "ffffff" --description "Won't be fixed" --force

# Component Labels
echo "Creating Component labels..."
gh label create "audio" --color "5319e7" --description "Audio processing" --force
gh label create "ai" --color "1d76db" --description "AI integrations" --force
gh label create "cli" --color "0052cc" --description "Command-line interface" --force
gh label create "api" --color "006b75" --description "API/backend" --force
gh label create "frontend" --color "c2e0c6" --description "Web frontend" --force
gh label create "tests" --color "f9d0c4" --description "Testing related" --force

echo ""
echo "✅ All 23 labels created successfully!"
echo ""
echo "View labels at: https://github.com/lchtangen/samplemind-ai-v2-phoenix/labels"
