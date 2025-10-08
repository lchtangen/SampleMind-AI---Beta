# 🔧 GitHub Repository Setup Guide

**Purpose:** Configure GitHub repository for optimal collaboration  
**Time Required:** 15-20 minutes  
**Prerequisites:** Repository admin access

---

## 📋 Quick Setup Checklist

- [ ] Create labels
- [ ] Create milestones
- [ ] Enable Discussions
- [ ] Configure branch protection
- [ ] Set up secrets (optional, for CI/CD)

---

## 🏷️ Step 1: Create Labels

**Navigate to:** Repository → Issues → Labels

### Type Labels (6)
```
bug                  #d73a4a    Something isn't working
enhancement          #a2eeef    New feature or request
documentation        #0075ca    Documentation improvements
question             #d876e3    Questions or support
good first issue     #7057ff    Good for newcomers
help wanted          #008672    Extra attention needed
```

### Priority Labels (4)
```
priority: critical   #b60205    Critical issues blocking release
priority: high       #d93f0b    High priority
priority: medium     #fbca04    Medium priority
priority: low        #0e8a16    Low priority
```

### Difficulty Labels (3)
```
beginner            #c5def5    Beginner friendly (1-2 hrs)
intermediate        #bfd4f2    Some experience needed (2-4 hrs)
advanced            #7fc8ff    Significant experience (4+ hrs)
```

### Status Labels (4)
```
in progress         #fbca04    Work in progress
needs review        #0075ca    Ready for review
blocked             #d73a4a    Blocked by dependencies
wontfix             #ffffff    Won't be fixed/implemented
```

### Component Labels (6)
```
audio               #5319e7    Audio processing
ai                  #1d76db    AI integrations
cli                 #0052cc    Command-line interface
api                 #006b75    API/backend
frontend            #c2e0c6    Web frontend
tests               #f9d0c4    Testing related
```

**CLI Command to create all labels:**
```bash
# Install gh CLI: https://cli.github.com/
# Authenticate: gh auth login

# Then run:
gh label create "bug" --color "d73a4a" --description "Something isn't working"
gh label create "enhancement" --color "a2eeef" --description "New feature or request"
gh label create "documentation" --color "0075ca" --description "Documentation improvements"
gh label create "question" --color "d876e3" --description "Questions or support"
gh label create "good first issue" --color "7057ff" --description "Good for newcomers"
gh label create "help wanted" --color "008672" --description "Extra attention needed"
gh label create "priority: critical" --color "b60205" --description "Critical issues"
gh label create "priority: high" --color "d93f0b" --description "High priority"
gh label create "priority: medium" --color "fbca04" --description "Medium priority"
gh label create "priority: low" --color "0e8a16" --description "Low priority"
gh label create "beginner" --color "c5def5" --description "Beginner friendly"
gh label create "intermediate" --color "bfd4f2" --description "Some experience needed"
gh label create "advanced" --color "7fc8ff" --description "Significant experience"
gh label create "in progress" --color "fbca04" --description "Work in progress"
gh label create "needs review" --color "0075ca" --description "Ready for review"
gh label create "blocked" --color "d73a4a" --description "Blocked by dependencies"
gh label create "wontfix" --color "ffffff" --description "Won't be fixed"
gh label create "audio" --color "5319e7" --description "Audio processing"
gh label create "ai" --color "1d76db" --description "AI integrations"
gh label create "cli" --color "0052cc" --description "Command-line interface"
gh label create "api" --color "006b75" --description "API/backend"
gh label create "frontend" --color "c2e0c6" --description "Web frontend"
gh label create "tests" --color "f9d0c4" --description "Testing related"
```

---

## 🎯 Step 2: Create Milestones

**Navigate to:** Repository → Issues → Milestones

### Milestone 1: Beta v0.6.0
- **Due date:** 1 week from now
- **Description:**
  ```
  Initial beta release for testing
  
  Goals:
  - 75%+ tests passing
  - Critical bugs fixed
  - Documentation complete
  - 5-10 beta testers recruited
  ```

