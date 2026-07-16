---
kind: collaboration
id: bld_collaboration_partner_listing
pillar: P12
llm_function: COLLABORATE
purpose: How partner_listing-builder works in crews with other builders
quality: null
title: "Collaboration Partner Listing"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [partner_listing, builder, collaboration]
tldr: "How partner_listing-builder works in crews with other builders"
domain: "partner_listing construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [partner_listing construction, collaboration partner listing, partner_listing, builder, collaboration, case_study-builder, app_directory_entry-builder, crew role  
curates, receives from, produces for]
density_score: 0.85
related:
  - bld_tools_partner_listing
  - bld_collaboration_app_directory_entry
  - partner-listing-builder
  - bld_output_template_partner_listing
  - bld_config_partner_listing
---
## Crew Role  
Curates and standardizes partner listing content, ensuring compliance with brand guidelines and data accuracy.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| CRM System    | Partner data          | JSON        |  
| Designer      | Formatting guidelines | Markdown    |  
| Manager       | Approval status       | Boolean     |  

## Produces For  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| Content Team  | Partner listing doc   | Markdown    |  
| Website Team  | Summary card          | HTML        |  
| Database      | Structured partner data| CSV         |  

## Boundary  
Does NOT handle case studies (handled by `case_study-builder`) or app directory entries (handled by `app_directory_entry-builder`). Legal reviews and compliance checks are managed by the Legal Team.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_partner_listing]] | upstream | 0.36 |
| [[bld_collaboration_app_directory_entry]] | sibling | 0.35 |
| [[partner-listing-builder]] | upstream | 0.32 |
| [[bld_output_template_partner_listing]] | upstream | 0.32 |
| [[bld_config_partner_listing]] | upstream | 0.31 |
