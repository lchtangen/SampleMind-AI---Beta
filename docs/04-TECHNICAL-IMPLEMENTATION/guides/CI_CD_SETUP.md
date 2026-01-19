# 🚀 CI/CD Pipeline Setup Guide

This document provides a comprehensive guide to the SampleMind AI CI/CD pipeline, including setup instructions, workflow details, and best practices.

## 📋 Overview

Our CI/CD pipeline is built using GitHub Actions and includes the following key components:

1. **Testing** - Automated testing with PostgreSQL integration
2. **Building** - Docker image building and caching
3. **Deployment** - Staging and production deployments
4. **Notification** - Status updates via Slack

## 🛠️ Prerequisites

Before setting up the CI/CD pipeline, ensure you have:

- A GitHub repository for your project
- Docker Hub account (for container registry)
- Access to your deployment servers (staging/production)
- Slack workspace (for notifications)

## 🔐 Required Secrets

Add these secrets to your GitHub repository (Settings > Secrets > Actions):

| Secret Name | Description |
|-------------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `STAGING_SSH_PRIVATE_KEY` | SSH key for staging server access |
| `PROD_SSH_PRIVATE_KEY` | SSH key for production server access |
| `SLACK_WEBHOOK_URL` | Webhook URL for Slack notifications |

## 🏗️ Pipeline Workflow

### 1. Test
- **Runs on:** Every push and pull request
- **Environment:** Ubuntu with PostgreSQL service
- **Steps:**
  - Set up Python 3.10
  - Install dependencies
  - Run database migrations
  - Execute tests with coverage
  - Upload coverage to Codecov

### 2. Build
- **Runs on:** Push to main/develop branches
- **Dependencies:** Test job must pass
- **Steps:**
  - Set up Docker Buildx
  - Log in to Docker Hub
  - Build and push Docker images

### 3. Deploy to Staging
- **Runs on:** Push to develop branch
- **Environment:** staging
- **Steps:**
  - Checkout code
  - Set up SSH key
  - Deploy to staging server

### 4. Deploy to Production
- **Runs on:** Push to main branch
- **Environment:** production
- **Steps:**
  - Checkout code
  - Set up SSH key
  - Deploy to production server

## 🚦 Environment Variables

### PostgreSQL Configuration
```env
POSTGRES_DB=test_samplemind
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

## 🔄 Manual Triggers

You can manually trigger the workflow from the Actions tab in your GitHub repository. Available workflows:

- **Full CI/CD Pipeline** - Runs all jobs
- **Test Only** - Runs only the test suite
- **Deploy Staging** - Deploys to staging environment
- **Deploy Production** - Deploys to production environment

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Verify PostgreSQL service is running
   - Check connection strings and credentials
   - Ensure ports are properly exposed

2. **Docker Build Failures**
   - Check Dockerfile for syntax errors
   - Verify build context and paths
   - Ensure all required files are included in the repository

3. **Deployment Issues**
   - Verify SSH keys have proper permissions
   - Check server logs for errors
   - Ensure deployment scripts are executable

## 📈 Monitoring

- **Test Coverage:** View coverage reports on Codecov
- **Build Status:** Check GitHub Actions workflow runs
- **Deployment Logs:** Available in GitHub Actions and server logs

## 🔒 Security

- **Secrets Management:** All sensitive data is stored in GitHub Secrets
- **Dependency Scanning:** Dependencies are automatically scanned for vulnerabilities
- **Code Scanning:** Static code analysis runs on every push

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Slack API Documentation](https://api.slack.com/)
