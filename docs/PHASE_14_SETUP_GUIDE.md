# Phase 14 Beta Testing Infrastructure Setup Guide

**Target Date:** February 3-10, 2026
**Status:** In Progress
**Last Updated:** February 3, 2026

## Overview

This guide provides step-by-step instructions to set up all Phase 14 beta testing infrastructure, including GitHub issues, discussions, analytics, and monitoring.

---

## 1. GitHub Issue Templates Setup ✅

**Status:** COMPLETE (`.github/ISSUE_TEMPLATE/` directory)

### What Was Created

1. **bug_report.yml** - Structured bug reporting form
   - Includes reproduction steps, expected vs actual behavior
   - Platform/environment dropdown
   - Version tracking
   - Screenshot/video upload fields
   - Error logs section

2. **feature_request.yml** - Feature request template
   - Problem statement section
   - Proposed solution
   - Use case description
   - Category dropdown (11 categories)
   - Priority levels

3. **beta_feedback.yml** - Beta tester feedback template
   - Overall rating (1-5 stars)
   - What works well / what needs improvement
   - Workflow description
   - Feature requests
   - Recommendation likelihood
   - Platform preference (CLI vs Web)

4. **config.yml** - Issue template configuration
   - Disables blank issues
   - Provides contact links to docs and Discord

### How to Verify

```bash
# Check if templates are visible on GitHub
# Go to: https://github.com/samplemind/samplemind-ai/issues/new/choose

# Should see 3 templates:
# - Bug Report
# - Feature Request
# - Beta Feedback
```

---

## 2. GitHub Discussions Setup

### Manual Setup Required

Since Discussions require manual GitHub UI configuration, follow these steps:

#### Step 1: Enable Discussions
1. Go to repository Settings
2. Find "Features" section
3. Check "Discussions" checkbox
4. Save settings

#### Step 2: Create Discussion Categories

Create these 6 categories in order:

1. **📣 Announcements** (read-only for team, discussion disabled)
   - Description: "Major updates and release announcements"

2. **💬 General Discussion**
   - Description: "General chat, off-topic conversations, introductions"

3. **💡 Ideas & Feature Requests**
   - Description: "Share product ideas and vote on requested features"
   - **Enable as Voting:** Yes

4. **🙏 Q&A** (Special: Use "Question" category type if available)
   - Description: "Ask questions and get answers from community"
   - **Enable as Q&A:** Yes

5. **🎨 Show & Tell**
   - Description: "Share your music, workflows, or projects using SampleMind AI"

6. **🐛 Troubleshooting**
   - Description: "Need help? Debug issues with the community's help"

#### Step 3: Pin Welcome Message

Create discussion in Announcements:

```markdown
# Welcome to SampleMind AI Beta! 🎉

Thank you for being part of our beta testing community! Here's how to get the most out of SampleMind AI:

## Quick Start
- [Installation Guide](/docs/PHASE_13_USER_QUICK_START.md)
- [FAQ](/docs/PHASE_13_FAQ.md)
- [Video Tutorials](https://youtube.com/@samplemindai)

## Report Issues
- Found a bug? [Report it here](https://github.com/samplemind/samplemind-ai/issues/new/choose)
- Feature idea? [Suggest it here](https://github.com/samplemind/samplemind-ai/issues/new?template=feature_request.yml)

## Get Help
- Technical questions? Ask in [Q&A](https://github.com/samplemind/samplemind-ai/discussions/categories/q-a)
- Join our Discord community: [Discord Invite](https://discord.gg/samplemind)

## Community Guidelines
- Be respectful and constructive
- Search before posting (avoid duplicates)
- Share your workflows and feedback!
- Help others when you can

Happy analyzing! 🎵
```

---

## 3. Environment Variables Setup

### For PostHog Analytics

Add to `.env.local` (development) and `.env.production`:

```env
# PostHog Configuration
# Get API key from https://posthog.com/signup
NEXT_PUBLIC_POSTHOG_KEY=phc_your_api_key_here
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
# Set to "true" in development to enable tracking for testing
NEXT_PUBLIC_POSTHOG_DEBUG=false
```

### PostHog Setup Steps

