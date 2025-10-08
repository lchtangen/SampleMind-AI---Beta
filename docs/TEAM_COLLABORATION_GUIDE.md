# 🤝 SampleMind AI v6 - Team Collaboration Guide

**For:** Project maintainers and new contributors  
**Purpose:** Complete guide to collaborating on SampleMind AI v6  
**Last Updated:** 2025-10-04

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contribution Workflow](#contribution-workflow)
5. [Communication Channels](#communication-channels)
6. [Code Review Process](#code-review-process)
7. [Finding Contributors](#finding-contributors)
8. [Remote Team Best Practices](#remote-team-best-practices)

---

## 🎯 Project Overview

### What is SampleMind AI?

SampleMind AI is an AI-powered music production platform that helps producers analyze, organize, and enhance their sample libraries using advanced machine learning.

**Key Features:**
- 🎵 Deep audio analysis (tempo, key, mood, genre)
- 🤖 AI-powered insights (Gemini 2.5 Pro, OpenAI GPT-4o, local Ollama models)
- 📁 Intelligent sample organization
- 🎛️ DAW integration (FL Studio, Ableton, Logic Pro)
- ⚡ Real-time processing (<100ms with local AI)

### Project Stats
- **Progress:** 70% complete
- **Lines of Code:** 6,238
- **Test Coverage:** 29% (target: 90%+)
- **Contributors:** Looking to grow from 1 to 5-10
- **License:** MIT

### Tech Stack
- **Backend:** Python 3.11+, FastAPI, MongoDB, Redis, ChromaDB
- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **AI/ML:** Google Gemini API, OpenAI API, Ollama, PyTorch
- **Audio:** librosa, soundfile, scipy
- **Testing:** pytest, pytest-asyncio, pytest-cov

---

## 🚀 Getting Started

### Prerequisites

**Required:**
- Python 3.11 or 3.12
- Git
- Basic understanding of async Python
- Familiarity with audio concepts (helpful but not required)

**Recommended:**
- Docker & Docker Compose
- Experience with FastAPI or similar frameworks
- Music production experience
- Experience with AI APIs

### Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/lchtangen/samplemind-ai-v2-phoenix.git
cd samplemind-ai-v6

# 2. Run the setup script
./scripts/setup/quick_start.sh

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Run tests to verify setup
make test

# 5. Start the CLI
python main.py
```

### Environment Setup

Create `.env` file with your API keys (optional for testing):

```bash
# AI Provider Keys (at least one required for full functionality)
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database (for API development)
MONGODB_URI=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379

# JWT Secrets (for auth testing)
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
```

---

## 💻 Development Setup

### Directory Structure

```
samplemind-ai-v6/
├── src/samplemind/           # Main source code
│   ├── core/                 # Core functionality
│   │   ├── engine/           # Audio processing engine
│   │   ├── auth/             # Authentication
│   │   └── database/         # Database clients
│   ├── integrations/         # AI provider integrations
│   ├── interfaces/           # User interfaces
│   │   ├── cli/              # Command-line interface
│   │   ├── api/              # FastAPI REST API
│   │   └── tui/              # Terminal UI
│   └── utils/                # Utilities
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── docs/                     # Documentation
├── frontend/web/             # Next.js web app
└── scripts/                  # Utility scripts
```

### Common Development Commands

```bash
# Setup and installation
make setup                    # Complete environment setup
make install-models           # Download Ollama AI models

# Development
make dev                      # Start FastAPI development server
python main.py                # Run CLI application

# Testing
make test                     # Run all tests with coverage
make lint                     # Run linters (ruff, mypy)
make format                   # Format code (black, isort)
make quality                  # Run all quality checks

# Database
make setup-db                 # Start Docker databases
docker-compose up -d          # Start all services

# Cleanup
make clean                    # Clean temporary files
```

### Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run quality checks**
   ```bash
   make test
   make quality
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

---

## 📝 Contribution Workflow

### Types of Contributions

We welcome all types of contributions:

1. **🐛 Bug Fixes** - Fix issues, resolve test failures
2. **✨ Features** - Add new functionality
3. **📚 Documentation** - Improve guides, add examples
4. **🧪 Tests** - Increase test coverage
5. **🎨 UI/UX** - Improve interfaces
6. **🔧 Refactoring** - Code improvements
7. **🌍 i18n** - Translations (future)

### Finding Issues to Work On

**For Beginners:**
- Look for `good-first-issue` label
- Look for `difficulty: beginner` label
- Focus on documentation and test coverage

**For Experienced Contributors:**
- Look for `difficulty: intermediate` or `difficulty: advanced`
- Check Project Roadmap for priorities
- See `docs/PROJECT_AUDIT.md` for critical needs

### Issue Assignment

1. Comment on the issue: "I'd like to work on this"
2. Wait for maintainer response (usually < 24 hours)
3. Issue will be assigned to you
4. Start working! Ask questions if needed

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Build/maintenance tasks

**Examples:**
```bash
feat(cli): add folder analysis menu option
fix(auth): resolve JWT token expiration issue
docs(readme): update installation instructions
test(audio): increase engine test coverage to 80%
```

### Pull Request Process

1. **Before Creating PR:**
   - All tests pass locally
   - Code is formatted (`make format`)
   - No lint errors (`make lint`)
   - Documentation updated if needed

2. **PR Title:** Follow commit message convention

3. **PR Description:** Use the template (auto-populated)
   - Describe changes
   - Link related issues
   - Add screenshots if UI changes
   - List testing done

4. **Review Process:**
   - At least 1 approval required
   - All CI checks must pass
   - Resolve all review comments
   - Maintainer will merge (do not merge your own PR)

5. **After Merge:**
   - Delete your feature branch
   - Update your fork's main branch

---

## 💬 Communication Channels

### GitHub (Primary)
- **Issues:** Bug reports, feature requests
- **Pull Requests:** Code contributions
- **Discussions:** Q&A, ideas, announcements
- **Projects:** Task tracking and planning

### Discord (Coming Soon)
Planned channels:
- `#general` - General discussion
- `#dev-discussion` - Development topics
- `#bug-reports` - Bug discussion
- `#feature-requests` - Feature ideas
- `#showcase` - Share your work
- `#help` - Get assistance

### Response Time Expectations
- **Issues:** Response within 24-48 hours
- **PRs:** Initial review within 2-3 days
- **Questions:** Response within 24 hours
- **Urgent:** Tag with `urgent` label

### Communication Best Practices
- ✅ Be respectful and constructive
- ✅ Provide context and examples
- ✅ Search existing issues before creating new ones
- ✅ Use clear, descriptive titles
- ✅ Be patient - maintainers are volunteers
- ❌ Don't ping maintainers unnecessarily
- ❌ Don't demand immediate responses

---

## 🔍 Code Review Process

### For Contributors

When submitting a PR:
1. **Self-review first** - Check your own code
2. **Add description** - Explain what and why
3. **Request review** - Tag relevant reviewers
4. **Be responsive** - Address feedback promptly
5. **Don't take it personally** - Feedback is about code, not you

### For Reviewers

When reviewing PRs:
1. **Be constructive** - Suggest solutions, not just problems
2. **Ask questions** - If something is unclear
3. **Approve quickly** - If changes are good
4. **Request changes** - If significant issues
5. **Give praise** - Recognize good work

### Review Checklist

**Code Quality:**
- [ ] Code follows project style guide
- [ ] No obvious bugs or logic errors
- [ ] Handles edge cases and errors
- [ ] No security vulnerabilities

**Testing:**
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage maintained or increased

**Documentation:**
- [ ] Code is well-commented
- [ ] Public APIs documented
- [ ] README updated if needed
- [ ] CHANGELOG updated

**Performance:**
- [ ] No performance regressions
- [ ] Efficient algorithms used
- [ ] No memory leaks

---

## 🔎 Finding Contributors

### Where to Post

1. **GitHub**
   - Add "Help Wanted" to README
   - Create good first issues
   - Use GitHub Topics: `python`, `ai`, `music-production`

2. **Reddit**
   - r/Python - General Python projects
   - r/musicproduction - Music producer community
   - r/WeAreTheMusicMakers - Musicians and producers
   - r/opensource - Open source projects

3. **Discord Servers**
   - Python Discord
   - Music Production Discord
   - AI/ML Discord servers

4. **Forums**
   - KVR Audio Forum
   - Gearspace (formerly Gearslutz)
   - AudioSex
   - VI-Control

5. **Social Media**
   - Twitter/X: `#MusicTech` `#Python` `#OpenSource`
   - LinkedIn: Post in groups
   - Dev.to: Write blog post about project

### Roles Needed

#### 1. Python Developers (2-3 needed)
**Skills:**
- Strong Python 3.11+ experience
- Async/await patterns
- FastAPI or similar frameworks
- Testing (pytest)

**Responsibilities:**
- Backend development
- API endpoint creation
- Bug fixes
- Code reviews

#### 2. Audio Engineers (1-2 needed)
**Skills:**
- Music production experience
- Understanding of audio concepts
- DAW experience (FL Studio, Ableton, Logic)
- Python helpful but not required

**Responsibilities:**
- Feature validation
- Audio algorithm review
- DAW integration testing
- User perspective feedback

#### 3. Documentation Writers (1 needed)
**Skills:**
- Clear technical writing
- Markdown proficiency
- Understanding of developer needs

**Responsibilities:**
- Write/update guides
- Create tutorials
- Improve README
- API documentation

#### 4. UI/UX Designers (1 needed)
**Skills:**
- React/Next.js experience
- UI design
- Understanding of music production workflows

**Responsibilities:**
- Web UI design
- CLI/TUI improvements
- User experience optimization

#### 5. Beta Testers (5-10 needed)
**Skills:**
- Music production experience
- Willingness to report bugs
- Detailed feedback

**Responsibilities:**
- Test features
- Report bugs
- Suggest improvements
- Provide use cases

### Recruitment Message Template

```markdown
🎵 **SampleMind AI - AI-Powered Music Production Tool**

We're building an open-source AI platform for music producers!

**What we're building:**
- AI-powered sample analysis (tempo, key, mood)
- Smart sample organization
- DAW integration (FL Studio, Ableton, Logic)
- Local + cloud AI (Gemini, OpenAI, Ollama)

**We need:**
- Python developers (FastAPI, async)
- Audio engineers (music production experience)
- Documentation writers
- UI/UX designers
- Beta testers

**Tech Stack:**
Python, FastAPI, Next.js, AI/ML, Audio Processing

**Status:** 70% complete, entering beta soon

**How to contribute:**
[GitHub repo link]
See CONTRIBUTING.md for details

**Why join:**
- Learn AI/ML in audio domain
- Build portfolio project
- Collaborate with music tech community
- MIT licensed - your work is yours

Questions? Comment below or join our [Discord/repo]!
```

---

## 👥 Remote Team Best Practices

### For First-Time Remote Team Lead

#### Start Small and Scale
- Begin with 2-3 contributors
- Learn processes before expanding
- Build trust and rapport
- Scale when comfortable

#### Clear Expectations
- Define working hours (flexible)
- Set response time expectations
- Clarify contribution frequency
- Document decision-making process

#### Over-Communicate
- Write everything down
- Share context liberally
- Provide frequent updates
- Encourage questions

#### Build Culture
- Welcome new contributors warmly
- Recognize contributions publicly
- Foster inclusive environment
- Celebrate wins together

### Team Meeting Structure

#### Weekly Sync (Optional, Async-Friendly)
- **When:** Same time each week
- **Duration:** 30-45 minutes
- **Format:** Video call or written updates
- **Agenda:**
  - Progress updates
  - Blockers discussion
  - Next week planning
  - Open questions

#### Monthly Planning
- Review roadmap
- Prioritize issues
- Assign major tasks
- Celebrate achievements

### Async-First Practices

1. **Written Updates**
   - Use GitHub Discussions
   - Post weekly progress
   - Document decisions

2. **Time Zone Friendly**
   - No required meeting times
   - Record video calls
   - Provide meeting notes

3. **Clear Documentation**
   - Write everything down
   - Keep docs updated
   - Link to relevant resources

### Conflict Resolution

1. **Address issues early** - Don't let problems fester
2. **Listen actively** - Understand all perspectives
3. **Focus on solutions** - Not blame
4. **Escalate if needed** - Seek outside mediation
5. **Document agreements** - Write down resolutions

### Recognition and Motivation

- **Public praise** - Recognize contributions on GitHub
- **Contributor spotlight** - Feature contributors monthly
- **Early access** - Give core contributors beta access
- **Mentorship** - Pair experienced with new contributors
- **Swag** - Send stickers/shirts when possible

---

## 🎓 Onboarding New Contributors

### Day 1: Welcome
- Send welcome message
- Share links to docs
- Assign "buddy" for questions
- Suggest good first issue

### Day 2-3: Environment Setup
- Help with setup issues
- Verify tests running
- Walk through codebase
- Answer architecture questions

### Week 1: First Contribution
- Guide through first PR
- Provide detailed code review
- Merge first contribution
- Celebrate publicly

### Week 2-4: Integration
- Assign medium-difficulty issues
- Include in team discussions
- Gather feedback on experience
- Ask for suggestions

---

## 📊 Success Metrics

### Contributor Health
- Time to first contribution
- PR merge time
- Issue response time
- Contributor retention rate

### Code Quality
- Test coverage
- Bug resolution time
- Code review thoroughness
- Documentation completeness

### Community Growth
- New contributors per month
- Active contributors
- Community engagement (issues, discussions)
- External mentions/shares

---

## 🆘 Getting Help

### For Contributors
- Read existing documentation first
- Check GitHub Discussions
- Ask in Discord (when available)
- Tag maintainers on GitHub

### For Maintainers
- Refer to this guide
- Consult with core team
- Seek advice in maintainer communities
- Document learnings for future

---

## 📚 Additional Resources

### Internal Docs
- `README.md` - Project overview
- `CONTRIBUTING.md` - Detailed contribution guidelines
- `docs/PROJECT_AUDIT.md` - Current project status
- `docs/PROJECT_ROADMAP.md` - Future plans
- `CLAUDE.md` - AI assistant instructions

### External Resources
- [Open Source Guides](https://opensource.guide/) - General open source advice
- [GitHub Skills](https://skills.github.com/) - Learn GitHub
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit standards
- [Semantic Versioning](https://semver.org/) - Version numbering

---

## 🙏 Acknowledgments

Thank you to all contributors, testers, and supporters of SampleMind AI!

Your contributions make this project possible. ❤️

---

**Questions about collaboration?**  
Open an issue or discussion on GitHub!

**Ready to contribute?**  
See `CONTRIBUTING.md` and pick an issue to start!
