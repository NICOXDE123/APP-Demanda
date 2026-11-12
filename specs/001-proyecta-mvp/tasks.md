---
description: "Task list for Proyecta MVP implementation"
---

# Tasks: Proyecta — MVP de oportunidades, demandas y proyecciones

**Input**: Design documents from `/specs/001-proyecta-mvp/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Requeridas por la especificación (Principio V y `RNF-13`). Escribir primero, verificar que fallan y luego implementar. El dominio debe alcanzar ≥ 90 % de cobertura.

**Organization**: Tareas agrupadas por historia de usuario para permitir implementación y prueba independientes. El MVP mínimo es US1–US4; US5–US9 son la operación completa; US10 y US11 son opcionales/etapa posterior.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias de tareas incompletas).
- **[Story]**: Historia de usuario a la que pertenece la tarea (`US1`…`US11`).
- Cada tarea incluye una ruta de archivo exacta.

## Path Conventions

Proyecto único server-rendered: `src/proyecta/` y `tests/` en la raíz del repositorio. Los artefactos de diseño viven en `specs/001-proyecta-mvp/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto, dependencias y estructura base.

- [ ] T001 Crear la estructura `src/proyecta/{domain,application,infrastructure,interfaces,seed}`, `tests/{unit/domain,integration,contract,e2e}`, `scripts/` y `deploy/` según `plan.md`.
- [ ] T002 Inicializar `pyproject.toml` con Python 3.12, FastAPI, Uvicorn, Pydantic v2, Jinja2, `google-cloud-datastore`, `google-cloud-secret-manager`, `google-cloud-logging`, `argon2-cffi`, `openpyxl` y extras de desarrollo.
- [ ] T003 Configurar `ruff`, `pytest`, `pytest-cov` y `mypy` en `pyproject.toml` con umbral de cobertura del dominio en 90 %.
- [ ] T004 [P] Crear `deploy/Dockerfile` y `deploy/.dockerignore` para una imagen Linux reproducible.
- [ ] T005 [P] Crear `deploy/cloudbuild.yaml` y `deploy/service.yaml` con variables de entorno, puerto y límites de Cloud Run.
- [ ] T006 [P] Crear `src/proyecta/config.py` y `.env.example` para `DATASTORE_EMULATOR_HOST`, `GOOGLE_CLOUD_PROJECT`, `PROYECTA_ENV`, `PROYECTA_SECRET_KEY`, `PROYECTA_AI_ENABLED` y `PROYECTA_SEED_PASSWORD` (solo desarrollo local).
- [ ] T007 [P] Crear `src/proyecta/main.py` con la app FastAPI, el montaje de routers y `/health`.
- [ ] T008 [P] Crear `src/proyecta/interfaces/web/static/css/app.css` y `js/app.js` con Bootstrap, HTMX y Chart.js servidos localmente.
- [ ] T009 [P] Crear `tests/conftest.py` con fixtures de app, cliente HTTP, repositorios y emulador de Datastore.
- [ ] T010 [P] Crear `README.md` con requisitos, instalación, variables de entorno, comandos de prueba y advertencia de datos sintéticos.
- [ ] T011 Crear el pipeline de CI en `deploy/cloudbuild.yaml` que ejecute lint, pruebas y cobertura antes de desplegar.

**Checkpoint**: Proyecto instala, arranca y ejecuta una prueba vacía.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Núcleo compartido que MUST estar listo antes de cualquier historia.

**⚠️ CRITICAL**: Ninguna historia puede empezar hasta completar esta fase.

