# Repository Configuration

This directory contains configuration files for GitHub repository settings and workflows.

## Contents

### 1. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

A GitHub Actions workflow that runs on every push and pull request to the `main` branch. It includes:

- Node.js setup with pnpm
- Dependency installation
- Linting and type checking
- Testing
- Building the application
- Deployment (to be configured)

### 2. CODEOWNERS (`.github/CODEOWNERS`)

Defines the code owners for different parts of the repository. Currently, `@lchtangen` is set as the owner for all files. Update this file to include your team members as the project grows.

### 3. Branch Protection Rules (Script)

To set up branch protection rules for the `main` branch, run:

```bash
./scripts/setup-branch-protection.sh
```

This will configure the following protections:
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Require linear history
- Prevent force pushes
- Prevent branch deletion
- Require conversation resolution before merging

### 4. Required GitHub Secrets

For the CI/CD pipeline to work properly, make sure to set up the following GitHub secrets in your repository settings:

- `NPM_TOKEN` (for private package access, if needed)
- `VERCEL_TOKEN` (if deploying to Vercel)
- Any other environment-specific secrets

## Getting Started

1. Clone the repository
2. Install dependencies: `pnpm install`
3. Run the development server: `pnpm dev`

## Development Workflow

1. Create a new branch for your feature/fix
2. Make your changes and commit them
3. Push your branch and create a pull request
4. Request a review from the relevant code owners
5. Once approved, merge your pull request into `main`

## License

This project is licensed under the terms of the [MIT License](LICENSE).
