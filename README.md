# MyStore Security Assessment Research Archive

This branch collects the assessment results, evaluation reports, reference data, and testing documentation for a graduation research project comparing three security assessment approaches on a Django e-commerce application: Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), and AI-assisted assessment.

The research uses two application versions: a security-focused baseline and a version with manually injected vulnerabilities. This README describes the files currently stored in `main`; it does not present a new assessment or recalculate the published evaluation results.

## Branches and Research Roles

| Branch | Purpose |
| --- | --- |
| `main` | Research artifacts: findings, evaluation reports, prompts, target descriptions, and methodology notes. |
| `Safe-code` | Application source for the security-focused baseline. |
| `unSafe-code` | Application source containing manually injected vulnerabilities for controlled testing. |

The branches represent separate research processes and must remain independent. Do not merge them. The `Safe-code/` and `unSafe-code/` directories on `main` organize archived artifacts; they are not the application source checkouts. There is no `manage.py` or runnable Django application on this branch.

## Repository Layout

```text
main/
|-- README.md
|-- ai_prompt.md
|-- ground_truth.json
|-- targets.md
|-- Safe-code/
|   |-- data/
|   |   |-- ai/ai_unified_clean.json
|   |   |-- dast/dast_unified_clean.json
|   |   `-- sast/sast_unified_clean.json
|   `-- docs/
|       |-- dast_secure.md
|       `-- sast_run/
|           |-- bandit_run.md
|           `-- semgrep_run.md
`-- unSafe-code/
    |-- ai/
    |-- dast/
    |-- sast/
    |-- Safe-code/        # Additional copies of baseline artifacts
    |-- ai_prompt.md
    |-- ground_truth.json
    `-- targets.md
```

## Reference Data and Assessment Instructions

| File | Contents and purpose |
| --- | --- |
| [ground_truth.json](ground_truth.json) | Reference catalog of 30 deliberately introduced vulnerabilities, with `GT-xx` identifiers, locations, affected functions, severity, assessment scopes, OWASP/CWE tags, and verification notes. Used to match findings to the experimental targets. |
| [ai_prompt.md](ai_prompt.md) | Archived AI assessment instructions, labeled BlackBox AI. Requests source/configuration review, runtime HTTP validation, and JSON output; excludes third-party supply-chain analysis unless implemented or modified in project code. |
| [targets.md](targets.md) | Application endpoint inventory, HTTP methods, authentication and role requirements, and setup notes. Setup instructions apply to an application branch, not directly to this archive. |
| [unSafe-code/ground_truth.json](unSafe-code/ground_truth.json) | A separate archived copy of the vulnerability reference. It currently differs from the root copy in the severity assigned to `GT-02`. |
| [unSafe-code/ai_prompt.md](unSafe-code/ai_prompt.md) and [unSafe-code/targets.md](unSafe-code/targets.md) | Copies of the root assessment prompt and endpoint inventory. |

Ground-truth entries describe the injected-vulnerability experiment. They should not be treated as a verified vulnerability list for the `Safe-code` application.

## Baseline Assessment Artifacts

The top-level [Safe-code](Safe-code) directory holds normalized finding lists and supporting assessment documentation for the security-focused version.

| File | Contents |
| --- | --- |
| [data/ai/ai_unified_clean.json](Safe-code/data/ai/ai_unified_clean.json) | 12 AI finding records, including descriptions, evidence, suggested fixes, and classification tags. |
| [data/dast/dast_unified_clean.json](Safe-code/data/dast/dast_unified_clean.json) | 25 DAST finding records, including informational observations. |
| [data/sast/sast_unified_clean.json](Safe-code/data/sast/sast_unified_clean.json) | 4 SAST finding records; some records contain multiple source locations. |
| [docs/dast_secure.md](Safe-code/docs/dast_secure.md) | OWASP ZAP assessment notes covering scope, authenticated/unauthenticated scanning, discovery, active scanning, and output conventions. |
| [docs/sast_run/bandit_run.md](Safe-code/docs/sast_run/bandit_run.md) | Bandit setup and scanning instructions, including the intended application folders and exclusion of virtual-environment dependencies. |
| [docs/sast_run/semgrep_run.md](Safe-code/docs/sast_run/semgrep_run.md) | Documentation of the Semgrep web/GitHub integration approach used for SAST. |

These counts are JSON records, not confirmed vulnerabilities or ground-truth matches. The branch name and the word `clean` in filenames do not establish that findings are verified, that duplicates are fully removed, or that the application is vulnerability-free.

## Injected-Version AI Artifacts

The [unSafe-code/ai](unSafe-code/ai) directory contains five separately archived AI reports and their evaluation materials.

| Location | Contents |
| --- | --- |
| `Blackbox(1st)-Primary/` | Primary Blackbox run: `vulnerability_report.json` (28 records), plus full-scope and common-scope Word comparison reports. |
| `Blackbox(2st)/blackbox(2st).json` | Second Blackbox report, with 29 records. |
| `blackbox(3st)/ai_unified_findings.json` | Third Blackbox report, with 32 records. The filename does not mean that all five experimental reports were merged. |
| `Chatgpt(1st)/security_report.json` | First ChatGPT report, with 34 records. |
| `Chatgpt(2st)/gpt-5.5-medium.json` | Second ChatGPT report, with 26 records. A finding can cover multiple issues, so record count need not equal the number of ground-truth matches. |
| `report_all_result.docx` | Comparison of the five reports, including per-run TP/FP/FN, precision, recall, F1-score, and discussion of missed findings for full and common scopes. |
| `ai_stability_metrics.json` | Per-report evaluation values and descriptive means/sample standard deviations across the five reports. Includes a provenance note about the common-scope TP value used for Blackbox (3). |