### Milestone 2: Beta v0.7.0
- **Due date:** 4 weeks from now
- **Description:**
  ```
  Improved beta with community feedback
  
  Goals:
  - 85%+ tests passing
  - All critical bugs fixed
  - Web UI alpha
  - 20+ active beta testers
  - Performance benchmarks met
  ```

### Milestone 3: v1.0.0 Release
- **Due date:** 12 weeks from now
- **Description:**
  ```
  Production release
  
  Goals:
  - 95%+ tests passing
  - All features complete
  - Production-ready
  - Public launch
  - Marketing campaign
  - First 100 users
  ```

**CLI Command:**
```bash
gh api repos/:owner/:repo/milestones -f title="Beta v0.6.0" -f description="Initial beta release"
gh api repos/:owner/:repo/milestones -f title="Beta v0.7.0" -f description="Improved beta"
gh api repos/:owner/:repo/milestones -f title="v1.0.0 Release" -f description="Production release"
```

---

## 💬 Step 3: Enable GitHub Discussions

**Navigate to:** Repository → Settings → General → Features

1. ✅ Check "Discussions"
2. Click "Set up Discussions"
3. Create categories:

### Discussion Categories

#### 📢 Announcements
- **Type:** Announcement
- **Description:** Project updates and releases
- **Format:** Only maintainers can post

#### 💡 Ideas
- **Type:** Open Discussion
- **Description:** Feature requests and suggestions
- **Format:** Anyone can post

#### 🙏 Q&A
- **Type:** Q&A
- **Description:** Questions and support
- **Format:** Anyone can post, answers can be marked

#### 🐛 Bug Reports
- **Type:** Open Discussion  
- **Description:** Discuss bugs before creating issues
- **Format:** Anyone can post

#### 📖 Tutorials
- **Type:** Open Discussion
- **Description:** How-to guides and tutorials
- **Format:** Anyone can post

#### 🎵 Show and Tell
- **Type:** Show and Tell
- **Description:** Share your results and projects
- **Format:** Anyone can post

#### 🤝 Collaboration
- **Type:** Open Discussion
- **Description:** Team discussions and coordination
- **Format:** Anyone can post

---

## 🛡️ Step 4: Configure Branch Protection

**Navigate to:** Repository → Settings → Branches → Add rule

### Main Branch Protection
**Branch name pattern:** `main`

**Settings:**
- ✅ Require a pull request before merging
  - ✅ Require approvals: 1
  - ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - Status checks: CI, Test, Lint
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings (even for admins)

**Optional (for teams):**
- ✅ Require review from Code Owners
- ✅ Restrict who can push to matching branches

---

## 🔐 Step 5: Set Up Secrets (Optional)

**Navigate to:** Repository → Settings → Secrets and variables → Actions

### Required for CI/CD

**Docker Hub (if using):**
```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
```

**Codecov (for coverage reporting):**
```
CODECOV_TOKEN=your_codecov_token
```

**Vercel (for frontend deployment):**
```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_org_id
VERCEL_PROJECT_ID=your_project_id
```

**PyPI (for package publishing):**
```
PYPI_TOKEN=your_pypi_api_token
```

---

## 📊 Step 6: Create GitHub Project Board (Optional)

**Navigate to:** Repository → Projects → New project

### Project Setup
1. **Template:** Board
2. **Name:** SampleMind Development
3. **Description:** Track development progress

### Columns to Create
```
📥 Backlog       - Future work
✅ To Do         - Ready to start
🚧 In Progress   - Being worked on
👀 Review        - Needs code review
✅ Done          - Completed
```

### Automation Rules
- **To Do → In Progress:** When issue is assigned
- **In Progress → Review:** When PR is opened
- **Review → Done:** When PR is merged
- **Done (auto-archive):** After 7 days

---

## 🎨 Step 7: Customize Repository

**Navigate to:** Repository → Settings

### General Settings
- **Description:** AI-powered music production assistant with intelligent audio analysis
- **Website:** https://samplemind.ai (if available)
- **Topics:** `ai`, `music`, `audio`, `python`, `machine-learning`, `music-production`, `audio-analysis`, `fl-studio`

### Features
- ✅ Issues
- ✅ Projects
- ✅ Discussions
- ✅ Wiki (optional)
- ❌ Sponsorships (unless ready)

