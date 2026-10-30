# Research Baseline Version — `Safe-code`

> **Before retesting:** This README documents the research context and is not an assessment input. Delete `README.md` from the test copy before providing the project to an AI tool or repeating the assessment. Describing a version as safe or explaining its security controls can influence the tool's expectations and bias its findings. Do not include this file in the assessment inputs, context, or conversation.

## Branch Purpose

The `Safe-code` branch contains the security-focused baseline of MyStore, a Django e-commerce application used in this research. It provides a separate test subject for evaluating security assessment tools against a version with security controls in place.

The `unSafe-code` branch serves a different experimental purpose: it contains manually injected vulnerabilities. Each version must be assessed and documented independently so that findings remain attributable to the code actually tested.

The name `Safe-code` identifies this branch's role in the experiment; it does not certify that the application is free of vulnerabilities. Findings still require verification, and an absence of reported issues is not proof of security.

## Research Objective

This version supports comparison across three assessment approaches:

- **Static Application Security Testing (SAST):** Examining source code for potentially insecure patterns and practices.
- **Dynamic Application Security Testing (DAST):** Assessing the running application through requests, responses, and observable behavior.
- **AI-assisted security assessment (AI):** Analyzing the project using the inputs and instructions defined for the experiment, and evaluating the relevance and accuracy of the findings.

Assessment results should be reviewed against the research reference for this specific version. Evaluation should account for confirmed findings, false positives, and missed issues where independently established, as well as differences in scope and visibility between the approaches. Do not assume that this branch has no real vulnerabilities or classify every alert as a false positive because of its name.

## Application and Security Controls

MyStore includes user accounts, product browsing, a shopping cart, orders, and an administrative dashboard. The application uses Django, SQLite, Argon2 password hashing, Bleach, and Pillow.

The current configuration includes:

- A required `DJANGO_SECRET_KEY` environment variable.
- Environment-based debug and allowed-host settings.
- Django CSRF middleware and password validators.
- Argon2 as the preferred password hasher.
- HTTPS redirects and secure session and CSRF cookies when debug mode is disabled.
- Browser security headers, including frame restrictions and content-type protection.

These controls describe the checked-in configuration. Their effectiveness depends on the application code, runtime environment, and deployment settings, and must be assessed within the experiment's scope.

## Branch Independence

Each branch represents a separate research stage or process. Preserve `Safe-code` as an independent experimental version.

Do not merge this branch into `main`, `unSafe-code`, or any other branch. Do not import changes from other branches while repeating the same experiment. If a new experiment requires changes, document them and record the exact commit used so that its results can be distinguished from earlier results.

## Retesting and Preventing Information Leakage

This README explains the experimental context and security configuration. Giving that information to an AI assessment tool can create expectations about what it should or should not find, affecting the independence of the assessment.

To repeat the experiment:

1. Prepare a test copy of the `Safe-code` branch and record the commit being evaluated.
2. Delete this file (`README.md`) from the test copy before making it available to the tool. Keep research documentation outside the files accessible to the assessment tool.
3. Exclude previous assessment results, expected findings, ground-truth annotations, and documentation that reveals the intended security status. Deleting this README alone is insufficient if that information remains available elsewhere in the inputs or context.
4. Use the documented instructions, scope, and tool settings. Keep the runtime environment and synthetic test data consistent across comparable runs, and record any required differences between versions.
5. Save the tool's outputs before evaluating them against the research reference outside the assessment tool's context.

These steps help keep the comparison focused on what each tool can establish from the permitted inputs and support reproducible results.
