# ADR — Registro de decisiones de arquitectura

Este directorio guarda las decisiones que afectan la estructura, la seguridad, la persistencia o la integración de Proyecta.

## Índice

| ADR | Tema | Estado | Responsable |
|---|---|---|---|
| `001-stack.md` | Python 3.12 + FastAPI + Firestore Datastore + Jinja2/HTMX | Pendiente | Matías Mcintire |
| `002-sesiones.md` | Sesión de servidor, Argon2id y CSRF | Pendiente | Matías Mcintire |
| `003-auditoria.md` | Auditoría de solo inserción y retención | Pendiente | Roberto Villouta |
| `004-cierre.md` | Cierre por lotes idempotentes | Pendiente | Felipe Astete |

## Formato

Cada ADR debe incluir:

- **Estado**: propuesto, aceptado, reemplazado o rechazado.
- **Contexto**: problema y restricciones.
- **Decisión**: qué se eligió.
- **Consecuencias**: impacto, riesgos y alternativas descartadas.
- **Referencias**: `spec.md`, `plan.md`, `data-model.md` o `docs/fuentes/requerimientos.md`.

## Reglas

- Un ADR no reemplaza la especificación ni la Constitución.
- Las decisiones de negocio se validan con el PO y, cuando corresponda, con el sponsor.
- Un ADR aceptado se enlaza desde `plan.md` o `tasks.md`.
- No se borra un ADR: se marca como reemplazado por otro.
