# Phase 14: Analytics & Monitoring Configuration

**Date**: February 4, 2026
**Purpose**: Comprehensive guide to setting up PostHog analytics for SampleMind AI beta testing
**Status**: Ready to implement

---

## Overview

This guide covers the complete analytics setup for Phase 14 beta testing, including PostHog configuration, event tracking, dashboards, and monitoring.

---

## 1. PostHog Setup

### Step 1: Create PostHog Account

1. Go to https://posthog.com/signup
2. Sign up with email (free tier includes 1M events/month)
3. Create new project: "SampleMind AI Beta"
4. Copy API key from project settings

### Step 2: Configure Environment Variables

Add to `.env.local` (development) and `.env.production`:

```env
# PostHog Configuration
NEXT_PUBLIC_POSTHOG_KEY=phc_your_api_key_here
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_POSTHOG_DEBUG=false

# Session recording
POSTHOG_CAPTURE_RATE=1.0
POSTHOG_AUTOCAPTURE=true
```

### Step 3: Verify Installation

PostHog should auto-capture:
- Page views
- Clicks and form interactions
- Custom events via `posthog.capture()`
- Session recordings (if enabled)

---

## 2. Event Tracking

### Tracked Events

#### Upload Events
```python
posthog.capture('audio_uploaded', {
    'file_size_mb': 45.2,
    'format': 'wav',
    'duration_seconds': 180,
    'timestamp': datetime.now().isoformat()
})

posthog.capture('batch_upload_started', {
    'file_count': 10,
    'total_size_mb': 452
})

posthog.capture('batch_upload_completed', {
    'file_count': 10,
    'success_count': 9,
    'failed_count': 1,
    'success_rate': 0.9
})
```

#### Analysis Events
```python
posthog.capture('analysis_started', {
    'analysis_level': 'STANDARD',
    'file_size_mb': 45.2
})

posthog.capture('analysis_completed', {
    'analysis_level': 'STANDARD',
    'duration_ms': 1250,
    'confidence_score': 0.92,
    'success': True
})

posthog.capture('analysis_failed', {
    'error_type': 'InvalidAudioFormat',
    'error_message': 'File is not a valid WAV',
    'analysis_level': 'STANDARD'
})
```

#### Search Events
```python
posthog.capture('similar_samples_found', {
    'query_type': 'audio_similarity',
    'result_count': 10,
    'search_time_ms': 125,
    'top_similarity_score': 0.95
})

posthog.capture('semantic_search_performed', {
    'query': 'fast dance track',
    'query_length': 15,
    'result_count': 10,
    'search_time_ms': 200
})

posthog.capture('library_search_performed', {
    'search_type': 'library',
    'filter_count': 3,
    'result_count': 42
})
```

#### Feature Usage Events
```python
posthog.capture('effect_applied', {
    'effect_type': 'reverb',
    'preset_name': 'Large Hall',
    'duration_ms': 2500
})

posthog.capture('midi_generated', {
    'source_format': 'wav',
    'midi_type': 'melody',
    'note_count': 24,
    'confidence': 0.87
})

posthog.capture('command_palette_opened', {
    'source': 'keyboard_shortcut'  # or 'menu_click'
})

posthog.capture('onboarding_completed', {
    'steps_completed': 5,
    'total_steps': 5,
    'duration_seconds': 180
})
```

#### User Events
```python
posthog.capture('feedback_submitted', {
    'category': 'bug',  # or 'feature', 'praise', 'other'
    'rating': 4,
    'message_length': 250
})

posthog.capture('file_downloaded', {
    'file_type': 'analysis_result',  # or 'midi', 'project'
    'format': 'json'
})

posthog.capture('results_exported', {
    'export_format': 'csv',  # or 'json', 'pdf'
    'item_count': 150
})
```

---

## 3. PostHog Dashboard Setup

### Create Dashboard: "SampleMind AI Beta"

#### Dashboard 1: Overview

**Top Events (Last 7 Days)**
- Filter: Event Name contains "analysis", "upload", "search"
- Shows: Event count, trend line
- Purpose: See main feature usage

**User Funnel**
1. audio_uploaded
2. analysis_started
3. analysis_completed
4. similar_samples_found

**Success Rate Metrics**
- analysis_completed / analysis_started
- batch_upload_completed success_count / file_count
- library_search_performed result_count > 0

#### Dashboard 2: Engagement

**Daily Active Users (DAU)**
- Filter: Any event
- Breakdown: By date
- Target: Growth trend

**Feature Adoption**
- analysis_started
- similar_samples_found
- midi_generated
- effect_applied
- command_palette_opened

**Session Duration**
- Median: Should be 10-30 minutes for engaged users
- Target: Increasing over time

#### Dashboard 3: Performance

**Analysis Duration**
- analysis_completed → duration_ms
- Breakdown: By analysis_level
- Target: BASIC <500ms, STANDARD <1500ms, DETAILED <3000ms

**Search Performance**
- similar_samples_found → search_time_ms
- semantic_search_performed → search_time_ms
- Target: <200ms

**Success Rates**
- analysis_completed success rate
- batch_upload success rate
- Feature completion rates

#### Dashboard 4: Issues & Quality

**Error Events**
- analysis_failed count
- Error breakdown by type
- Trend over time
- Target: Decreasing

**Failed Uploads**
- batch_upload_completed failed_count
- Error types
- Correlation with file types/sizes

---

## 4. Alerts Configuration

### Alert 1: High Error Rate

```
Condition: (analysis_failed count) / (analysis_started count) > 0.05
Frequency: Check every 1 hour
Action: Email team + Slack notification
```