- [ ] T012 Crear enums de dominio (`Tipo`, `Estado`, `Flujo`, `Rol`, `Modalidad`, `Origen`, `Bucket`) en `src/proyecta/domain/enums.py`.
- [ ] T013 Crear value objects `Money`, `Percentage`, `Period` y `DateRange` en `src/proyecta/domain/value_objects.py`.
- [ ] T014 Crear entidades `Usuario`, `Registro`, `Perfil`, `TarifaPerfil`, `AjusteHC` y `Contrato` en `src/proyecta/domain/entities.py`.
- [ ] T015 Crear entidades `VigenciaEstadoCalculo`, `Bitacora`, `EventoAuditoria`, `Parametro`, `Catalogo`, `MetaComercial`, `Corte`, `CorteDetalle`, `SugerenciaIA` y `Sesion` en `src/proyecta/domain/entities.py`.
- [ ] T016 Crear excepciones y códigos de error de dominio en `src/proyecta/domain/errors.py`.
- [ ] T017 Definir puertos de repositorio, reloj, exportación e IA en `src/proyecta/application/ports.py`.
- [ ] T018 Implementar serialización y mapeo Datastore de entidades en `src/proyecta/infrastructure/datastore/mappings.py`.
- [ ] T019 Implementar el repositorio de `Registro` en `src/proyecta/infrastructure/datastore/registro_repository.py`.
- [ ] T020 [P] Implementar repositorios de `Perfil`, `TarifaPerfil` y `AjusteHC` en `src/proyecta/infrastructure/datastore/perfil_repository.py`.
- [ ] T021 [P] Implementar repositorios de `Usuario`, `Sesion`, `Parametro` y `Catalogo` en `src/proyecta/infrastructure/datastore/config_repository.py`.
- [ ] T022 [P] Implementar repositorios de `Bitacora` y `EventoAuditoria` en `src/proyecta/infrastructure/datastore/audit_repository.py`.
- [ ] T023 [P] Implementar repositorios de `Corte` y `CorteDetalle` en `src/proyecta/infrastructure/datastore/corte_repository.py`.
- [ ] T024 Configurar índices compuestos y `datastore-indexes.xml` en `src/proyecta/infrastructure/datastore/indexes.py` según `data-model.md`.
- [ ] T025 Implementar hash y verificación Argon2id en `src/proyecta/infrastructure/auth/passwords.py`.
- [ ] T026 Implementar sesiones de servidor, expiración y bloqueo tras cinco intentos por cuenta e IP en `src/proyecta/infrastructure/auth/sessions.py`, persistiendo `intentos_fallidos` y `bloqueado_hasta` en `src/proyecta/infrastructure/datastore/config_repository.py`.
- [ ] T027 Implementar CSRF para formularios y HTMX en `src/proyecta/infrastructure/auth/csrf.py`.
- [ ] T028 Implementar políticas de rol y propiedad en `src/proyecta/domain/permissions.py`.
- [ ] T029 Implementar el servicio de auditoría por campo, con impacto MAB/Forecast, en `src/proyecta/application/services/audit.py`.
- [ ] T030 Implementar el servicio de parámetros, catálogos y alias en `src/proyecta/application/services/config.py`.
- [ ] T031 Implementar manejadores de error JSON y mapeo a `400/401/403/404/405/409/422` en `src/proyecta/interfaces/api/errors.py`.
- [ ] T032 Configurar logging estructurado y trazas en `src/proyecta/infrastructure/logging.py`.
- [ ] T033 Crear layout base, navegación por rol y pantalla de login en `src/proyecta/interfaces/web/templates/base.html` y `login.html`.
- [ ] T034 Crear el router `/api/v1` y el wiring de dependencias en `src/proyecta/interfaces/api/v1/router.py`.
- [ ] T035 Crear el esqueleto del generador sintético y los fixtures base en `src/proyecta/seed/synthetic.py`.
- [ ] T036 Crear pruebas de fundación (auth, bloqueo por intentos, auditoría, repositorios, configuración) en `tests/integration/test_foundation.py`.

**Checkpoint**: Fundación lista; las historias pueden comenzar.

---

## Phase 3: User Story 1 — Registrar y mantener una oportunidad o demanda (Priority: P1) 🎯 MVP

**Goal**: Alta, edición, perfiles, tarifas, observaciones y búsqueda de registros.

**Independent Test**: crear una oportunidad con dos perfiles, verificar código, estado, flujo, probabilidad, previsualización y evento de creación.

### Tests for User Story 1

> **NOTE: escribir primero y verificar que fallan.**

- [ ] T037 [P] [US1] Contrato de `/registros`, `/registros/{id}`, `/perfiles` y `/tarifas` en `tests/contract/test_registros.py`.
- [ ] T038 [P] [US1] Integración de alta con dos perfiles en `tests/integration/test_registro_create.py`.
- [ ] T039 [P] [US1] Unitarias de código, obligatorios y coherencia tipo/estado/flujo en `tests/unit/domain/test_registro_rules.py`.

### Implementation for User Story 1

- [ ] T040 [P] [US1] Generador de código `OPD-####` en `src/proyecta/domain/registro_code.py`.
- [ ] T041 [P] [US1] Validadores de registro, fechas y catálogos en `src/proyecta/domain/registro_rules.py`.
- [ ] T042 [US1] Caso de uso de alta, edición y cierre de registro en `src/proyecta/application/use_cases/registros.py`.
- [ ] T043 [US1] Casos de uso de perfiles, tarifas y ajustes en `src/proyecta/application/use_cases/perfiles.py`.
- [ ] T044 [US1] Rutas API de registros en `src/proyecta/interfaces/api/v1/registros.py`.
- [ ] T045 [US1] Rutas API de perfiles y tarifas en `src/proyecta/interfaces/api/v1/perfiles.py`.
- [ ] T046 [US1] Búsqueda, filtros y paginación en `src/proyecta/application/use_cases/registros.py`.
- [ ] T047 [P] [US1] Plantillas de alta y detalle con perfiles y tarifas en `src/proyecta/interfaces/web/templates/registros/form.html` y `detail.html`.
- [ ] T048 [P] [US1] Plantilla de listado con filtros en `src/proyecta/interfaces/web/templates/registros/list.html`.
- [ ] T049 [US1] Rutas web de alta, edición, detalle y listado en `src/proyecta/interfaces/web/routes/registros.py`.
- [ ] T050 [US1] Integrar auditoría de creación, edición, perfil y tarifa en `src/proyecta/application/use_cases/registros.py`.
- [ ] T051 [US1] Ejecutar la suite de US1 y corregir fallos en `tests/contract/test_registros.py` y `tests/integration/test_registro_create.py`.

