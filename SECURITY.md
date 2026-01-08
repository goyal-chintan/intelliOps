# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in OpsPilot, please report it
**privately** rather than opening a public issue.

### How to Report

1. **Preferred**: Open a **GitHub Security Advisory** for this repository (private by default).
2. **If you cannot use advisories**: contact the maintainers privately (do not share exploit details in issues).
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Resolution timeline**: Depends on severity; we aim for 30–90 days for most issues

We appreciate responsible disclosure and will credit reporters in release notes
(unless you prefer to remain anonymous).

## Scope

This policy covers the OpsPilot codebase, including:

- Python AI services (`level_zero/`, `multi-tenant/`)
- Configuration and infrastructure code
- Sample datasets (if they inadvertently contain sensitive patterns)

Third-party dependencies are out of scope, but we welcome reports if you find
a vulnerable dependency we should update.
