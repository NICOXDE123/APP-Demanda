# Implementation Plan: Proyecta — MVP de oportunidades, demandas y proyecciones

**Branch**: `001-proyecta-mvp` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-proyecta-mvp/spec.md`

**Note**: This plan is the Phase 0 and Phase 1 design baseline for the MVP; implementation details belong to `tasks.md` and the implementation phase.

## Summary

Construir un monolito modular en Python 3.12 con FastAPI que centralice oportunidades, demandas y continuidades, calcule Base, MAB, Backlog, Forecast, HC y Gap con un motor único, y exponga un dashboard ejecutivo con detalle hasta el registro. La interfaz será server-rendered con Jinja2 + HTMX + Bootstrap + Chart.js; la persistencia será Firestore en modo Datastore detrás de un puerto de repositorio. La auditoría y la bitácora serán de solo inserción, con un evento por campo y trazabilidad de impacto en MAB/Forecast.

El plan implementa las decisiones ya cerradas en la especificación: 100 % de probabilidad al adjudicar (`H-01`), prorrateo por motivo de cierre (`H-02`), lista amplia de motivos (`H-03`), horas editables con vigencia mensual (`H-04`), sin migración real en el MVP (`H-05`), vigencia mensual de probabilidad y confiabilidad (`H-06`) y `Backlog confirmado` como vista de la MAB (`H-07`).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Jinja2, HTMX 2.x, Bootstrap 5.x, Chart.js 4.x, `google-cloud-datastore`, `google-cloud-secret-manager`, `google-cloud-logging`, `argon2-cffi`, `openpyxl`, `pytest`, `pytest-cov`, `httpx`, Playwright, axe-core, `ruff` y `mypy`.

**Storage**: Firestore en modo Datastore, con emulador local y transacciones ACID; repositorios aislados para permitir Cloud SQL si NTT DATA lo exige.

**Testing**: `pytest` para dominio, integración y contrato; `pytest-cov` con umbral de 90 % en dominio; Playwright + axe-core para E2E y accesibilidad; casos C-01 a C-08 como regresión obligatoria.

**Target Platform**: Linux container en Cloud Run (GCP), navegadores Chrome y Edge de las últimas dos versiones, responsive desde 360 px.

**Project Type**: Aplicación web server-rendered con API REST `/api/v1` y OpenAPI 3.1.

**Performance Goals**: Dashboard < 2 s p95 con 1.000 registros y 300 activos; listas < 1 s; consultas de API < 500 ms p95; diseño para 5.000 registros y 50 usuarios concurrentes.

**Constraints**: CLP único; horizonte de 12 meses; 180 h iniciales editables con vigencia mensual; sin datos reales en demo ni en la carga inicial; auditoría de solo inserción por 5 años; OWASP Top 10 y ASVS L1; WCAG 2.1 AA; costo USD 10–30 mensuales.

**Scale/Scope**: 5.000 registros, ~15.000 perfiles, 12 cortes/año, 3 roles, 11 indicadores del dashboard y 90 requisitos funcionales.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Evidencia |
|---|---|---|
| I. Integridad de los datos | PASS | Semilla sintética y sin migración real (`H-05`); simulación en memoria sin persistencia; no se implementan métricas sin fórmula; los datos faltantes se marcan, no se imputan. |
| II. Reglas explícitas y cálculo determinista | PASS | Motor único en el paquete `src/proyecta/domain/engine/`; `Decimal` para cálculo y enteros CLP/centavos/puntos base en almacenamiento; sin fórmulas en plantillas, JavaScript ni consultas. |
| III. Trazabilidad y auditoría | PASS | `EventoAuditoria` por campo, `Bitacora` inmutable, `405` en la API, `409` por versión, cortes inmutables y retención de 5 años. |
| IV. Separación de responsabilidades | PASS | Capas `domain`, `application`, `infrastructure` e `interfaces`; dominio sin FastAPI, Datastore ni Jinja2; repositorios como puertos. |
| V. Calidad verificable | PASS | `pytest` + cobertura ≥ 90 % del dominio; C-01 a C-08; pruebas de contrato, permisos, auditoría, concurrencia, redondeo y E2E. |
| VI. Consistencia documental | PASS | `spec.md` → `plan.md` → `data-model.md` → `contracts/openapi.yaml` → `tasks.md`; cada `FR` se mapea a módulo y prueba. |
| VII. Cambios mínimos | PASS | No existe código previo que reemplazar; se adopta la arquitectura de referencia del Anexo C sin servicios extra; dependencias justificadas. |
| VIII. Transparencia de IA | PASS | Adaptador opcional con feature flag; etiquetas dato verificado/cálculo/estimación/datos insuficientes; aprobación humana; la IA no escribe; simulación aislada. |
| IX. Seguridad y protección de datos | PASS | Argon2id, sesión de servidor, cookie `HttpOnly`/`Secure`/`SameSite=Strict`, CSRF, RBAC por rol y propiedad, Secret Manager, datos sintéticos y exportación filtrada. |

**Gate result**: PASS. No hay violaciones que justificar en `Complexity Tracking`.

## Project Structure

### Documentation (this feature)

```text
specs/001-proyecta-mvp/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas
├── data-model.md        # Fase 1: entidades, reglas, índices
├── quickstart.md        # Fase 1: validación end-to-end
├── contracts/
│   └── openapi.yaml     # Fase 1: contrato REST /api/v1
├── checklists/
│   └── requirements.md  # Calidad de la especificación
└── tasks.md             # Fase 2 (lo genera /speckit.tasks)
```

### Source Code (repository root)

```text
src/proyecta/
├── main.py                    # Creación de la app y wiring
├── config.py                  # Configuración por entorno
├── domain/
│   ├── entities.py            # Entidades y value objects
│   ├── engine/                # Base, MAB, Backlog, Forecast, HC, Gap, puente (T067–T073, T110)
│   ├── rules.py               # Reglas de negocio y validaciones
│   ├── states.py              # Máquina de estados y transiciones
│   ├── quality.py             # DQ-01 a DQ-13
│   └── permissions.py         # Políticas de rol y propiedad
├── application/
│   ├── ports.py               # Interfaces de repositorio, reloj, IA, exportación
│   └── use_cases/
│       ├── auth.py
│       ├── registros.py
│       ├── perfiles.py
│       ├── estados.py
│       ├── calculo.py
│       ├── backlog.py
│       ├── metas.py
│       ├── cierre.py
│       ├── calidad.py
│       ├── exportacion.py
│       └── ia.py
├── infrastructure/
│   ├── datastore/
│   │   ├── repositories.py
│   │   ├── mappings.py
│   │   └── indexes.py
│   ├── auth/
│   │   ├── passwords.py
│   │   ├── sessions.py
│   │   └── csrf.py
│   ├── export/
│   │   └── xlsx.py
│   ├── ai/
│   │   └── vertex.py
│   └── logging.py
├── interfaces/
│   ├── web/
│   │   ├── routes/
│   │   ├── templates/
│   │   └── static/
│   └── api/
│       └── v1/
├── seed/
│   └── synthetic.py