**Checkpoint**: US1 funciona y es demostrable de forma independiente.

---

## Phase 4: User Story 2 — Avanzar el ciclo de vida, el flujo y la probabilidad (Priority: P1)

**Goal**: Transiciones válidas, probabilidad 100 % al adjudicar, pausa/reapertura y bitácora inmutable.

**Independent Test**: recorrer `Pendiente → Adjudicada → Perfiles seleccionados → En Curso` con P 100 %, auditoría y bitácora.

### Tests for User Story 2

- [ ] T052 [P] [US2] Contrato de `/estado`, `/flujo` y `/bitacora` en `tests/contract/test_estados.py`.
- [ ] T053 [P] [US2] Unitarias de la máquina de estados en `tests/unit/domain/test_states.py`.
- [ ] T054 [P] [US2] Integración del ciclo de vida en `tests/integration/test_lifecycle.py`.

### Implementation for User Story 2

- [ ] T055 [P] [US2] Máquina de estados y transiciones en `src/proyecta/domain/states.py`.
- [ ] T056 [P] [US2] Reglas de probabilidad y confiabilidad con vigencia mensual en `src/proyecta/domain/rules.py`.
- [ ] T057 [US2] Caso de uso de transición de estado y flujo en `src/proyecta/application/use_cases/estados.py`.
- [ ] T058 [US2] Caso de uso de bitácora y correcciones por referencia en `src/proyecta/application/use_cases/bitacora.py`.
- [ ] T059 [US2] Rutas API de estado, flujo y bitácora en `src/proyecta/interfaces/api/v1/estados.py` y `bitacora.py`.
- [ ] T060 [US2] Acciones web y bitácora en `src/proyecta/interfaces/web/routes/estados.py` y `templates/registros/bitacora.html`.
- [ ] T061 [US2] Integrar auditoría de estado, tipo, flujo, P y C en `src/proyecta/application/use_cases/estados.py`.
- [ ] T062 [US2] Pruebas de adjudicación al 100 %, StandBy, cancelación por motivo (AC-16) y transiciones inválidas en `tests/integration/test_lifecycle.py`.
- [ ] T063 [US2] Ejecutar la suite de US2 y corregir fallos en `tests/contract/test_estados.py` y `tests/integration/test_lifecycle.py`.

**Checkpoint**: US1 y US2 funcionan de forma independiente.

---

## Phase 5: User Story 3 — Calcular y explicar la proyección (Priority: P1)

**Goal**: Motor único de Base, MAB, Backlog, Forecast, HC y Gap, con series y detalle.

**Independent Test**: C-01 a C-08, serie de 12 meses y detalle de cada cifra.

### Tests for User Story 3

- [ ] T064 [P] [US3] Unitarias de C-01 a C-08 en `tests/unit/domain/test_engine_cases.py`.
- [ ] T065 [P] [US3] Unitarias de prorrateo y redondeo en `tests/unit/domain/test_engine_rounding.py`.
- [ ] T066 [P] [US3] Integración de la serie de 12 meses en `tests/integration/test_forecast.py`.

### Implementation for User Story 3

- [ ] T067 [P] [US3] Fracción activa por días en `src/proyecta/domain/engine/active_fraction.py`.
- [ ] T068 [P] [US3] Cálculo de Base mensual en `src/proyecta/domain/engine/base.py`.
- [ ] T069 [P] [US3] MAB, Backlog contractual, Backlog confirmado y Forecast en `src/proyecta/domain/engine/bags.py`.
- [ ] T070 [P] [US3] HC proyectado y grilla Altas/Bajas/Cierre en `src/proyecta/domain/engine/headcount.py`.
- [ ] T071 [P] [US3] Gap y cobertura en `src/proyecta/domain/engine/gap.py`.
- [ ] T072 [US3] Fachada del motor y contrato de resultados en `src/proyecta/domain/engine/service.py`.
- [ ] T073 [US3] Resolución de vigencias de P, C y horas en `src/proyecta/domain/engine/vigencias.py`.
- [ ] T074 [US3] Caso de uso de cálculo y previsualización en `src/proyecta/application/use_cases/calculo.py`.
- [ ] T075 [US3] Rutas API de forecast y detalle en `src/proyecta/interfaces/api/v1/forecast.py`.
- [ ] T076 [US3] Plantilla de serie y detalle de cálculo en `src/proyecta/interfaces/web/templates/registros/calculo.html`.
- [ ] T077 [US3] Integrar impacto MAB/Forecast en la auditoría en `src/proyecta/application/services/audit.py`.
- [ ] T078 [US3] Pruebas de horas con vigencia (AC-17) y P/C con vigencia en `tests/integration/test_forecast.py`.
- [ ] T079 [US3] Ejecutar la suite de US3 y corregir fallos en `tests/unit/domain/test_engine_cases.py` y `tests/integration/test_forecast.py`.

