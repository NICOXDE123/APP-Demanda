# Requirements Quality Checklist: Proyecta — MVP

**Purpose**: Revisar la calidad, claridad, consistencia y cobertura de los requisitos de Proyecta antes de implementar.
**Created**: 2026-10-27
**Feature**: [spec.md](../spec.md)
**Focus**: Calidad integral de requisitos
**Depth**: Estándar
**Audience**: Revisor/PR

**Note**: Este checklist evalúa los requisitos, no la implementación. Cada ítem pregunta si el requisito está definido, cuantificado, es consistente o trazable; no verifica que el sistema funcione.
**Review Ownership**: Artefacto de revisión propiedad del revisor. Marcar `[x]` solo cuando el criterio de calidad de requisitos esté satisfecho.
**Marker Semantics**: `[x]` significa que el requisito fue revisado y cumple el criterio; no significa que la implementación esté terminada.

## Requirement Completeness

- [ ] CHK001 - Are the MVP scope and excluded capabilities (ERP, costs, transactional Invoicing/Staffing, CRM, SSO, multicurrency) explicitly bounded? [Completeness, Spec §Out of Scope]
- [ ] CHK002 - Is the exclusion of real-data migration from the MVP documented together with its later-stage treatment? [Completeness, Spec §H-05, §S-11]
- [ ] CHK003 - Are the 9 mandatory OnePage capabilities traceable to user stories, FRs and acceptance criteria? [Coverage, Spec §Traceability]
- [ ] CHK004 - Are the three roles, their responsibilities and their read/write scope fully specified? [Completeness, Spec §Actores, §FR-061–067]
- [ ] CHK005 - Are AI and simulation explicitly optional, non-blocking and outside the critical path? [Completeness, Spec §US10, §FR-084]
- [ ] CHK006 - Is the synthetic dataset's volume and coverage specified for the demo and for testing? [Gap, Spec §Assumptions, Plan §M6]

## Requirement Clarity

- [ ] CHK007 - Is "Backlog confirmado" defined unambiguously as a view of MAB rather than a separate bag? [Clarity, Spec §FR-032, §H-07]
- [ ] CHK008 - Are MAB, Backlog contractual, Forecast and Ingreso potencial distinguished with explicit formulas? [Clarity, Spec §FR-030–034]
- [ ] CHK009 - Is "Confiabilidad" distinguished from "Probabilidad" and its application to the Backlog confirmado specified? [Clarity, Spec §FR-026, §FR-032]
- [ ] CHK010 - Are "Cerrada" and "Cancelada" semantics, motives and effects unambiguous? [Clarity, Spec §FR-005, §S-03]
- [ ] CHK011 - Are "Corte", "Cierre de período" and "Puente" used consistently? [Consistency, Spec §FR-073–077]
- [ ] CHK012 - Are percentage units (stored 0–1, displayed 0–100) and rounding rules consistently specified? [Consistency, Spec §FR-028, §FR-036]

## Requirement Consistency

- [ ] CHK013 - Is the 100 % probability at adjudication reflected consistently in states, transitions, AC-02 and the retirement of the 80–95 % range? [Consistency, Spec §FR-021, §AC-02, §H-01]
- [ ] CHK014 - Is the motive list consistent across FR-054, audit rules, validations and H-03? [Consistency, Spec §FR-054]
- [ ] CHK015 - Are editable hours with monthly validity reflected in FR-037, the bridge, edge cases and the plan? [Consistency, Spec §FR-037, §FR-075]
- [ ] CHK016 - Is the no-real-migration decision consistent across US11, FR-087, AC-14, S-11 and Out of Scope? [Consistency, Spec §US11, §AC-14]
- [ ] CHK017 - Does every FR trace to a source RF/RN and to at least one acceptance criterion or test? [Traceability, Spec §Traceability]
- [ ] CHK018 - Are identifiers stable and non-renumbered across spec, plan and data model? [Traceability, Spec §Conventions]

## Acceptance Criteria Quality