### Alert 2: Performance Degradation

```
Condition: analysis_completed duration_ms > 3000 (for STANDARD level)
Frequency: Check every 30 minutes
Action: Email team
```

### Alert 3: Low Engagement

```
Condition: DAU drops 20% from previous day
Frequency: Check daily
Action: Slack notification
```

### Alert 4: Upload Failures

```
Condition: (batch_upload_completed failed_count) / (file_count) > 0.1
Frequency: Check every 1 hour
Action: Email team
```

---

## 5. Privacy Considerations

### Data Minimization

- Only track essential metrics
- No audio file contents tracked
- No personally identifiable information (PII)
- No recording of sensitive keyboard input

### User Opt-Out

Settings > Privacy:
```
[x] Enable analytics and performance tracking
[x] Allow session recordings for debugging
```

### GDPR Compliance

- Respect `navigator.doNotTrack`
- Include privacy policy link
- Clear data retention: 90 days
- User data export capability

---

## 6. Event Implementation Examples

### In React Component

```typescript
// apps/web/src/components/AnalysisPanel.tsx
import { usePostHog } from 'posthog-js/react'

export function AnalysisPanel() {
  const posthog = usePostHog()

  const handleAnalyze = async (file: File) => {
    posthog.capture('analysis_started', {
      analysis_level: 'STANDARD',
      file_size_mb: file.size / (1024 * 1024)
    })

    try {
      const result = await api.analyze(file)

      posthog.capture('analysis_completed', {
        analysis_level: 'STANDARD',
        duration_ms: result.analysis_time_ms,
        confidence_score: result.confidence,
        success: true
      })

      // Display results
    } catch (error) {
      posthog.capture('analysis_failed', {
        error_type: error.type,
        error_message: error.message,
        analysis_level: 'STANDARD'
      })
    }
  }

  return (
    <button onClick={() => handleAnalyze(file)}>
      Analyze Audio
    </button>
  )
}
```

### In Python Backend

```python
# plugins/ableton/python_backend.py
from posthog import Posthog

posthog = Posthog(
    api_key=os.getenv('POSTHOG_API_KEY'),
    host='https://app.posthog.com'
)

@app.post('/api/analyze')
async def analyze_audio(request: AnalysisRequest):
    posthog.capture('analysis_started', {
        'analysis_level': request.analysis_level,
        'timestamp': datetime.now().isoformat()
    })

    try:
        result = await engine.analyze(request.file_path, request.analysis_level)

        posthog.capture('analysis_completed', {
            'analysis_level': request.analysis_level,
            'duration_ms': result.analysis_time_ms,
            'confidence': result.confidence,
            'success': True
        })

        return result

    except Exception as e:
        posthog.capture('analysis_failed', {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'analysis_level': request.analysis_level
        })
        raise
```

---

## 7. Testing Analytics

### Check Events Are Captured

1. Open PostHog dashboard
2. Go to "Insights" → "Events"
3. Filter for recent events
4. Verify events appear with correct properties

### Session Recording Verification

1. Start session recording
2. Use app normally
3. Check PostHog for session video
4. Verify user interactions are captured

---

## 8. Key Metrics to Monitor

### Beta Testing Metrics

| Metric | Target | Frequency |
|--------|--------|-----------|
| Daily Active Users (DAU) | 50+ | Daily |
| Analysis Operations/Day | 100+ | Daily |
| Feature Adoption Rate | >60% | Weekly |
| User Retention (Day 7) | >40% | Weekly |
| Feedback Submissions | 5+ | Daily |

### Performance Metrics

| Metric | Target | Frequency |
|--------|--------|-----------|
| Analysis Duration (STANDARD) | <1500ms | Real-time |
| Search Duration | <200ms | Real-time |
| Error Rate | <5% | Hourly |
| Success Rate | >95% | Hourly |

### Engagement Metrics

| Metric | Target | Frequency |
|--------|--------|-----------|
| Avg Session Duration | 10-30min | Daily |
| Command Palette Usage | >30% | Weekly |
| Feature Completion Rate | >70% | Weekly |
| Onboarding Completion | >80% | Weekly |

---

## 9. Weekly Review Process

### Monday: Data Review

1. Check DAU trend
2. Review error rates
3. Analyze feature adoption
4. Check performance metrics

### Wednesday: Engagement Review

1. User feedback analysis
2. Session recording review
3. Funnel analysis
4. Pain point identification

### Friday: Planning

1. Prioritize fixes based on data
2. Plan feature improvements
3. Identify optimizations
4. Set next week targets

---

## 10. Troubleshooting

### Events Not Appearing

- Verify API key is correct
- Check network requests in browser DevTools
- Ensure `posthog.capture()` is being called
- Check PostHog debug mode: `NEXT_PUBLIC_POSTHOG_DEBUG=true`

### High Event Volume

- Consider reducing `POSTHOG_CAPTURE_RATE`
- Disable session recordings if not needed
- Filter autocapture events

### Privacy Concerns

- Review event properties for sensitive data
- Implement data anonymization
- Respect Do Not Track header
- Document data retention policy

---

## References

- PostHog Docs: https://posthog.com/docs
- Event Tracking Best Practices: https://posthog.com/docs/integrate/event-tracking
- Privacy Guide: https://posthog.com/docs/privacy
- React Integration: https://posthog.com/docs/libraries/react

---

**Status**: Ready for implementation
**Next Steps**:
1. Create PostHog account
2. Add API key to .env files
3. Implement event tracking in components
4. Create dashboards
5. Set up alerts
