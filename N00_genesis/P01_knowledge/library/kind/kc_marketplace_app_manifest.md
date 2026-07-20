---
id: kc_marketplace_app_manifest
kind: knowledge_card
8f: F3_inject
title: Marketplace App Manifest Specification
version: 1.0.0
quality: null
pillar: P01
tldr: "Metadata manifest for AI marketplace listings: permissions, pricing, dependencies, and security"
when_to_use: "When publishing an app to Claude, LangChain, or HuggingFace marketplaces and need a standardized listing"
keywords: [marketplace application manifest, permissions, pricing model, functional capabilities, dependencies, data encryption standards, authentication mechanisms, model version compatibility, prompt budget allocations, chain execution policies, marketplace_app_manifest]
long_tails:
  - "how do I publish an app listing to the Claude or HuggingFace marketplace"
  - "how do I declare permissions pricing and dependencies for a marketplace app"
primary_8f: F5_call
slots:
  APP_NAME: "listing name shown in the marketplace"
  PERMISSIONS: "access-control and data-handling scopes requested"
  PRICING_MODEL: "subscription | pay-per-use | free-tier"
  DEPENDENCIES: "required libraries and runtime versions"
  PLATFORM: "Claude | LangChain | HuggingFace target"
density_score: 0.94
related:
  - marketplace-app-manifest-builder
  - bld_collaboration_marketplace_app_manifest
  - bld_instruction_marketplace_app_manifest
  - app-directory-entry-builder
  - kc_app_directory_entry
---

# Marketplace App Manifest Specification

This document defines the structure and requirements for marketplace application manifests used in Claude, LangChain, and HuggingFace ecosystems. The manifest serves as metadata configuration for app listings, defining permissions, pricing, and functional capabilities.

## Core Components

1. **Metadata**
   - App name and description
   - Versioning information
   - Author/organization details
   - License type and restrictions

2. **Permissions**
   - Access control settings
   - Data handling policies
   - Third-party integration rights
   - User privacy preferences

3. **Pricing Model**
   - Subscription tiers
   - Pay-per-use rates
   - Free tier limitations
   - Currency and payment methods

4. **Functional Capabilities**
   - Core features and APIs
   - Performance benchmarks
   - System requirements
   - Compatibility specifications

5. **Dependencies**
   - Required libraries/frameworks
   - Recommended runtime versions
   - External service integrations

6. **Security**
   - Data encryption standards
   - Authentication mechanisms
   - Audit logging requirements
   - Compliance certifications

## Platform-Specific Notes
- **Claude**: Include model version compatibility and prompt budget allocations
- **LangChain**: Specify chain execution policies and memory management
- **HuggingFace**: Define model card requirements and training data sources

This specification ensures consistent app discovery, security, and interoperability across different AI platform ecosystems.

### How to use
```text
Role: you are the CALL agent at 8F step F5 packaging an app for a marketplace.
Load this card to assemble a complete, listing-ready manifest.
- Fill every Core Component section; a missing block blocks marketplace review.
- Scope PERMISSIONS to least privilege; over-broad scopes fail security review.
- Declare the PRICING_MODEL and DEPENDENCIES exactly as the PLATFORM requires.
- Add the Platform-Specific Notes for your target (Claude / LangChain / HF).
```

### Procedure
```text
1. Set APP_NAME, version, author, and license in the Metadata block.
2. Enumerate PERMISSIONS (access, data handling, third-party rights).
3. Choose the PRICING_MODEL and list tiers, rates, and free-tier limits.
4. List functional capabilities, benchmarks, and DEPENDENCIES.
5. Fill the Security block (encryption, auth, audit, compliance).
6. Add PLATFORM-specific notes, then submit the manifest for review.
```

### Slots
```text
APP_NAME      = <APP_NAME>       # marketplace listing name
PERMISSIONS   = <PERMISSIONS>    # least-privilege scopes
PRICING_MODEL = <PRICING_MODEL>  # subscription | pay-per-use | free
DEPENDENCIES  = <DEPENDENCIES>   # libraries + runtime versions
PLATFORM      = <PLATFORM>       # Claude | LangChain | HuggingFace
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[marketplace-app-manifest-builder]] | downstream | 0.46 |
| [[bld_collaboration_marketplace_app_manifest]] | downstream | 0.35 |
| [[bld_instruction_marketplace_app_manifest]] | downstream | 0.33 |
| [[app-directory-entry-builder]] | downstream | 0.31 |
| [[kc_app_directory_entry]] | sibling | 0.30 |
