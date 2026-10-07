# Argos — Offline assessment report

## Mission

**Title:** Synthetic offline assessment

**ID:** demo\-offline

Demonstrates evidence integrity and human review using invented training data\. No application has been tested\.

**Assessment SHA-256:** 3bd4926b765b4995a286ef979ec876b18d5952061046cf206e0e30a4cc2785e5

**Scope:**

- training\-fixtures

## Review summary

Findings: 2. Accepted: 0. Rejected: 0. Needs review: 2.

Evidence integrity and a recorded review decision do not establish that a vulnerability has been technically confirmed. Severity and provenance are declared by the input author. Rejected and unreviewed findings remain visible.

| Declared severity | Findings |
| --- | ---: |
| critical | 0 |
| high | 0 |
| medium | 0 |
| low | 1 |
| info | 1 |

## Findings

### F\-001 — Diagnostic configuration needs review

**Declared severity:** low

**Asset:** training\-fixtures

**Review:** needs_review

The synthetic configuration declares debug mode\. This observation requires human review and is not a confirmed vulnerability\.

**Recommendation:** Check the intended environment and document the chosen diagnostic settings\.

**Evidence IDs:** E\-001

### F\-002 — Training banner could be clearer

**Declared severity:** info

**Asset:** training\-fixtures

**Review:** needs_review

The invented banner could describe the purpose of the training application more clearly\.

**Recommendation:** Make the training\-only purpose explicit in the banner\.

**Evidence IDs:** E\-002

## Evidence register

### E\-001

**File:** evidence/configuration\.txt

**SHA-256:** 821ce65fea65e873803390058858bf4c0b647eeb17a74397ee7b9f74b348ff0c

**Declared source:** Original Argos synthetic fixture; no target or real user data\.

Synthetic configuration for demonstrating a review workflow\.

### E\-002

**File:** evidence/banner\.txt

**SHA-256:** 29f3cce70d629012f6ad39ba7b335603f35951d70d866f487a67f761ddb2fe2d

**Declared source:** Original Argos synthetic fixture; no target or real user data\.

Synthetic application banner for a documentation review\.