The stability file describes variation across these five archived reports. It does not establish repeatability for a single model under identical conditions, and it does not combine the reports into one detection result.

## Injected-Version DAST Artifacts

The [unSafe-code/dast](unSafe-code/dast) directory preserves two OWASP ZAP scan configurations:

| Directory | Scan and files |
| --- | --- |
| `Zap Scan - using default setting/` | Initial/default-settings run. Includes a 15-record normalized JSON report, a Word results summary, and full/common-scope comparison documents with `_1st_Run` filenames. |
| `Zap Scan - using auth$ulrSeed/` | Authenticated scan with 79 seeded URLs. Includes a 24-record JSON report, a Word results summary, full/common-scope comparisons, the URL seed list, and an accompanying JPEG image. |
| `fisrt run/` | Duplicate copies of the four initial-run report files. The directory spelling is preserved as stored. |

The authenticated/seeded artifacts also appear directly under `unSafe-code/dast/`. The Word results summary documents 24 alert types, of which 17 are non-informational and used in its evaluation. The seven informational alerts are excluded from those metrics. A matching vulnerability name alone is not sufficient to establish a true positive: the reported location and issue must match the reference target.

The JSON files here already use a finding schema. They should not be described as native, unmodified ZAP exports solely because their filenames contain “ZAP.”

## Injected-Version SAST Artifacts

The [unSafe-code/sast](unSafe-code/sast) directory contains:

| File | Contents |
| --- | --- |
| `vulnerability_report_sast.json` | 25 SAST finding records containing rule evidence, affected locations, severity, explanations, and remediation guidance. |
| `Full_Scope_SAST.docx` | Mapping of SAST findings to the full 30-target reference, including matched and missed vulnerabilities and additional findings. |
| `common_Scope_SAST.docx` | Evaluation against the 16-target common subset used in the comparison reports. |
| `SAST_Audit_Report.docx` | Full/common-scope metric summaries and interpretation of detection coverage. |

The SAST methodology documents cover Bandit and Semgrep. Finding records, rule hits, and matched ground-truth vulnerabilities are different counting units: several alerts can map to one target, and a single consolidated record can reference several locations.

## Shared Finding Format and Evaluation

The JSON finding lists generally use `id`, `name`, `location`, `source`, `severity`, `risk`, `evidence`, `explain`, `fix`, and `tags`. Some also include `tool`, and `location` may be a string or a list. Classification tags reference OWASP and CWE. Treat severity and risk values as recorded report attributes, not as a universally calibrated scale across tools.

The evaluation documents distinguish:

- **Full scope:** The complete 30-target reference used in the archived full-scope comparisons.
- **Common scope:** The 16-target subset used for comparison across assessment approaches.
- **TP / FN:** Reference targets detected or missed under the document's matching rules.
- **FP:** Findings not matched to the selected reference under the archived evaluation protocol. An unmatched finding can still represent a real issue outside that reference.

Consult each report's matching, grouping, and informational-alert rules before comparing its metrics. The AI comparison retains each report's original FP count in its common-scope evaluation.

## Duplicate Artifacts and Interpretation Notes

The archive preserves its existing structure, including duplicate copies. Do not count duplicate files as additional independent experiments.

- `unSafe-code/Safe-code/data/` duplicates the three JSON datasets in top-level `Safe-code/data/`.
- The DAST and SAST method documents under `unSafe-code/Safe-code/docs/` duplicate their top-level counterparts. This nested directory also contains an AI prompt copy and a separate `targets.md` document.
- Authenticated/seeded DAST files at `unSafe-code/dast/` duplicate the files in `Zap Scan - using auth$ulrSeed/`; the initial-run files in `fisrt run/` duplicate those in `Zap Scan - using default setting/`.
- The two ground-truth copies differ on `GT-02` severity. Their stored summary fields also do not fully agree with values derived from the individual entries. Record the exact reference file and commit used for any new calculation.
- Some narrative summaries differ from the JSON findings. For example, `dast_secure.md` says no high/critical findings were detected, while `dast_unified_clean.json` includes one High record. Some paths mentioned in methodology documents are historical or illustrative and do not exist in this checkout.

Use the actual dataset and the corresponding evaluation document together, and resolve inconsistencies before treating archived totals as a new validated result. This README leaves the original research artifacts unchanged.

## Reading and Repeating the Research

Start with the prompt and target inventory to understand the intended assessment. Read the JSON findings for evidence, then the Word comparison reports for ground-truth mapping and metrics. Use `ai_stability_metrics.json` for the archived cross-report descriptive statistics.

To run a new experiment, use the appropriate application branch and record its commit, environment, input scope, tool configuration, authentication state, and evaluation reference. Keep results and ground truth outside the assessment tool's inputs. In particular, do not provide this archive or README as AI assessment context: they reveal the experiment's design and expected findings and can cause information leakage.