**Checkpoint**: US3 funciona de forma independiente y el motor es reutilizable.

---

## Phase 6: User Story 4 — Consultar el dashboard ejecutivo (Priority: P1)

**Goal**: 11 indicadores, filtros, detalle y proyección de lectura.

**Independent Test**: dashboard con datos sintéticos, filtros combinables y cada cifra abierta hasta sus registros.

### Tests for User Story 4

- [ ] T080 [P] [US4] Contrato de `/dashboard` en `tests/contract/test_dashboard.py`.
- [ ] T081 [P] [US4] Integración de totales, filtros y detalle en `tests/integration/test_dashboard.py`.

### Implementation for User Story 4

- [ ] T082 [P] [US4] Repositorio y proyección `ResumenMensual` en `src/proyecta/infrastructure/datastore/dashboard_repository.py`.
- [ ] T083 [P] [US4] Servicio de agregación del dashboard en `src/proyecta/application/use_cases/dashboard.py`.
- [ ] T084 [US4] Ruta API de dashboard en `src/proyecta/interfaces/api/v1/dashboard.py`.
- [ ] T085 [US4] Filtros y totales sobre registros visibles en `src/proyecta/application/use_cases/dashboard.py`.
- [ ] T086 [P] [US4] Plantilla del dashboard con los 11 datos en `src/proyecta/interfaces/web/templates/dashboard/index.html`.
- [ ] T087 [P] [US4] Componentes Chart.js y series en `src/proyecta/interfaces/web/static/js/dashboard.js`.
- [ ] T088 [US4] Parciales de detalle y navegación hasta el registro en `src/proyecta/interfaces/web/templates/dashboard/detail.html`.
- [ ] T089 [US4] Comando de reconstrucción de `ResumenMensual` en `scripts/rebuild_resumen.py`.
- [ ] T090 [US4] Prueba de rendimiento con 1.000 registros y 300 activos en `tests/integration/test_dashboard_perf.py`.
- [ ] T091 [US4] Ejecutar la suite de US4 y corregir fallos en `tests/contract/test_dashboard.py` y `tests/integration/test_dashboard.py`.

**Checkpoint**: US1–US4 forman el MVP demostrable.

---

## Phase 7: User Story 5 — Gestionar Backlog, metas y gap (Priority: P1b)

**Goal**: Contratos de continuidad, vencimientos, metas por sector/mes, gap y cobertura.

**Independent Test**: contrato de continuidad con Backlog mensual, meta y gap correctos.

### Tests for User Story 5

- [ ] T092 [P] [US5] Contrato de `/contratos` y `/metas` en `tests/contract/test_backlog_metas.py`.
- [ ] T093 [P] [US5] Unitarias de gap y cobertura en `tests/unit/domain/test_gap.py`.
- [ ] T094 [P] [US5] Integración de continuidad y Backlog en `tests/integration/test_backlog.py`.

### Implementation for User Story 5

- [ ] T095 [US5] Caso de uso de contrato, renovación y cierre en `src/proyecta/application/use_cases/backlog.py`.
- [ ] T096 [US5] Caso de uso de metas por sector/mes en `src/proyecta/application/use_cases/metas.py`.
- [ ] T097 [US5] Cálculo de Backlog contractual y vencimientos en `src/proyecta/application/use_cases/backlog.py`.
- [ ] T098 [US5] Cálculo de gap y cobertura en `src/proyecta/application/use_cases/metas.py`.
- [ ] T099 [US5] Rutas API de contratos y metas en `src/proyecta/interfaces/api/v1/contratos.py` y `metas.py`.
- [ ] T100 [P] [US5] Plantilla de contrato en `src/proyecta/interfaces/web/templates/contratos/form.html`.
- [ ] T101 [P] [US5] Plantilla de metas y gap en `src/proyecta/interfaces/web/templates/metas/index.html`.
- [ ] T102 [US5] Alertas de vencimiento y `DQ-12` en `src/proyecta/application/use_cases/backlog.py`.
- [ ] T103 [US5] Pruebas de alertas, meta faltante y contrato vencido en `tests/integration/test_backlog.py`.
- [ ] T104 [US5] Ejecutar la suite de US5 y corregir fallos en `tests/contract/test_backlog_metas.py` y `tests/integration/test_backlog.py`.

