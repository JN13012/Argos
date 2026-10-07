"use strict";

// Synthetic fixture copied from examples/offline/assessment.json.
// This dashboard does not read local evidence or contact Argos Core.
globalThis.ARGOS_DEMO = Object.freeze({
  "schema_version": 1,
  "mission": {
    "id": "demo-offline",
    "title": "Synthetic offline assessment",
    "description": "Demonstrates evidence integrity and human review using invented training data. No application has been tested.",
    "scope": [
      "training-fixtures"
    ]
  },
  "evidence": [
    {
      "id": "E-001",
      "path": "evidence/configuration.txt",
      "sha256": "821ce65fea65e873803390058858bf4c0b647eeb17a74397ee7b9f74b348ff0c",
      "description": "Synthetic configuration for demonstrating a review workflow.",
      "source": "Original Argos synthetic fixture; no target or real user data."
    },
    {
      "id": "E-002",
      "path": "evidence/banner.txt",
      "sha256": "29f3cce70d629012f6ad39ba7b335603f35951d70d866f487a67f761ddb2fe2d",
      "description": "Synthetic application banner for a documentation review.",
      "source": "Original Argos synthetic fixture; no target or real user data."
    }
  ],
  "findings": [
    {
      "id": "F-001",
      "title": "Diagnostic configuration needs review",
      "severity": "low",
      "asset": "training-fixtures",
      "description": "The synthetic configuration declares debug mode. This observation requires human review and is not a confirmed vulnerability.",
      "recommendation": "Check the intended environment and document the chosen diagnostic settings.",
      "evidence_ids": [
        "E-001"
      ],
      "review": null
    },
    {
      "id": "F-002",
      "title": "Training banner could be clearer",
      "severity": "info",
      "asset": "training-fixtures",
      "description": "The invented banner could describe the purpose of the training application more clearly.",
      "recommendation": "Make the training-only purpose explicit in the banner.",
      "evidence_ids": [
        "E-002"
      ],
      "review": null
    }
  ]
});
