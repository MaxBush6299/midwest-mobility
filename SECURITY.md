# Security Policy

This is a demonstration project built on Microsoft Agent Framework, Azure AI
Foundry, and Azure SQL. It ships with a **fictional dataset** and is intended
for learning and demos, not production use. Even so, we take security reports
seriously and appreciate responsible disclosure.

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them privately through GitHub's built-in
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability):

1. Go to the repository's **Security** tab.
2. Click **Report a vulnerability**.
3. Provide as much detail as you can (see below).

If private reporting is unavailable, contact the maintainer directly rather
than opening a public issue.

## What to include

To help us triage quickly, please include:

- The type of issue (e.g., credential exposure, injection, insecure default).
- Affected file(s), script(s), or configuration.
- Steps to reproduce or a proof of concept.
- The potential impact.

## Scope notes

- The repository is designed to hold **no secrets**. Real credentials and
  endpoints belong only in a local, git-ignored `.env` file (see
  [`.env.example`](.env.example)). If you find a committed secret or a
  tenant-specific identifier, please report it.
- All Azure access uses Microsoft Entra ID via `DefaultAzureCredential` /
  `AzureCliCredential`; there are no SQL passwords or shared keys by design.

## Response

We will acknowledge your report, investigate, and keep you informed of
progress toward a fix. Thank you for helping keep this project and its users
safe.