tests/
├── unit/domain/
├── integration/
├── contract/
└── e2e/

scripts/
├── seed_synthetic.py
└── rebuild_resumen.py

deploy/
├── Dockerfile
├── cloudbuild.yaml
└── service.yaml

pyproject.toml
README.md
```

**Structure Decision**: un solo proyecto desplegable, con separación lógica de capas. No se separa frontend y backend porque la interfaz es server-rendered con Jinja2 + HTMX; el dominio puro permite probar las reglas sin HTTP ni base de datos. `interfaces/web` y `interfaces/api` comparten los mismos casos de uso.

## Phase 0 — Research

Resultados en [research.md](research.md). Decisiones principales:

- Python 3.12 + FastAPI + Jinja2/HTMX.
- Firestore Datastore con repositorios y emulador local.
- Sesión de servidor, Argon2id y CSRF.
- Motor puro con `Decimal`; almacenamiento en enteros CLP/centavos/puntos base.
- Auditoría de solo inserción y cierre por lotes idempotentes.
- Dashboard con proyección `ResumenMensual`; exportación con `openpyxl`.
- IA opcional con Vertex AI y simulación en memoria.
- Pruebas con pytest, Playwright y axe; despliegue en Cloud Run.

No quedan incógnitas técnicas pendientes. Las decisiones `S-xx` de negocio se aíslan con catálogos, parámetros y datos sintéticos.

## Phase 1 — Design

- [data-model.md](data-model.md): 17 entidades, claves, relaciones, estados, invariantes, índices y volumen.
- [contracts/openapi.yaml](contracts/openapi.yaml): contrato REST `/api/v1` con autenticación por sesión, recursos principales, errores y esquemas.
- [quickstart.md](quickstart.md): escenarios ejecutables de validación end-to-end con emulador y datos sintéticos.

## Implementation Strategy

### Milestones

| Hito | Alcance | Criterio de salida |
|---|---|---|
| **M0 · Fundación** | Proyecto, configuración, layout, autenticación, usuarios, catálogos, parámetros, auditoría base | Login, roles, catálogos y auditoría funcionando con pruebas |
| **M1 · Registro y seguimiento** | Registros, perfiles, tarifas, ajustes, estados, bitácora | AC-01, AC-02, AC-03, AC-09, AC-10, AC-13 |
| **M2 · Motor** | Base, MAB, Backlog, Forecast, HC, Gap, series de 12 meses, previsualización | C-01 a C-08 y AC-04, AC-05, AC-12 |
| **M3 · Dashboard** | 11 indicadores, filtros, detalle, calidad, alertas | AC-11, AC-15 y RNF-03 |
| **M4 · Backlog, metas y gap** | Contratos, vencimientos, metas, gap y cobertura | AC-06, AC-07 |
| **M5 · Cierre y puente** | Corte, congelamiento, comparación y puente | AC-08 |
| **M6 · Reportes, exportación y semilla** | R-01 a R-13, `.xlsx`, datos sintéticos, rendimiento | AC-14, exportación filtrada y demo reproducible |
| **M7 · Endurecimiento** | Seguridad, accesibilidad, E2E, IA/simulador opcional, guion de demo | RNF-04 a RNF-18 y demo de punta a punta |

### Ordering constraints

1. La autenticación y los catálogos preceden a cualquier registro.
2. El motor se implementa antes del dashboard y de la exportación.
3. La auditoría se integra en cada caso de uso, no al final.
4. El cierre y el puente requieren el motor y los cortes.
5. La IA y el simulador son opcionales y no bloquean M0–M6.

## Performance & Scale

- Consultas indexadas por `owner_id`, `sector_id`, `tipo`, `estado` y `fecha_ingreso`; paginación obligatoria en listas.
- `ResumenMensual` se actualiza en la misma operación de escritura o por comando de reconstrucción; el dashboard no recalcula 5.000 registros en cada request.
- El cierre escribe `CorteDetalle` en lotes de 500 y marca `CERRADO` al final; es idempotente y reanudable.
- La exportación se genera en streaming y no carga todo el libro en memoria.
- Prueba de carga con 1.000 registros/300 activos y 5.000/50 concurrentes antes de la demo.

## Security & Privacy

- Sesión de servidor con cookie `HttpOnly`, `Secure`, `SameSite=Strict`; expiración y revocación.
- Argon2id, bloqueo tras cinco intentos por cuenta e IP, CSRF en formularios y HTMX.
- RBAC por rol y propiedad en cada caso de uso; el Ejecutivo es de solo lectura.
- Secretos en Secret Manager; `.env` solo local y fuera del repositorio.
- Datos sintéticos en demo, pruebas y carga inicial; no se envían datos reales a modelos externos.
- Exportación con filtros, permisos y sanitización de fórmulas.
- Dependencias escaneadas; hallazgos críticos corregidos antes de la entrega.

## Risks & Mitigations

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Límites de transacción de Datastore en el cierre | Alto | Cierre por lotes con estado `CREANDO`/`CERRADO` e idempotencia; no una transacción única |
| p95 del dashboard con 5.000 registros | Alto | Proyección `ResumenMensual`, índices y paginación; prueba de carga temprana |
| `H-01` (100 % al adjudicar) no validado por el sponsor | Alto | Regla aislada en `states.py` y pruebas; cambio acotado si el sponsor la revierte |
| `S-01` (180 h) rechazado | Medio | Horas como parámetro con vigencia; recálculo y comparación documentados |
| `S-02` (nombre de la sexta etapa) rechazado | Bajo | Etapa como catálogo; renombrar sin cambiar el esquema |
| `S-05`/`S-06` sin contratos/metas reales | Medio | Semilla sintética y fixtures; módulos probados con datos de ejemplo |
| `S-12` sin proyecto/región GCP | Medio | Emulador local y despliegue reproducible; parametrizar proyecto/región |
| Migración real fuera del MVP | Medio | Carga sintética y guía de migración posterior; no se promete en la demo |
| IA no disponible | Bajo | Feature flag y fallback; el MVP funciona sin IA |
| Accesibilidad incompleta | Medio | axe en CI, revisión manual y pruebas con usuarios |

## Open Decisions

Las decisiones `S-xx` siguen abiertas y el plan las aísla:

| ID | Cómo la aísla el plan |
|---|---|
| `S-01` | Horas en `Parametro` con vigencia; 180 h iniciales; sin constante en el motor |
| `S-02` | Flujo como valor de catálogo; sin lógica condicionada al nombre |
| `S-03` | Cierre con motivo; el cálculo excluye el registro; la semántica se valida con el sponsor |
| `S-04` | Alias de catálogos en `Catalogo.metadata`; sin normalización hardcodeada |
| `S-05` | Contratos con `monto_mensual` o perfiles; fixtures sintéticos |
| `S-06` | Metas por sector/mes; fixtures sintéticos |
| `S-10` | Clientes sembrados con datos sintéticos |
| `S-11` | Migración real fuera del MVP; solo carga sintética |
| `S-12` | Proyecto/región parametrizados; Cloud Run como referencia |
| `S-15` | Este plan es línea base; la reestimación se hace al cerrar el alcance |

No quedan contradicciones `H` abiertas.

## Traceability

| Requisitos | Módulo / artefacto | Pruebas |
|---|---|---|
| `FR-001` a `FR-010` | `domain/entities`, `application/use_cases/registros`, `interfaces/api/v1` | Unitarias + `AC-01`, `AC-12` |
| `FR-011` a `FR-017` | `application/use_cases/perfiles`, `domain/engine` | Unitarias + `AC-01` |
| `FR-018` a `FR-028` | `domain/states`, `domain/rules`, `use_cases/estados` | Unitarias + `AC-02`, `AC-03`, `AC-16`, `AC-09` |
| `FR-029` a `FR-038` | `domain/engine`, `use_cases/calculo` | C-01 a C-08 + `AC-04`, `AC-05`, `AC-12`, `AC-17` |
| `FR-039` a `FR-045` | `use_cases/backlog`, `use_cases/metas`, `domain/engine` | `AC-06`, `AC-07` |
| `FR-046` a `FR-052` | `use_cases/calculo`, `interfaces/web`, `ResumenMensual` | `AC-11`, `AC-15`, RNF-03 |
| `FR-053` a `FR-060` | `use_cases/auditoria`, `domain/audit` | `AC-09`, `AC-10`, `AC-13` |
| `FR-061` a `FR-067` | `use_cases/auth`, `domain/permissions`, `infrastructure/auth` | `AC-10` |
| `FR-068` a `FR-072` | `domain/quality`, `use_cases/calidad` | `AC-11` |
| `FR-073` a `FR-077` | `use_cases/cierre`, `domain/engine` | `AC-08` |
| `FR-078` a `FR-081` | `use_cases/exportacion`, `infrastructure/export` | Exportación filtrada |
| `FR-082` a `FR-086` | `use_cases/ia`, `infrastructure/ai` | Pruebas de no escritura y etiquetas |
| `FR-087` a `FR-090` | `seed/synthetic`, `scripts/seed_synthetic.py` | `AC-14` |

## Complexity Tracking

No hay violaciones de la constitución ni excepciones que justificar. Las decisiones de diseño con mayor peso están documentadas en [research.md](research.md): Firestore Datastore, sesión de servidor, proyección `ResumenMensual`, cierre por lotes y motor puro.

## Post-Design Constitution Check

Después de definir el modelo, el contrato y la guía de validación, se re-evaluaron los nueve principios: todos siguen en PASS. El diseño no introduce fórmulas en la interfaz, no usa datos reales en demo, no hace que la IA escriba, mantiene la auditoría de solo inserción y conserva la separación de capas. No se requieren excepciones.