**Checkpoint**: US5 agrega Backlog, metas y gap sin romper el MVP.

---

## Phase 8: User Story 6 — Cerrar el período y explicar la variación (Priority: P2)

**Goal**: Corte congelado, cierre por lotes, comparación y puente por causa.

**Independent Test**: dos cortes consecutivos con puente cuya suma coincide con la variación.

### Tests for User Story 6

- [ ] T105 [P] [US6] Contrato de `/cortes` y `/puente` en `tests/contract/test_cortes.py`.
- [ ] T106 [P] [US6] Unitarias del puente por categoría en `tests/unit/domain/test_puente.py`.
- [ ] T107 [P] [US6] Integración de cierre e idempotencia en `tests/integration/test_cierre.py`.

### Implementation for User Story 6

- [ ] T108 [US6] Repositorio de corte y detalle en `src/proyecta/infrastructure/datastore/corte_repository.py`.
- [ ] T109 [US6] Servicio de cierre por lotes con estados `CREANDO`/`CERRADO`/`ERROR` en `src/proyecta/application/use_cases/cierre.py`.
- [ ] T110 [US6] Cálculo del puente en `src/proyecta/domain/engine/puente.py`.
- [ ] T111 [US6] Rutas API de cortes y puente en `src/proyecta/interfaces/api/v1/cortes.py`.
- [ ] T112 [US6] Plantilla de cortes y comparación en `src/proyecta/interfaces/web/templates/cortes/index.html`.
- [ ] T113 [US6] Inmutabilidad del corte cerrado y reintento idempotente en `src/proyecta/application/use_cases/cierre.py`.
- [ ] T114 [US6] Pruebas de AC-08 y línea de redondeo en `tests/integration/test_cierre.py`.
- [ ] T115 [US6] Ejecutar la suite de US6 y corregir fallos en `tests/contract/test_cortes.py` y `tests/integration/test_cierre.py`.

**Checkpoint**: US6 produce cortes reproducibles y un puente explicable.

---

## Phase 9: User Story 7 — Evaluar la calidad del dato (Priority: P2)

**Goal**: `DQ-01` a `DQ-13`, semáforo y pendientes por rol.

**Independent Test**: registro rojo, amarillo y verde; pendientes del líder y de Operaciones.

### Tests for User Story 7

- [ ] T116 [P] [US7] Unitarias de las reglas DQ en `tests/unit/domain/test_quality.py`.
- [ ] T117 [P] [US7] Integración del panel de calidad en `tests/integration/test_quality.py`.

### Implementation for User Story 7

- [ ] T118 [P] [US7] Reglas `DQ-01` a `DQ-13` en `src/proyecta/domain/quality.py`.
- [ ] T119 [US7] Servicio de calidad, semáforo y pendientes en `src/proyecta/application/use_cases/calidad.py`.
- [ ] T120 [US7] Ruta API de calidad en `src/proyecta/interfaces/api/v1/calidad.py`.
- [ ] T121 [US7] Panel de calidad y alertas en `src/proyecta/interfaces/web/templates/calidad/index.html`.
- [ ] T122 [US7] Pruebas de `DQ-06`, `DQ-07`, `DQ-08` y `DQ-12` en `tests/integration/test_quality.py`.
- [ ] T123 [US7] Ejecutar la suite de US7 y corregir fallos en `tests/unit/domain/test_quality.py` y `tests/integration/test_quality.py`.

**Checkpoint**: La calidad del dato es visible y accionable.

---

## Phase 10: User Story 8 — Auditar cambios y controlar el acceso (Priority: P2)

**Goal**: Auditoría consultable, permisos por rol/propiedad y usuarios.

**Independent Test**: cambios auditados con impacto; `403` entre líderes; `405` en auditoría; `409` por versión.

### Tests for User Story 8

- [ ] T124 [P] [US8] Contrato de auditoría y usuarios en `tests/contract/test_auditoria.py`.
- [ ] T125 [P] [US8] Integración de `403`, `405` y `409` en `tests/integration/test_permissions_audit.py`.

### Implementation for User Story 8

