# Semgrep (Web / Semgrep App) SAST CI Documentation for Django Applications

## 1. Overview

**Semgrep App (Web Version)** is a cloud-based Static Application Security Testing (SAST) platform that scans source code repositories directly through GitHub integration. It automatically runs security scans during CI workflows and provides vulnerability results through the Semgrep dashboard and GitHub security features.

This documentation explains how to configure and use **Semgrep App with GitHub CI** for scanning a **Django application**.

---

## 2. Architecture Overview

Semgrep App works using the following flow:

1. Django project is hosted in GitHub.
2. Semgrep App connects to the GitHub repository.
3. CI pipeline triggers Semgrep scans automatically.
4. Results are displayed in:
   - Semgrep Dashboard
   - GitHub Pull Requests
   - GitHub Security Tab (optional)

---

## 3. Prerequisites

Ensure the following requirements are met:

- Django application hosted on GitHub
- GitHub repository access permissions
- Semgrep account (https://semgrep.dev)
- GitHub Actions enabled
- CI permissions to run workflows

---

## 4. Connecting Semgrep App to GitHub

### 4.1 Sign in to Semgrep

1. Go to:

[text](https://semgrep.dev)

2. Sign in using GitHub authentication.

---

### 4.2 Install Semgrep GitHub Integration

1. Navigate to Semgrep Dashboard.
2. Click **Add Repository**.
3. Authorize GitHub access.
4. Select the project repository you want to test.
5. Confirm installation.

Semgrep will automatically:

- Create CI scanning workflows
- Start scanning pull requests
- Apply default security rules

---

## 5. Default Scanning Behavior

Once connected, Semgrep automatically scans:

- Pull Requests
- Commits
- Default branches 

The platform uses recommended rule packs including:

- Python security rules
- Django security rules
- OWASP Top 10 rules


