# Research Test Version — `unSafe-code`

> **Before retesting:** This README was written after the security assessment for documentation purposes. Delete `README.md` from the test copy before providing the project to an AI tool or repeating the assessment. Knowing that vulnerabilities were deliberately injected can guide the analysis, leak information about the experiment, and bias the results. Do not include this file in the tool's inputs, context, or conversation.

## Branch Purpose

The `unSafe-code` branch contains a Django e-commerce application prepared as an experimental subject for this research. Security vulnerabilities were manually injected into the source code to create deliberate test cases. This version was then used to test security assessment tools and compare their ability to identify vulnerabilities.

These vulnerabilities are intentional components of the experimental design. This version is intended for an isolated test environment with synthetic data, rather than production use.

## Research Objective

This branch provides a common test subject for three assessment approaches:

- **Static Application Security Testing (SAST):** Examining source code for patterns and practices that may introduce security vulnerabilities.
- **Dynamic Application Security Testing (DAST):** Assessing the running application through requests, responses, and observable behavior.
- **AI-assisted security assessment (AI):** Analyzing the project using the inputs and instructions defined for the experiment, and evaluating the tool's ability to identify and explain security issues.

Findings are compared against the research ground truth to evaluate true positives, false negatives, and false positives, while accounting for each approach's scope and visibility. A tool-generated alert is not treated as a confirmed vulnerability without review and verification.

## Branch Independence

Each branch represents a separate research stage or process. The `unSafe-code` branch preserves the version containing manually injected vulnerabilities so that results remain tied to a specific test subject and the experiment can be repeated.

Do not merge this branch into `main` or other branches. Do not introduce security fixes into this branch while repeating the same experiment. If a new experiment requires code changes, document those changes and the commit used so that its results can be distinguished from earlier results.

## Retesting and Preventing Information Leakage

This README is explanatory documentation created **after the assessment**; it was not part of the original assessment inputs. Even without listing vulnerability locations, describing the nature and purpose of the test subject can give an AI tool advance knowledge that influences its analysis and conclusions.

To repeat the experiment:

1. Prepare a test copy of the `unSafe-code` branch and record the commit being evaluated.
2. Delete this file (`README.md`) from the test copy before making it available to the tool. Keep the documentation outside the files accessible to the assessment tool.
3. Ensure that the inputs also exclude previous assessment results, ground truth that reveals the vulnerabilities, and documentation that points to the answers. Deleting this README alone is insufficient if that information remains available in other files or in the tool's context.
4. Use the documented assessment instructions, scope, and settings, with a consistent runtime environment and test data across comparisons.
5. Save the tool's outputs first, then evaluate them against the research ground truth outside the assessment tool's context.

These steps help ensure that the results reflect the tools' ability to discover vulnerabilities from the permitted inputs and that the comparison remains interpretable and reproducible.