- [ ] T126 [US8] Consulta y exportación de auditoría en `src/proyecta/application/use_cases/auditoria.py`.
- [ ] T127 [US8] Ruta API de auditoría en `src/proyecta/interfaces/api/v1/auditoria.py`.
- [ ] T128 [US8] Pantalla de auditoría en `src/proyecta/interfaces/web/templates/registros/auditoria.html`.
- [ ] T129 [US8] Administración de usuarios y roles, sin permitir desactivar al último usuario de Operaciones (FR-065), en `src/proyecta/application/use_cases/usuarios.py`.
- [ ] T130 [US8] Rutas API y pantalla de usuarios en `src/proyecta/interfaces/api/v1/usuarios.py` y `templates/usuarios/index.html`.
- [ ] T131 [US8] Aplicar políticas de rol/propiedad, incluido impedir que un líder cambie su propio rol o el de otra persona (FR-064), en `src/proyecta/domain/permissions.py`.
- [ ] T132 [US8] Rechazo `405` en bitácora/auditoría y `409` por versión en `src/proyecta/interfaces/api/errors.py`.
- [ ] T133 [US8] Ejecutar la suite de US8 y corregir fallos en `tests/contract/test_auditoria.py` y `tests/integration/test_permissions_audit.py`.

**Checkpoint**: La fuente es auditable y el acceso está controlado.

---

## Phase 11: User Story 9 — Reportar y exportar (Priority: P2)

**Goal**: Reportes `R-01` a `R-13` y exportación `.xlsx` con filtros, permisos y sanitización.

**Independent Test**: exportar pipeline y auditoría; verificar filtros, permisos y celdas sanitizadas.

### Tests for User Story 9

- [ ] T134 [P] [US9] Contrato de exportación en `tests/contract/test_export.py`.
- [ ] T135 [P] [US9] Integración de `.xlsx`, permisos e inyección de fórmulas en `tests/integration/test_export.py`.

### Implementation for User Story 9

- [ ] T136 [US9] Escritor `.xlsx` en streaming en `src/proyecta/infrastructure/export/xlsx.py`.
- [ ] T137 [US9] Consultas de reportes `R-01` a `R-13` en `src/proyecta/application/use_cases/reportes.py`.
- [ ] T138 [US9] Rutas API de exportación en `src/proyecta/interfaces/api/v1/exportaciones.py`.
- [ ] T139 [US9] Botones y enlaces de exportación en `src/proyecta/interfaces/web/templates/dashboard/index.html` y `registros/list.html`.
- [ ] T140 [US9] Sanitización de fórmulas y filtrado por owner en `src/proyecta/infrastructure/export/xlsx.py`.
- [ ] T141 [US9] Ejecutar la suite de US9 y corregir fallos en `tests/contract/test_export.py` y `tests/integration/test_export.py`.

**Checkpoint**: Los reportes y la exportación están disponibles sin fugas de datos.

---

## Phase 12: User Story 10 — Recibir sugerencias de IA y simular escenarios (Priority: P2b)

**Goal**: Sugerencias con cita y aprobación, simulación aislada, sin escritura autónoma.

**Independent Test**: sugerencia aceptada con auditoría `IA`; simulación sin persistencia ni cambio de estados.

### Tests for User Story 10

- [ ] T142 [P] [US10] Integración de sugerencias y simulación en `tests/integration/test_ia_sim.py`.

### Implementation for User Story 10

- [ ] T143 [P] [US10] Puerto de IA y adaptador Vertex AI en `src/proyecta/infrastructure/ai/vertex.py`.
- [ ] T144 [US10] Caso de uso de sugerencias con cita y aprobación en `src/proyecta/application/use_cases/ia.py`.
- [ ] T145 [US10] Caso de uso de simulación en memoria en `src/proyecta/application/use_cases/simulacion.py`.
- [ ] T146 [US10] Rutas API de IA y simulación en `src/proyecta/interfaces/api/v1/ia.py`.
- [ ] T147 [US10] Pantalla opcional de sugerencias en `src/proyecta/interfaces/web/templates/sugerencias/index.html`.
- [ ] T148 [US10] Pruebas de no escritura, etiquetas y funcionamiento sin IA en `tests/integration/test_ia_sim.py`.
- [ ] T149 [US10] Ejecutar la suite de US10 y corregir fallos en `tests/integration/test_ia_sim.py`.

**Checkpoint**: La IA y la simulación agregan valor sin comprometer la integridad.

---

## Phase 13: User Story 11 — Cargar los datos iniciales (Priority: P3)

**Goal**: Semilla sintética y carga de estructura con errores por fila; sin datos reales.

**Independent Test**: cargar un fixture de cuatro registros sintéticos, recalcular a 180 h y reportar inconsistencias.

### Tests for User Story 11

- [ ] T150 [P] [US11] Integración de la carga sintética en `tests/integration/test_seed.py`.

### Implementation for User Story 11

