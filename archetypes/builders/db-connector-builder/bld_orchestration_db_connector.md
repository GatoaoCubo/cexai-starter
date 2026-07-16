---
kind: collaboration
id: bld_collaboration_connector
pillar: P12
llm_function: COLLABORATE
purpose: How db-connector-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Db Connector"
version: "1.0.0"
author: n03_builder
tags: [db_connector, builder, examples]
tldr: "Golden and anti-examples for db connector construction, demonstrating ideal structure and common pitfalls."
domain: "db connector construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [db connector construction, collaboration db connector, db_connector, builder, examples, "### crew: service bridge", my role, crew compositions, full integration stack, service bridge]
density_score: 0.90
related:
  - db-connector-builder
  - bld_collaboration_client
  - bld_tools_connector
  - bld_instruction_connector
  - bld_architecture_connector
---
# Collaboration: db-connector-builder

This ISO addresses the database connector domain: connection pooling, query execution, and SQL dialect handling.
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "how does this system exchange data bidirectionally with an external service?"
I do not build unidirectional clients. I do not define MCP protocol servers.
I specify bidirectional integrations so systems can sync data in both directions.
## Crew Compositions
### Crew: "Full Integration Stack"
```
  1. interface-builder -> "formal bilateral contract"
  2. client-builder -> "outbound API consumer"
  3. db-connector-builder -> "bidirectional sync with transform rules"
  4. env-config-builder -> "credentials and connection settings"
```
### Crew: "Service Bridge"
```
  1. db-connector-builder -> "bidirectional service integration"
  2. hook-builder -> "event triggers for sync operations"
  3. daemon-builder -> "persistent process hosting the connector"
```
## Handoff Protocol
### I Receive
- seeds: service name, protocol (REST, WebSocket, gRPC, MQTT), direction mapping
- optional: auth strategy, transform rules, health check config, rate limits
### I Produce
- connector artifact (.md + .yaml frontmatter)
- committed to: `cex/P04/examples/p04_connector_{service}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
- interface-builder: provides bilateral contract the connector implements
- client-builder: may provide outbound consumer that connector extends
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| daemon-builder | Hosts connector as persistent background process |
| hook-builder | Triggers connector sync on specific events |
| env-config-builder | Documents connector credentials and settings |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[db-connector-builder]] | upstream | 0.54 |
| [[bld_collaboration_client]] | sibling | 0.42 |
| [[bld_tools_connector]] | upstream | 0.39 |
| [[bld_instruction_connector]] | upstream | 0.38 |
| [[bld_architecture_connector]] | upstream | 0.37 |
