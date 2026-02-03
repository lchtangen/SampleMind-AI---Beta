# SampleMind AI Beta Testing Guide

**Version**: 1.0 Beta
**Date**: February 4, 2026
**Status**: Ready for Beta Users

---

## Welcome to SampleMind AI Beta! 🎵

Thank you for being part of our beta testing community! This guide will help you get the most out of SampleMind AI and contribute valuable feedback that shapes the future of the platform.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Features](#core-features)
3. [How to Report Issues](#how-to-report-issues)
4. [How to Suggest Features](#how-to-suggest-features)
5. [Getting Help](#getting-help)
6. [Community Guidelines](#community-guidelines)
7. [Privacy & Data](#privacy--data)
8. [FAQ](#faq)

---

## Quick Start

### Installation

**Option 1: CLI (Recommended)**
```bash
pip install samplemind-ai
samplemind --help
```

**Option 2: Web Interface**
```bash
# Access at http://localhost:3000
docker-compose up
```

### First Steps

1. **Upload an audio file**
   - Use any MP3, WAV, AIFF, or OGG file
   - Recommended: 30 seconds to 10 minutes

2. **Analyze your audio**
   - CLI: `samplemind analyze audio.wav`
   - Web: Click "Analyze" button

3. **Explore results**
   - View tempo, key, genre, mood
   - Find similar samples
   - Generate MIDI

4. **Share feedback**
   - Click "?" button in bottom-right (web)
   - Use `samplemind feedback` (CLI)
   - Alternatively, create GitHub issue

---

## Core Features

### 1. Audio Analysis

Instantly analyze your audio for:
- **Tempo (BPM)** - Beat per minute detection
- **Key** - Musical key (C Major, A Minor, etc.)
- **Genre** - Music style classification
- **Energy** - 0-1 scale of audio intensity
- **Mood** - Emotional character (happy, dark, etc.)

**Analysis Levels:**
- **BASIC** - Fast analysis, essential features (~500ms)
- **STANDARD** - Default, comprehensive features (~1.5s)
- **DETAILED** - Includes harmonic analysis (~3s)
- **PROFESSIONAL** - Full analysis with confidence scores (~5s)

### 2. Similar Sample Discovery

Find songs in your library that match:
- Same tempo (±2 BPM)
- Same key signature
- Similar genre/mood
- Comparable energy level

**Use Cases:**
- Build playlists with consistent energy
- Find samples for remixing
- Discover new music in your collection

### 3. Project Synchronization

Get recommendations based on your current project:
1. Enter your project's BPM and key
2. Get samples that match your project
3. Create cohesive arrangements instantly

**Example:**
- Project: 120 BPM, C Major
- Results: All samples at 120 BPM in C Major (or compatible keys)

### 4. MIDI Generation

Extract MIDI from audio:
- **Melody** - Main melodic line
- **Harmony** - Harmonic content
- **Drums** - Drum pattern
- **Bass Line** - Bass track

Perfect for:
- Transcription
- Remixing
- Music theory learning
- DAW integration

### 5. DAW Integration

**Ableton Live:**
- Use Max for Live device
- Real-time analysis in mixer
- Drag-and-drop samples

**FL Studio** (Coming Soon):
- Native plugin
- Project integration
- Sample browser sync

---

## How to Report Issues

### Quick Report

**Option 1: Feedback Widget (Web)**
1. Click "?" button (bottom-right)
2. Select "Bug Report"
3. Describe the issue
4. Click "Send"

**Option 2: CLI**
```bash
samplemind feedback --type bug --message "Description of issue"
```

**Option 3: GitHub**
1. Go to [Issues](https://github.com/samplemind-ai/samplemind-ai/issues)
2. Click "New Issue"
3. Select "Bug Report"
4. Fill out form

### Detailed Bug Report

Include:
- **What you were doing** - Step-by-step description
- **Expected behavior** - What should have happened
- **Actual behavior** - What actually happened
- **Error message** - Exact error text (if any)
- **Environment** - OS, browser, version
- **Screenshot/Video** - Visual evidence (if applicable)

### Example Report

```
Title: Analysis fails with MP3 files larger than 50MB

What I was doing:
1. Opened SampleMind CLI
2. Tried to analyze a 65MB MP3 file
3. Waited for analysis to complete

Expected: Analysis completes and shows results
Actual: Error message appears after 2 seconds

Error: "File too large: max 50MB"

Environment:
- OS: macOS 13.2
- Version: 1.0 Beta
```

---

## How to Suggest Features

### Quick Suggestion

**Option 1: Feedback Widget (Web)**
1. Click "?" button
2. Select "Feature Request"
3. Describe your idea
4. Click "Send"

**Option 2: GitHub**
1. Go to [Issues](https://github.com/samplemind-ai/samplemind-ai/issues)
2. Click "New Issue"
3. Select "Feature Request"
4. Fill out form

**Option 3: Discussions**
1. Go to [Discussions](https://github.com/samplemind-ai/samplemind-ai/discussions)
2. Choose category
3. Create new discussion
4. Share your idea

### Feature Request Template

```
Title: [Brief description of feature]

Problem:
[What problem does this solve? What do you want to do?]

Solution:
[How would you like this feature to work?]

Use Case:
[When would you use this? Give examples]

Alternatives:
[What do you do now instead?]

Additional Context:
[Screenshots, examples, references]
```

### Example Request

```
Title: Batch Analysis with Progress Bar

Problem:
When analyzing 50+ files, there's no indication of progress.
I'd like to see how many files have been processed.

Solution:
Show a progress bar that updates as each file is analyzed.
Include estimated time remaining.

Use Case:
I frequently batch-analyze my sample library (500+ files).
Currently I have no idea when it will finish.

Alternatives:
I use external scripts to process files sequentially.
```

---

## Getting Help

### Documentation

- **Quick Start**: [docs/GUIDES/quickstart.md](../GUIDES/quickstart.md)
- **CLI Reference**: [docs/GUIDES/cli_reference.md](../GUIDES/cli_reference.md)
- **Web UI Guide**: [docs/GUIDES/web_ui_guide.md](../GUIDES/web_ui_guide.md)
- **FAQ**: [See below](#faq)

### Community

- **Discord**: [Join Discord Community](https://discord.gg/samplemind)
- **Q&A Forum**: [GitHub Discussions Q&A](https://github.com/samplemind-ai/samplemind-ai/discussions/categories/q-a)
- **Email**: support@samplemind.ai

### Support Channels

| Channel | Best For | Response Time |
|---------|----------|----------------|
| Discord | Quick questions, chat | <1 hour |
| GitHub Issues | Bug reports | <24 hours |
| GitHub Discussions | Feature ideas | <24 hours |
| Email | Detailed support | <48 hours |

### Asking Good Questions

When asking for help:
1. **Search first** - Check if someone already asked
2. **Be specific** - Include what you were doing
3. **Provide context** - Include OS, version, file type
4. **Share attempts** - What have you already tried
5. **Be patient** - Our team is small but responsive

---

## Community Guidelines

### Be Respectful

- Treat other community members with respect
- No harassment, discrimination, or hate speech
- Disagree constructively
- Respect diverse perspectives

### Stay On Topic

- Keep discussions relevant to SampleMind AI
- Use appropriate channels (bugs in Issues, ideas in Discussions)
- No spam or self-promotion

### Share Knowledge

- Help other beta testers when you can
- Share your workflows and tips
- Report good solutions to common problems
- Celebrate community contributions

### Give Honest Feedback

- Be truthful about your experience
- Both positive and negative feedback is valuable
- Explain your reasoning
- Focus on the feature, not the person

### Report Responsibly

- Don't publicly disclose security vulnerabilities
- Report security issues to: security@samplemind.ai
- Give the team time to fix before publicizing

---

## Privacy & Data

### What We Collect

**Analytics (if enabled):**
- Feature usage (which buttons you click)
- Performance metrics (how long analysis takes)
- Error types (which errors occur)
- Aggregated statistics (no personal data)

**NOT collected:**
- Your audio file contents
- Personal information (name, email, location)
- Keystroke data
- Sensitive file metadata

### Your Control

**Settings > Privacy:**
- [ ] Enable analytics tracking
- [ ] Enable session recordings (for debugging)
- [ ] Share anonymous crash reports

You can change these anytime.

### Data Retention

- Session data: 30 days
- Analytics: 90 days
- Error logs: 30 days
- User data can be deleted anytime

### GDPR & Privacy

We comply with:
- GDPR (General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- Standard privacy practices

**Your rights:**
- Access your data anytime
- Export your data anytime
- Delete your data anytime

See full [Privacy Policy](../PRIVACY.md)

---

## FAQ

### Installation & Setup

**Q: How do I install SampleMind AI?**
A: See "Quick Start" section above for CLI and Web installation.

**Q: What are the system requirements?**
A: Python 3.11+, 4GB RAM (8GB recommended), 5GB disk space

**Q: Can I use it offline?**
A: CLI uses offline models by default. Web requires internet for cloud features.

### Features & Usage

**Q: What audio formats are supported?**
A: MP3, WAV, AIFF, OGG, FLAC, M4A, Opus

**Q: What's the maximum file size?**
A: 100MB for single files, 500MB total per batch

**Q: How long does analysis take?**
A: BASIC: 500ms, STANDARD: 1-2s, DETAILED: 2-3s

**Q: Can I analyze the same file multiple times?**
A: Yes, results are cached for 24 hours

**Q: Does it work with samples I don't own?**
A: Yes, for personal use. Respect copyright for commercial use.

### Issues & Support

**Q: Analysis is taking too long**
A: Try BASIC level, check internet connection, restart app

**Q: I get "File not found" error**
A: Check file path, ensure file is readable, try absolute path

**Q: Similar samples are not accurate**
A: Try different analysis level, check BPM accuracy, increase search radius

**Q: How do I report a bug?**
A: See "How to Report Issues" section above

**Q: When will FL Studio plugin be ready?**
A: Q2 2026 (depends on external SDK availability)

### Privacy & Data

**Q: Is my data private?**
A: Yes, we don't share data with third parties

**Q: Can I opt out of analytics?**
A: Yes, in Settings > Privacy

**Q: How long is data kept?**
A: Session data 30 days, analytics 90 days, error logs 30 days

**Q: Can I delete my account?**
A: Yes, go to Settings > Account > Delete Account

---

## Beta Testing Tips

### Get the Most Out of Beta

1. **Test thoroughly** - Try different file types and sizes
2. **Report systematically** - Note what works and what doesn't
3. **Provide context** - Include details with all feedback
4. **Be constructive** - Suggest solutions, not just problems
5. **Be patient** - We're actively improving based on feedback

### What Happens With Your Feedback?

1. **Read** - Team reviews all feedback daily
2. **Triage** - We prioritize by impact and frequency
3. **Implement** - Top issues/features are worked on
4. **Release** - Fixed/new features appear in next version
5. **Thank** - We credit contributors in release notes

---

## Thank You! 🙏

Your participation in beta testing is invaluable. Every bug report, feature suggestion, and piece of feedback directly shapes SampleMind AI's development.

We're excited to have you part of the community!

**Questions?** → [Discord](https://discord.gg/samplemind)
**Report bugs?** → [GitHub Issues](https://github.com/samplemind-ai/samplemind-ai/issues)
**Have ideas?** → [GitHub Discussions](https://github.com/samplemind-ai/samplemind-ai/discussions)

---

**Ready to get started?** → [Quick Start Guide](#quick-start)

**Last Updated**: February 4, 2026
**Status**: Beta v1.0
**Next Review**: February 15, 2026