- [ ] T151 [US11] Generador de 1.000 registros sintéticos en `src/proyecta/seed/synthetic.py`.
- [ ] T152 [US11] Fixture de cuatro registros con inconsistencias en `src/proyecta/seed/fixtures.py`.
- [ ] T153 [US11] Cargador idempotente con errores por fila en `src/proyecta/application/use_cases/carga.py`.
- [ ] T154 [US11] CLI de carga en `scripts/seed_synthetic.py`.
- [ ] T155 [US11] Pruebas de idempotencia y ausencia de datos reales en `tests/integration/test_seed.py`.
- [ ] T156 [US11] Ejecutar la suite de US11 y corregir fallos en `tests/integration/test_seed.py`.

**Checkpoint**: La demo arranca con datos sintéticos reproducibles.

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Endurecimiento, evidencia y demo.

- [ ] T157 [P] Prueba de carga con 5.000 registros y 50 concurrentes; ajustar índices y proyección en `tests/integration/test_load.py`.
- [ ] T158 [P] Auditoría de accesibilidad con axe y correcciones en `src/proyecta/interfaces/web/templates/base.html` y `dashboard/index.html`.
- [ ] T159 Revisión de seguridad OWASP/ASVS, CSRF, sesión y secretos en `deploy/Dockerfile`, `src/proyecta/infrastructure/auth/sessions.py` y `csrf.py`.
- [ ] T160 [P] Completar logging, métricas y alertas en `src/proyecta/infrastructure/logging.py`.
- [ ] T161 [P] Documentar respaldo, restauración y retención en `docs/operacion.md`.
- [ ] T162 [P] Completar README, manual de usuario, ADR y guion de demo en `docs/manual.md`, `docs/adr/001-stack.md` y `docs/demo.md`.
- [ ] T163 Verificar cobertura ≥ 90 % del dominio y pipeline en verde en `pyproject.toml` y `deploy/cloudbuild.yaml`.
- [ ] T164 Ejecutar los escenarios V-01 a V-14 de `specs/001-proyecta-mvp/quickstart.md` y registrar evidencia.
- [ ] T165 Preparar semilla y guion de demo con datos sintéticos en `scripts/seed_synthetic.py` y `docs/demo.md`.
- [ ] T166 Revisar la Constitution Check final y el checklist de requisitos en `.specify/memory/constitution.md` y `specs/001-proyecta-mvp/checklists/requirements-quality.md`.
- [ ] T167 Actualizar `docs/fuentes/requerimientos.md` con H-01, H-04 y H-05 antes de la firma del sponsor.
- [ ] T168 Verificar disponibilidad 99,5 %, RTO 4 h y RPO 24 h con simulación de restauración en `tests/integration/test_availability.py`.
- [ ] T169 Verificar retención de cinco años y ausencia de TTL/borrado en `tests/integration/test_retention.py` y `src/proyecta/infrastructure/datastore/audit_repository.py`.
- [ ] T170 [P] Prueba de compatibilidad Chrome/Edge de las últimas dos versiones y responsive desde 360 px en `tests/e2e/test_compatibility.py`.
- [ ] T171 [P] Verificar es-CL, fechas `dd-mm-aaaa`, montos CLP y porcentajes con coma decimal en `tests/e2e/test_localization.py`.
- [ ] T172 [P] Verificar fechas de negocio sin hora y eventos UTC mostrados en America/Santiago en `tests/integration/test_timezone.py`.
- [ ] T173 [P] Configurar presupuesto y alertas de costo USD 10–30 en `deploy/billing-alerts.yaml` y `docs/costos.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup; bloquea todas las historias.
- **US1–US4 (P1)**: dependen de Foundational. US2 puede comenzar con fixtures, pero su extremo a extremo depende de US1; US3 depende de US1/US2; US4 depende de US3.
- **US5 (P1b)**: depende de US1 y US3.
- **US6 (P2)**: depende de US3 y US5.
- **US7 (P2)**: depende de US1 y US2.
- **US8 (P2)**: depende de US1 y de la auditoría de US2.
- **US9 (P2)**: depende de US4 y US6.
- **US10 (P2b)**: depende de US3; es opcional.
- **US11 (P3)**: depende de US1; es opcional para la demo.
- **Polish**: depende de las historias comprometidas.

### User Story Dependencies

- **US1**: sin dependencias de otras historias.
- **US2**: integra con US1; se prueba con fixtures de registros.
- **US3**: integra con US1/US2; usa fixtures para los casos C-01 a C-08.
- **US4**: requiere el motor de US3 y los datos de US1.
- **US5**: requiere US1 y US3.
- **US6**: requiere US3 y US5.
- **US7**: requiere US1 y US2.
- **US8**: requiere US1 y la auditoría de US2.
- **US9**: requiere US4 y US6.
- **US10**: requiere US3; no bloquea el MVP.
- **US11**: requiere US1; no bloquea el MVP.

### Within Each User Story

- Pruebas primero y fallando.
- Enums/value objects/entidades antes de servicios.
- Servicios antes de rutas.
- Rutas antes de plantillas.
- Auditoría integrada en el caso de uso, no al final.
- Cerrar la historia con su suite en verde.

### Parallel Opportunities

- Setup: T003–T010 en paralelo.
- Foundational: T020–T023 y T025–T027 en paralelo; T014/T015 comparten archivo y no son [P].
- US1: T037–T039 en paralelo; T040/T041 en paralelo; T047/T048 en paralelo.
- US2: T052–T054 en paralelo; T055/T056 en paralelo.
- US3: T064–T066 en paralelo; T067–T071 en paralelo.
- US4: T080/T081 en paralelo; T082/T083 en paralelo; T086/T087 en paralelo.
- US5: T092–T094 en paralelo; T095/T096 en paralelo; T100/T101 en paralelo.
- US6: T105–T107 en paralelo; T108/T110 en paralelo.
- US7: T116/T117 en paralelo; T118/T119 en paralelo.
- US8: T124/T125 en paralelo; T126/T129 en paralelo.
- US9: T134/T135 en paralelo; T136/T137 en paralelo.
- US10: T142/T143 en paralelo; T144/T145 en paralelo.
- US11: T150/T152 en paralelo; T151/T153 en paralelo.

---

## Parallel Example: User Story 3

```bash
# Pruebas del motor en paralelo
Task: "Unitarias de C-01 a C-08 en tests/unit/domain/test_engine_cases.py"
Task: "Unitarias de prorrateo y redondeo en tests/unit/domain/test_engine_rounding.py"
Task: "Integración de la serie de 12 meses en tests/integration/test_forecast.py"

