# 🚀 GitHub Repository Setup Guide

## SampleMind AI v2.0 - Phoenix Beta Release

This guide will walk you through setting up your private GitHub repository for the v2.0 Phoenix beta release.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- [ ] GitHub account (https://github.com)
- [ ] Git configured locally
- [ ] GitHub CLI (`gh`) installed (optional, but recommended)

---

## 🎯 Quick Setup (3 Steps)

### Step 1: Run the Setup Script

The setup script will:
- Configure your Git identity (if needed)
- Set default branch to `main`
- Create `.gitignore` and `.gitattributes`
- Stage all files
- Create initial commit
- Create version tag `v2.0.0-beta`

**Run this command:**

```bash
./scripts/complete-github-setup.sh
```

If the script prompts you for your name and email, provide them. These will be used for all your Git commits.

**Example:**
```
Your name (e.g., John Doe): Your Name Here
Your email (e.g., john@example.com): your.email@example.com
```

---

### Step 2: Create GitHub Repository

You have **two options** to create your GitHub repository:

#### Option 1: Using GitHub CLI (RECOMMENDED) ⭐

If you have the GitHub CLI (`gh`) installed and authenticated:

```bash
gh repo create samplemind-ai-v2-phoenix --private \
  --description "SampleMind AI v2.0 Phoenix - Private beta development" \
  --source=. --push
```

**This will:**
- ✅ Create a private repository
- ✅ Add it as remote `origin`
- ✅ Push your code and tags
- ✅ Set up branch tracking

**Done! Skip to Step 3.**

---

#### Option 2: Manual GitHub Setup 🖱️

If you prefer to use the web interface:

**2.1. Create Repository on GitHub:**

1. Go to: https://github.com/new
2. Fill in the details:
   - **Repository name:** `samplemind-ai-v2-phoenix`
   - **Description:** `SampleMind AI v2.0 Phoenix - Private beta development`
   - **Visibility:** ⚠️ **PRIVATE** (CRITICAL!)
   - **Initialize:** ❌ Do NOT check "Add a README file"
   - **Initialize:** ❌ Do NOT add .gitignore
   - **Initialize:** ❌ Do NOT add a license
3. Click **"Create repository"**

**2.2. Push Your Code:**

After creating the repository, GitHub will show you instructions. Use these commands:

```bash
# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/samplemind-ai-v2-phoenix.git

# Push main branch
git push -u origin main

# Push tag
git push origin v2.0.0-beta
```

**Example if your GitHub username is "johndoe":**
```bash
git remote add origin https://github.com/johndoe/samplemind-ai-v2-phoenix.git
git push -u origin main
git push origin v2.0.0-beta
```

---

### Step 3: Verify Setup ✅

After pushing, verify everything is set up correctly:

```bash
# Check remote is configured
git remote -v

# Check branch tracking
git branch -vv

# View all tags
git tag -l

# View commit history
git log --oneline -5
```

**Expected output:**
- Remote `origin` pointing to your GitHub repository
- Branch `main` tracking `origin/main`
- Tag `v2.0.0-beta` present
- Initial commit with full project details

---

## 🔐 Security Checklist

Ensure your repository is properly secured:

- [ ] Repository visibility is set to **PRIVATE**
- [ ] No `.env` files are committed (check `.gitignore`)
- [ ] No API keys in code
- [ ] No sensitive credentials committed
- [ ] Repository description doesn't reveal internal details

**Check repository visibility:**
```bash
gh repo view --web  # Opens repo in browser
```

Or visit: `https://github.com/YOUR_USERNAME/samplemind-ai-v2-phoenix`

---

## 📊 Repository Overview

### What's Included

Your repository contains:

```
✅ Complete v2.0.0-beta codebase
✅ All 24,081 lines of documentation
✅ Frontend (Next.js 14)
✅ Backend (FastAPI)
✅ Database configurations
✅ Test suite
✅ Scripts and utilities
✅ Docker configurations
✅ CI/CD workflows
```

### What's NOT Included (Properly Ignored)

These are excluded via `.gitignore`:

```
❌ node_modules/
❌ .next/ (Next.js build)
❌ __pycache__/ (Python cache)
❌ .env (environment variables)
❌ *.log (log files)
❌ data/ (database files)
❌ uploads/ (user uploads)
❌ .vscode/, .idea/ (IDE configs)
```

---

## 🎨 Repository Customization

### Update Repository README

The repository includes `README-GITHUB.md` - a comprehensive README designed for the GitHub repository. To use it:

**Option 1: Replace existing README:**
```bash
mv README.md README-LOCAL.md
mv README-GITHUB.md README.md
git add README.md README-LOCAL.md
git commit -m "docs: update README for GitHub"
git push
```

**Option 2: Keep both:**
```bash
# Keep current README.md for local development
# Use README-GITHUB.md as reference or for later
```

### Add Repository Topics

Enhance discoverability (once public) by adding topics:

```bash
gh repo edit --add-topic ai
gh repo edit --add-topic audio-processing
gh repo edit --add-topic music-production
gh repo edit --add-topic nextjs
gh repo edit --add-topic fastapi
gh repo edit --add-topic python
gh repo edit --add-topic typescript
gh repo edit --add-topic machine-learning
```

Or add via web interface: Settings → Topics

---

## 🔄 Daily Workflow

### Making Changes

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, then stage
git add .

# Commit with descriptive message
git commit -m "feat: add new feature description"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request via CLI
gh pr create --title "Add feature" --body "Description"

# Or create PR via web interface
```

### Keeping Main Branch Updated

```bash
# Switch to main
git checkout main

# Pull latest changes
git pull origin main

# Merge feature branch (after PR approved)
git merge feature/your-feature-name

# Push
git push origin main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 🏷️ Version Tagging

### Creating New Tags

When you're ready for a new version:

```bash
# Create annotated tag
git tag -a v2.0.1-beta -m "Version 2.0.1-beta

Release notes:
- Bug fixes
- Performance improvements"

# Push tag to GitHub
git push origin v2.0.1-beta

# Or push all tags
git push --tags
```

### Viewing Tags

```bash
# List all tags
git tag -l

# Show tag details
git show v2.0.0-beta

# Check out specific tag
git checkout v2.0.0-beta
```

---

## 🚨 Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution:**
```bash
# Check SSH keys
gh auth status

# Re-authenticate
gh auth login

# Or use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/samplemind-ai-v2-phoenix.git
```

### Issue: "fatal: refusing to merge unrelated histories"

**Solution:**
```bash
git pull origin main --allow-unrelated-histories
```

### Issue: Large files rejected by GitHub

**Solution:**
```bash
# Check file sizes
find . -type f -size +50M

# Add large files to .gitignore
echo "path/to/large/file" >> .gitignore

# Remove from staging
git rm --cached path/to/large/file

# Commit and push
git commit -m "chore: remove large files"
git push
```

### Issue: Git says "already exists"

**Solution:**
```bash
# If repository name already exists, use different name
gh repo create samplemind-ai-phoenix-v2 --private ...

# Or delete existing and recreate
gh repo delete samplemind-ai-v2-phoenix
gh repo create samplemind-ai-v2-phoenix --private ...
```

---

## 📞 GitHub CLI Quick Reference

### Authentication

```bash
gh auth login              # Login to GitHub
gh auth status             # Check authentication status
gh auth logout             # Logout
```

### Repository Management

```bash
gh repo view               # View repository details
gh repo view --web         # Open repository in browser
gh repo edit               # Edit repository settings
gh repo clone              # Clone repository
gh repo delete             # Delete repository
```

### Pull Requests

```bash
gh pr create               # Create pull request
gh pr list                 # List pull requests
gh pr view 123             # View PR #123
gh pr checkout 123         # Check out PR #123
gh pr merge 123            # Merge PR #123
```

### Issues

```bash
gh issue create            # Create issue
gh issue list              # List issues
gh issue view 123          # View issue #123
gh issue close 123         # Close issue #123
```

---

## 🎯 Next Steps After Setup

Once your repository is set up:

1. **Continue Development**
   - Work on CLI enhancement
   - Build GUI application
   - Develop DAW plugins
   - Improve test coverage to 80-100%

2. **Branch Protection** (Optional for now)
   ```bash
   # Add branch protection to main
   gh api repos/:owner/:repo/branches/main/protection \
     --method PUT \
     --field required_pull_request_reviews[required_approving_review_count]=1
   ```

3. **Set Up GitHub Actions**
   - CI/CD workflows are already in `.github/workflows/`
   - They'll run automatically on push

4. **Regular Backups**
   ```bash
   # Clone to backup location
   git clone https://github.com/YOUR_USERNAME/samplemind-ai-v2-phoenix.git backup/
   ```

---

## 🔒 Keep It Private!

**REMINDER:** This repository is **PRIVATE** until:

- ✅ CLI enhancement complete
- ✅ GUI application complete
- ✅ DAW plugins complete
- ✅ Test coverage reaches 80-100%
- ✅ All quality gates passed

**When ready to go public:**

```bash
# Change visibility to public
gh repo edit --visibility public

# Or via web: Settings → Danger Zone → Change visibility
```

---

## 📚 Additional Resources

- **GitHub Docs:** https://docs.github.com
- **GitHub CLI Docs:** https://cli.github.com/manual
- **Git Docs:** https://git-scm.com/doc
- **Conventional Commits:** https://www.conventionalcommits.org

---

## ✅ Setup Complete!

Your repository is now ready for development! 🎉

**Current Status:**
- ✅ Repository: `samplemind-ai-v2-phoenix`
- ✅ Version: v2.0.0-beta
- ✅ Visibility: PRIVATE
- ✅ Branch: main
- ✅ Tag: v2.0.0-beta
- ✅ Commit: Initial release commit

**Stay mystical. The phoenix rises when ready!** 🔥🚀

---

*Last updated: December 2024*
*SampleMind AI v2.0 - Phoenix Beta Release*