1. **Sign Up** at https://posthog.com/signup (free tier available)
2. **Get API Key** from project settings
3. **Create Dashboard** with these events:
   - audio_uploaded
   - analysis_completed
   - similar_samples_found
   - effect_applied
   - command_palette_opened
   - onboarding_completed
4. **Set Up Alerts** for:
   - Error events (severity: high)
   - Failed analyses
   - API performance degradation

---

## 4. Analytics Integration

### What's Tracked

#### Upload Tracking
- `audio_uploaded` - File size, format, duration
- `batch_upload_started` - File count, total size
- `batch_upload_completed` - Success/failure rates

#### Analysis Tracking
- `analysis_started` - Analysis level (BASIC, STANDARD, DETAILED, PROFESSIONAL)
- `analysis_completed` - Duration, confidence score
- `analysis_failed` - Error type

#### Search Tracking
- `similar_samples_found` - Query, result count, duration
- `semantic_search_performed` - Query type, length
- `library_search_performed` - Result count

#### Feature Usage
- `effect_applied` - Effect type, preset used
- `midi_generated` - Source format, MIDI type
- `command_palette_opened` - (no parameters)
- `onboarding_completed` - Steps completed, total steps

#### User Events
- `feedback_submitted` - Category, rating
- `file_downloaded` - File type
- `results_exported` - Export format

### Privacy Considerations

All tracking respects:
- `navigator.doNotTrack` browser setting
- User opt-out preference (in Settings)
- GDPR compliance (no personally identifiable information tracked)
- Data minimization (only essential metrics)

---

## 5. Feedback Widget Integration ✅

### What Was Created

Component: `apps/web/src/components/feedback/FeedbackWidget.tsx`

Features:
- Fixed button in bottom-right corner
- Modal form with:
  - 1-5 star rating
  - Category dropdown (Bug, Feature, Praise, Other)
  - Feedback message textarea
  - Optional email field
- Submits directly to GitHub Issues API
- Posts with `beta-feedback` label
- Tracks submission via PostHog

### How It Works

1. User clicks feedback button
2. Modal opens with form
3. User fills out form and clicks "Send Feedback"
4. Widget creates GitHub issue with:
   - Title: "Feedback: [category] - [rating]/5 stars"
   - Body: Includes category, rating, email, message, timestamp
   - Labels: `beta-feedback`, `feedback`
5. Success notification shown
6. Event tracked in PostHog

### Usage Example

Users will see:
- Floating button labeled "?" with message icon
- Click to open feedback form
- Fill out and submit
- GitHub issue created automatically

---

## 6. Command Palette Integration ✅

### What Was Integrated

- Root layout (`apps/web/app/layout.tsx`)
- Dynamic import with `ssr: false`
- Global Cmd+K (macOS) / Ctrl+K (Windows/Linux) shortcut
- Available on all pages

### Functionality

Users can:
- Open palette: `Cmd+K` or `Ctrl+K`
- Search commands, pages, settings
- Navigate quickly
- Track usage in PostHog

---

## 7. Monitoring & Metrics

### Key Metrics to Track

**Beta Testing Metrics:**
- [ ] Total beta signups: Target 100+
- [ ] Daily active users (DAU)
- [ ] Feature adoption rate
- [ ] Analysis average duration
- [ ] Search success rate
- [ ] Error rate

**GitHub Metrics:**
- [ ] Issues created (bugs, features, feedback)
- [ ] Discussion threads started
- [ ] Q&A questions answered
- [ ] Average response time

**Analytics Metrics:**
- [ ] Session duration
- [ ] Feature usage distribution
- [ ] Onboarding completion rate
- [ ] Feedback submission rate
- [ ] Command palette usage

### Creating PostHog Dashboard

1. Go to PostHog project
2. Create new dashboard: "SampleMind AI Beta"
3. Add these insights:

```
Top Events (7-day)
- Filter: Event Name contains "analysis", "upload", "search"
- Shows: Event count, trend

User Funnel
- 1. audio_uploaded
- 2. analysis_started
- 3. analysis_completed
- 4. similar_samples_found

Retention Cohorts
- Cohort: audio_uploaded in last 7 days
- Retention: 1, 7, 14, 30 days

Conversion: Onboarding
- analysis_started → analysis_completed (% success)
```

---

