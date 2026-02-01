---
description: Security audit workflow. OWASP checks, dependency scanning, code review for vulnerabilities.
---

# /security-audit - Security Audit Workflow

Comprehensive security review for applications.

## Steps

### 1. Scope Definition
Ask the user:
- What type of application? (web, API, mobile)
- What's the deployment environment?
- Any compliance requirements? (PCI, HIPAA, SOC2)

### 2. Dependency Scanning
```bash
# JavaScript/Node.js
npm audit
npx snyk test

# Python
pip-audit
safety check

# Check for outdated packages
npm outdated
pip list --outdated
```

### 3. Static Analysis Security Testing (SAST)
```bash
# JavaScript/TypeScript
npx eslint --plugin security src/

# Python
bandit -r src/

# Generic secrets scanner
gitleaks detect --source .
```

### 4. OWASP Top 10 Review

Check for:

| # | Vulnerability | What to Look For |
|---|---------------|------------------|
| 1 | Broken Access Control | Missing auth checks, IDOR |
| 2 | Cryptographic Failures | Weak encryption, exposed secrets |
| 3 | Injection | SQL, NoSQL, Command injection |
| 4 | Insecure Design | Missing threat modeling |
| 5 | Security Misconfiguration | Debug mode, default creds |
| 6 | Vulnerable Components | Outdated dependencies |
| 7 | Auth Failures | Weak passwords, session issues |
| 8 | Data Integrity Failures | Unsigned updates, deserialize |
| 9 | Logging Failures | Missing audit logs |
| 10 | SSRF | Unvalidated URLs |

### 5. Code Review Focus Areas

**Authentication:**
- Password hashing (bcrypt, argon2)
- Session management
- JWT validation
- MFA implementation

**Authorization:**
- Role-based access control
- Resource ownership validation
- API endpoint protection

**Input Validation:**
- Sanitization of user input
- Parameterized queries
- File upload restrictions

**Output Encoding:**
- XSS prevention
- Content-Type headers
- CSP headers

### 6. Generate Report

Create security report with:
- Executive summary
- Critical findings (fix immediately)
- High findings (fix within sprint)
- Medium findings (fix within quarter)
- Low findings (backlog)
- Recommendations

### 7. Remediation Tracking

Create issues for each finding:
```markdown
## Security Issue: [Title]

**Severity:** Critical/High/Medium/Low
**Location:** [file:line]
**Description:** [what's wrong]
**Recommendation:** [how to fix]
**References:** [OWASP, CWE links]
```

## Security Checklist

- [ ] Dependencies up to date
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] Auth/authz properly enforced
- [ ] HTTPS enforced
- [ ] Security headers set
- [ ] Logging in place
- [ ] Error messages don't leak info
