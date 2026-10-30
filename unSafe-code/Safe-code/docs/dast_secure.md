# OWASP ZAP DAST – Secure Django Application

## Overview

This document describes a **Dynamic Application Security Testing (DAST)** scan performed on the **secure version** of a Django web application using **OWASP ZAP**.  
The scan was executed using an **automated black-box testing** approach against a running application, without access to the source code.

---

## Tool Information

- **Tool:** OWASP ZAP  
- **Testing Type:** DAST (Black-Box)  
- **Scan Mode:** Automated Scan  
- **Target Framework:** Django  

---

## Scan Scope

### Target Application
Secure Django Web Application

### Target URL
```
http://127.0.0.1:8000
```

### Scope Rules
- Scan limited to application-owned endpoints
- External and third-party domains excluded
- Scope restricted to base application URL

---

## Security Baseline (Secure Configuration)

The secure version of the application applies OWASP Top 10 aligned security controls:

- Authentication and authorization enforced  
- CSRF protection enabled  
- Secure session and cookie attributes  
- HTTP security headers configured  
- Input validation and output encoding  
- Debug mode disabled  

---

## Scan Execution

### Scan Types

- **Unauthenticated Automated Scan**
- **Authenticated Automated Scan** (session-based authentication)

### Automated Workflow

1. OWASP ZAP configured as an intercepting proxy  
2. Initial manual interaction to establish application context  
3. Automated **Spider Scan** for endpoint discovery  
4. Automated **Active Scan** for vulnerability detection  

---

## Results Summary

- No high or critical severity vulnerabilities detected  
- Findings limited to low-risk or informational alerts  
- Secure configuration significantly reduced the attack surface  

---

## Output Artifacts

### Raw ZAP Output
```
data/raw/dast_zap_secure.json
```

### Unified JSON Outputs
```
data/unified/dast_secure_unified_clean.json
```

---

## Unified JSON Finding Template

```json
[
  {
    "id": "D-SEC-001",
    "name": "Missing Security Header",
    "location": "GET /",
    "source": "DAST",
    "tool": "OWASP ZAP",
    "severity": "Low",
    "risk": 20,
    "evidence": "ZAP alert: X-Frame-Options header not set",
    "explain": "Missing security headers may expose the application to browser-based attacks such as clickjacking.",
    "fix": "Enable the required security headers using Django middleware or web server configuration.",
    "tags": ["OWASP A05: Security Misconfiguration", "CWE-693"]
  }
]
```

---

## Notes

- DAST scans only reachable endpoints  
- Automated results may require manual verification  
- DAST complements SAST and AI-based static analysis  