# Módulos del motor en paralelo (archivos distintos)
Task: "Fracción activa en src/proyecta/domain/engine/active_fraction.py"
Task: "Base mensual en src/proyecta/domain/engine/base.py"
Task: "Bolsas y Forecast en src/proyecta/domain/engine/bags.py"
Task: "HC proyectado en src/proyecta/domain/engine/headcount.py"
Task: "Gap y cobertura en src/proyecta/domain/engine/gap.py"
```

---

## Implementation Strategy

### MVP First (US1–US4)

1. Completar Phase 1 (Setup).
2. Completar Phase 2 (Foundational).
3. Completar US1 → validar alta, perfiles y auditoría.
4. Completar US2 → validar ciclo de vida y P 100 % al adjudicar.
5. Completar US3 → validar C-01 a C-08 y series.
6. Completar US4 → validar dashboard y detalle.
7. **STOP and VALIDATE**: demo del MVP con datos sintéticos.

### Incremental Delivery

1. US5 → Backlog, metas y gap.
2. US6 → cierre y puente.
3. US7 → calidad del dato.
4. US8 → auditoría y permisos.
5. US9 → reportes y exportación.
6. US10 y US11 → opcionales, sin bloquear la demo.

### Parallel Team Strategy

1. El equipo completa Setup + Foundational.
2. Luego:
   - Persona A: US1 + US2.
   - Persona B: US3 + US4.
   - Persona C: US5 + US6.
   - Persona D: US7 + US8 + US9.
3. US10 y US11 se asignan solo si hay holgura.
4. Integrar por historia, no por capa.

---

## Requirement Traceability

| Requirement | Tasks |
|---|---|
| FR-001–FR-010 | T037–T051 |
| FR-011–FR-017 | T043, T070 |
| FR-018–FR-028 | T052–T063 |
| FR-029–FR-038 | T064–T079 |
| FR-039–FR-045 | T092–T104 |
| FR-046–FR-052 | T080–T091, T137 |
| FR-053–FR-060 | T052–T063, T124–T133 |
| FR-061–FR-067 | T025–T028, T129–T131 (FR-066 en T026) |
| FR-068–FR-072 | T116–T123 |
| FR-073–FR-077 | T105–T115 |
| FR-078–FR-081 | T134–T141 |
| FR-082–FR-086 | T142–T149 |
| FR-087–FR-090 | T150–T156 |

## Notes

- `[P]` significa archivos distintos y sin dependencia de una tarea incompleta.
- `[Story]` traza la tarea a la historia de usuario; no reemplaza el `FR`/`AC`.
- Cada historia debe quedar demostrable por sí sola; las dependencias reales están en la sección anterior.
- No hay migración real en el MVP: la carga inicial es sintética (`H-05`).
- La IA y la simulación son opcionales; si fallan, el MVP sigue operando.
- Las decisiones `S-xx` siguen abiertas: no convertir sus valores en supuestos de implementación.
- Antes de la firma del sponsor, actualizar `requerimientos.md` con `H-01`, `H-04` y `H-05`.