### Social Preview
Upload a banner image (1280x640px) showing:
- Project logo
- Tagline: "AI-Powered Music Production Assistant"
- Key features visualization

---

## 📝 Step 8: Create Initial Issues

Use the issues from `docs/GOOD_FIRST_ISSUES.md` to populate your issue tracker.

**Quick script to create first 5 issues:**
```bash
# Issue 1: Documentation
gh issue create \
  --title "Add missing docstrings to utility functions" \
  --body "See docs/GOOD_FIRST_ISSUES.md #1" \
  --label "good first issue,beginner,documentation"

# Issue 2: CLI
gh issue create \
  --title "Improve CLI help messages" \
  --body "See docs/GOOD_FIRST_ISSUES.md #2" \
  --label "good first issue,beginner,cli"

# Issue 3: Documentation
gh issue create \
  --title "Fix typos in documentation" \
  --body "See docs/GOOD_FIRST_ISSUES.md #3" \
  --label "good first issue,beginner,documentation"

# Issue 4: Code Quality
gh issue create \
  --title "Add type hints to config module" \
  --body "See docs/GOOD_FIRST_ISSUES.md #4" \
  --label "good first issue,beginner,enhancement"

# Issue 5: Error Handling
gh issue create \
  --title "Improve error messages in audio engine" \
  --body "See docs/GOOD_FIRST_ISSUES.md #5" \
  --label "good first issue,beginner,audio"
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] All labels created (23 total)
- [ ] All milestones created (3 total)
- [ ] Discussions enabled with categories
- [ ] Branch protection active on `main`
- [ ] At least 5 "good first issues" created
- [ ] Repository description and topics set
- [ ] README.md has contributor section
- [ ] CONTRIBUTING.md linked in README

---

## 🚀 Post-Setup Actions

### 1. Announce Beta Testing
Create a pinned issue:
```markdown
Title: 🚀 Beta Testing - Join Us!

We're looking for beta testers! See docs/BETA_TESTING_GUIDE.md

What you get:
- Early access to cutting-edge AI music tools
- Direct influence on product development
- Free lifetime access when we launch
- Beta tester badge & recognition

How to join:
1. Comment on this issue
2. We'll add you to the beta tester team
3. Follow the Beta Testing Guide

Let's build the future of AI music production together! 🎵🤖
```

### 2. Create Discussion Post
Post in Announcements:
```markdown
Title: Welcome to SampleMind AI! 👋

We're excited to have you here!

📚 New here? Start with:
- README.md - Project overview
- docs/BETA_TESTING_GUIDE.md - Join beta testing
- docs/CONTRIBUTING.md - Contribute to the project

🎯 Looking to contribute?
- Check out "good first issues"
- Read docs/GOOD_FIRST_ISSUES.md
- Join our discussions

🐛 Found a bug?
- Search existing issues first
- Use our bug report template
- Include reproduction steps

Let's make music production more intelligent! 🚀
```

### 3. Update README Badge Section
Add these badges to your README.md:
```markdown
[![GitHub issues](https://img.shields.io/github/issues/YOUR-USERNAME/samplemind-ai-v6)](https://github.com/YOUR-USERNAME/samplemind-ai-v6/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/YOUR-USERNAME/samplemind-ai-v6)](https://github.com/YOUR-USERNAME/samplemind-ai-v6/pulls)
[![GitHub Discussions](https://img.shields.io/github/discussions/YOUR-USERNAME/samplemind-ai-v6)](https://github.com/YOUR-USERNAME/samplemind-ai-v6/discussions)
[![Contributors](https://img.shields.io/github/contributors/YOUR-USERNAME/samplemind-ai-v6)](https://github.com/YOUR-USERNAME/samplemind-ai-v6/graphs/contributors)
```

---

## 📞 Need Help?

- **GitHub CLI docs:** https://cli.github.com/manual/
- **GitHub Actions:** https://docs.github.com/en/actions
- **Branch Protection:** https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches

---

**Last Updated:** 2025-01-04  
**Setup Time:** ~20 minutes  
**Difficulty:** Beginner