## 8. Email Setup

### For Beta Onboarding Email

Using SendGrid or similar service:

**Template:** `docs/marketing/beta-onboarding-email.md`

**Variables:**
- {{USER_NAME}}
- {{BETA_START_DATE}}
- {{BETA_DURATION}}
- {{BETA_TESTER_COUNT}}

**Send Configuration:**
- Trigger: When user submits beta signup form
- Subject: "Welcome to SampleMind AI Beta! 🚀"
- From: beta@samplemind.ai
- Reply-to: support@samplemind.ai

---

## 9. Verification Checklist

### GitHub Setup
- [ ] Bug report template works
- [ ] Feature request template works
- [ ] Beta feedback template works
- [ ] All 6 Discussions categories created
- [ ] Welcome announcement pinned
- [ ] Issue templates link to Discord

### Analytics Setup
- [ ] PostHog account created
- [ ] API key configured in `.env`
- [ ] Events firing (check PostHog dashboard)
- [ ] Dashboard created with key metrics
- [ ] Privacy policy updated to mention analytics

### Feature Integration
- [ ] CommandPalette opens with Cmd+K
- [ ] FeedbackWidget button visible in bottom-right
- [ ] Feedback form submits to GitHub Issues
- [ ] Events tracked in PostHog

### Email Setup
- [ ] SendGrid (or alternative) configured
- [ ] Beta onboarding email template created
- [ ] Test email sent successfully
- [ ] Unsubscribe links working

---

## 10. Going Live Checklist (Feb 10, 2026)

**Launch Day:**
- [ ] GitHub issue templates enabled
- [ ] GitHub Discussions categories live
- [ ] PostHog tracking verified
- [ ] FeedbackWidget functional
- [ ] CommandPalette working
- [ ] Beta signup page live
- [ ] Welcome email sent to first batch
- [ ] Discord server created and populated
- [ ] Announcement posted on Twitter/X, Reddit
- [ ] Team on standby for issues

---

## Support & Troubleshooting

### Issue: PostHog Events Not Appearing

**Solution:**
```bash
# Check environment variable is set
echo $NEXT_PUBLIC_POSTHOG_KEY

# Check in browser console
# Type: window.posthog
# Should show PostHog object

# Disable doNotTrack for testing
# Chrome DevTools > Settings > Privacy > uncheck "Respect user's choice"
```

### Issue: GitHub Issue Creation Failing

**Causes:**
1. API rate limit exceeded (60 requests/hour unauthenticated)
2. Invalid GitHub token
3. Repository not accessible

**Solution:**
- Use GitHub personal access token instead of anonymous API
- Implement rate limiting on client side
- Fall back to Discord webhook if GitHub API fails

### Issue: FeedbackWidget Button Not Visible

**Causes:**
1. CSS z-index conflict
2. Component not mounted
3. Dynamic import failing

**Solution:**
```typescript
// Check in browser console
console.log(window.posthog) // Should exist
// Check React DevTools for FeedbackWidget component

// Force reload: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

---

## Next Steps (Phase 14.3)

1. Create marketing assets (logos, screenshots, social media content)
2. Write 3 video scripts
3. Prepare Product Hunt launch kit
4. Create 30-day social media calendar
5. Design beta signup landing page

---

## Rollback Plan

If issues occur before launch:

1. **Disable Analytics:** Set `NEXT_PUBLIC_POSTHOG_KEY` to empty string
2. **Hide Feedback Widget:** Comment out FeedbackWidget in layout
3. **Revert GitHub Templates:** Delete `.github/ISSUE_TEMPLATE/` directory
4. **Disable Discussions:** Uncheck in repository settings

---

## Resources

- **PostHog Docs:** https://posthog.com/docs
- **GitHub Discussions:** https://docs.github.com/en/discussions
- **GitHub Issues:** https://docs.github.com/en/issues
- **SampleMind Docs:** `/docs/`
- **Community Links:**
  - Discord: https://discord.gg/samplemind
  - GitHub: https://github.com/samplemind/samplemind-ai

---

**Phase 14.2 Status:** ✅ INFRASTRUCTURE COMPLETE
**Ready for Launch:** February 10, 2026
**Next Phase:** 14.3 - Marketing Assets Creation
