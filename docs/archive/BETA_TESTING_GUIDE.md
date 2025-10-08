# 🎵 SampleMind AI - Beta Testing Guide

Welcome beta testers! This guide helps you test all features effectively.

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/samplemind-ai.git
cd samplemind-ai
pip install -r requirements-optimized.txt
cp .env.example .env
# Add your API keys to .env
```

## 🧪 Testing Checklist

### CLI Commands
- [ ] `samplemind version`
- [ ] `samplemind analyze [file]`
- [ ] `samplemind stems separate [file]`
- [ ] `samplemind midi convert [file]`
- [ ] `samplemind generate music --prompt "test"`

### Web API (http://localhost:8000/docs)
- [ ] POST `/api/v1/audio/upload`
- [ ] POST `/api/v1/audio/analyze/{file_id}`
- [ ] POST `/api/v1/generate/music`
- [ ] POST `/api/v1/vector/search/similar`

### Performance
- [ ] Audio analysis < 5sec for 10MB files
- [ ] API health check < 100ms
- [ ] Batch processing 10 files successfully

## 🐛 Bug Reporting

File issues at: https://github.com/YOUR_USERNAME/samplemind-ai/issues

Include:
1. Steps to reproduce
2. Expected vs actual behavior
3. System info (OS, Python version)
4. Error logs

## 📊 Feature Feedback

Share what works and what needs improvement!

**Thank you for testing! 🎉**

Version: v2.0.0-beta | Date: 2025-10-04
