#!/bin/bash
# Create GitHub Milestones for SampleMind AI v6
# Repository: lchtangen/samplemind-ai-v2-phoenix

set -e

echo "🎯 Creating GitHub Milestones..."
echo ""

# Calculate due dates
WEEK_1=$(date -d "+1 week" +%Y-%m-%d)
WEEK_4=$(date -d "+4 weeks" +%Y-%m-%d)
WEEK_12=$(date -d "+12 weeks" +%Y-%m-%d)

echo "Milestone 1: Beta v0.6.0 (due: $WEEK_1)"
gh api repos/lchtangen/samplemind-ai-v2-phoenix/milestones \
  -f title="Beta v0.6.0" \
  -f state="open" \
  -f description="Initial beta release for testing

Goals:
- 75%+ tests passing
- Critical bugs fixed
- Documentation complete
- 5-10 beta testers recruited" \
  -f due_on="${WEEK_1}T23:59:59Z" 2>/dev/null || echo "Milestone may already exist"

echo "Milestone 2: Beta v0.7.0 (due: $WEEK_4)"
gh api repos/lchtangen/samplemind-ai-v2-phoenix/milestones \
  -f title="Beta v0.7.0" \
  -f state="open" \
  -f description="Improved beta with community feedback

Goals:
- 85%+ tests passing
- All critical bugs fixed
- Web UI alpha
- 20+ active beta testers
- Performance benchmarks met" \
  -f due_on="${WEEK_4}T23:59:59Z" 2>/dev/null || echo "Milestone may already exist"

echo "Milestone 3: v1.0.0 Release (due: $WEEK_12)"
gh api repos/lchtangen/samplemind-ai-v2-phoenix/milestones \
  -f title="v1.0.0 Release" \
  -f state="open" \
  -f description="Production release

Goals:
- 95%+ tests passing
- All features complete
- Production-ready
- Public launch
- Marketing campaign
- First 100 users" \
  -f due_on="${WEEK_12}T23:59:59Z" 2>/dev/null || echo "Milestone may already exist"

echo ""
echo "✅ All 3 milestones created successfully!"
echo ""
echo "View milestones at: https://github.com/lchtangen/samplemind-ai-v2-phoenix/milestones"