- [ ] CHK019 - Are all 17 acceptance criteria written as Given/When/Then and objectively testable? [Measurability, Spec §AC]
- [ ] CHK020 - Is there an acceptance criterion for cancellation by each motive, especially DUPLICADO versus CANCELADA_CLIENTE? [Gap, Spec §FR-005]
- [ ] CHK021 - Is there an acceptance criterion for a change of hours with effective date and unchanged prior months? [Gap, Spec §FR-037]
- [ ] CHK022 - Are no-double-counting and the Backlog confirmado view covered by acceptance criteria? [Coverage, Spec §AC-05, §AC-06]
- [ ] CHK023 - Are the success criteria measurable, technology-agnostic and tied to a verification method? [Measurability, Spec §SC]

## Scenario & Edge Case Coverage

- [ ] CHK024 - Are primary, alternate, exception and recovery flows defined for the record lifecycle? [Coverage, Spec §Flujos]
- [ ] CHK025 - Are empty, loading and error states defined for dashboard, lists, quality panel and export? [Gap, Spec §UX]
- [ ] CHK026 - Are concurrent edit, stale version and conflict resolution fully specified? [Coverage, Spec §FR-058]
- [ ] CHK027 - Are failed close/cut recovery, idempotency and partial-failure requirements defined? [Coverage, Spec §FR-073, §FR-074]
- [ ] CHK028 - Are permission-denied, session-expired and cross-owner export scenarios addressed? [Coverage, Spec §FR-063, §FR-067, §FR-081]

## Non-Functional Requirements

- [ ] CHK029 - Are performance targets quantified for dashboard, lists and queries under the stated volume? [Clarity, Spec §NFR-001]
- [ ] CHK030 - Are availability, RTO and RPO defined for the demo period? [Clarity, Spec §NFR-003]
- [ ] CHK031 - Are authentication, authorization, session, CSRF and password requirements complete? [Completeness, Spec §NFR-004]
- [ ] CHK032 - Are accessibility requirements measurable (WCAG, axe, SUS)? [Measurability, Spec §NFR-007]
- [ ] CHK033 - Are privacy, synthetic data, backup and retention requirements explicit? [Completeness, Spec §NFR-005, §NFR-012, §NFR-018]
- [ ] CHK034 - Are rate-limiting or throttling requirements defined or explicitly excluded for login and export? [Gap, Spec §NFR-004]

## Dependencies, Assumptions & Decisions

- [ ] CHK035 - Are open decisions S-xx recorded with owner, status and affected requirements? [Traceability, Spec §Open Decisions]
- [ ] CHK036 - Are external dependencies (contracts, metas, environment) and sponsor sign-off documented? [Dependency, Spec §S-05, §S-06, §S-12]
- [ ] CHK037 - Are assumptions about 180 h, CLP, 12 months and synthetic data validated or flagged? [Assumption, Spec §Assumptions]

## Ambiguities & Conflicts

- [ ] CHK038 - Are H-01 to H-07 resolutions reflected in `docs/fuentes/requerimientos.md`, or is the pending update explicit? [Traceability, Spec §H resolved note]
- [ ] CHK039 - Is the probability catalog still consistent with 100 % at Adjudicada and the historical 80/90/95 % values? [Conflict, Spec §FR-028]
- [ ] CHK040 - Is the `En Curso` bag still ambiguous for Continuidad after H-07? [Ambiguity, Spec §FR-032, §FR-033]

## Notes

- Marcar `[x]` solo después de revisar el requisito; el estado del checkbox pertenece al revisor.
- Los ítems con `[Gap]`, `[Ambiguity]` o `[Conflict]` señalan hallazgos de calidad, no fallas de implementación.
- `/speckit.implement` lee el estado de los checkboxes como compuerta y no debe modificar los marcadores.
- `checklists/requirements.md` es el checklist integrado de calidad de la especificación; este archivo es un checklist de revisión de requisitos separado.
- Añadir hallazgos o comentarios en línea y enlazar las secciones correspondientes de `spec.md`, `plan.md` o `docs/fuentes/requerimientos.md`.
- Los ítems están numerados globalmente para facilitar la referencia en la revisión.
