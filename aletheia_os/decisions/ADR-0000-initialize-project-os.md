# ADR-0000 — Initialize AletheiaOS

## Status

Draft until bootstrap finalization.

## Context

This project requires durable memory across AI-agent sessions and must avoid drift caused by local task optimization.

## Decision

Use this repository as the source of truth for mission, constraints, system graph, evidence, decisions, contracts, risks, and session state.

## Consequences

- AI assistants must read project-state files before non-trivial work.
- Important changes must update durable state.
- Git checkpoints become part of the research/design audit trail.

## Affected nodes

- `root`
- `engineering_execution`
- `evidence_validation`

## Review trigger

Revisit if AletheiaOS becomes too heavy, fails to prevent drift, or blocks useful iteration speed.
