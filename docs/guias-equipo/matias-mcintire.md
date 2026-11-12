# Matías Mcintire — Arquitectura y seguridad

## Resultado esperado

Entregar una base instalable, una aplicación que arranque y los adaptadores necesarios para integrar el trabajo del equipo.

**Tareas base:** T001–T011, T018–T027, T030–T032, T034 y T159. **Complementarias propuestas:** T160 y T173. Lee [el flujo común](README.md), `AGENTS.md`, `docs/equipo.md` y los documentos del frente. Las rutas parten de la raíz.

## Archivos y contenidos

Los archivos siguientes son entregables previstos; inspecciona cuáles existen antes de crearlos. En las filas con nombres abreviados, estos comparten el directorio del primer archivo.

| Archivo o grupo | Contenido esperado |
|---|---|
| `pyproject.toml` | Python 3.12, dependencias, extras dev, Ruff, mypy, pytest y cobertura del dominio ≥90 %. |
| `deploy/Dockerfile`; `deploy/.dockerignore` | Imagen Linux reproducible y exclusiones de archivos locales/secretos. |
| `deploy/cloudbuild.yaml`; `deploy/service.yaml` | Pipeline de lint/pruebas/cobertura y configuración de Cloud Run. |
| `src/proyecta/config.py`; `.env.example` | Variables por entorno, validación y ejemplos sin secretos reales. |
| `src/proyecta/main.py`; `src/proyecta/interfaces/api/v1/router.py` | App FastAPI, `/health`, montaje de routers e inyección de dependencias. |
| `src/proyecta/infrastructure/datastore/mappings.py` | Serialización de entidades, dinero, fechas y versiones. |
| `src/proyecta/infrastructure/datastore/registro_repository.py`; `perfil_repository.py` | Persistencia de registros y de perfiles/tarifas/ajustes. |
| `src/proyecta/infrastructure/datastore/config_repository.py`; `audit_repository.py`; `corte_repository.py` | Usuarios/sesiones/parámetros/catálogos, bitácora/auditoría y cortes/detalles. |
| `src/proyecta/infrastructure/datastore/indexes.py` | Índices según el modelo. T024 también pide `datastore-indexes.xml`: acordar y documentar su ubicación, no explicitada en esa tarea. |
| `src/proyecta/infrastructure/auth/passwords.py`; `sessions.py`; `csrf.py` | Argon2id, sesiones/expiración, bloqueo por cuenta e IP y CSRF para formularios/HTMX. |
| `src/proyecta/application/services/config.py`; `src/proyecta/interfaces/api/errors.py` | Parámetros/catálogos/alias y traducción de errores a códigos HTTP estables. |
| `src/proyecta/infrastructure/logging.py` | Logging estructurado, trazas, métricas y alertas sin información sensible. |
| `src/proyecta/interfaces/web/static/css/app.css`; `src/proyecta/interfaces/web/static/js/app.js` | Recursos comunes locales; coordinar su uso con Bryam. |
| `tests/conftest.py`; `README.md` | Fixtures compartidos y pasos verificables de instalación, configuración y pruebas. |
| `docs/adr/001-stack.md`; `002-sesiones.md`; `003-auditoria.md`; `004-cierre.md` | Contexto, decisión, consecuencias y referencias, redactados con los responsables de cada frente. |
| `deploy/billing-alerts.yaml`; `docs/costos.md` | Propuesta de presupuesto y alertas USD 10–30, supuestos y parámetros del proyecto GCP. |

## Orden de ejecución

1. Completa Setup T001–T011 conservando el esqueleto existente. Coordina T009 con Roberto y T008 con Bryam.
2. Acuerda entidades y puertos con Nicolás antes de finalizar mapeos y repositorios T018–T024.
3. Implementa autenticación, configuración y errores. Integra las políticas de Felipe y la auditoría de Roberto.
4. Demuestra el checkpoint de Fundación con el equipo: app, sesión, repositorios, layout y pruebas conectados.
5. Ejecuta T159 con revisión de Roberto. Completa observabilidad y propuesta de costos durante el endurecimiento.

Preparar configuración de despliegue no acredita que el servicio esté desplegado. Registra qué validaste localmente y qué requiere un entorno GCP.

## Validación y entrega

Tras implementar la configuración correspondiente, ejecuta desde la raíz:

```powershell
uv sync --extra dev
uv run ruff check .
uv run mypy src/proyecta
uv run pytest tests/integration/test_foundation.py -q
uv run pytest --cov=proyecta.domain --cov-fail-under=90
```

La cobertura global se exige al integrar el dominio; no declares Fundación validada si sus pruebas aún no existen. Comprueba `/health`, login, bloqueo, expiración y CSRF con Roberto. Entrega al equipo instrucciones de arranque, variables, fixtures y dependencias conectadas. Nicolás revisa mapeos; Felipe, políticas.

## Prompt personal para una IA

Añade al prompt común del índice:

```text
Soy Matías Mcintire, responsable de arquitectura y seguridad.
Lee docs/guias-equipo/matias-mcintire.md.
Primer lote: T002, después de comprobar el estado de T001.
Configura pyproject.toml con el stack de plan.md y extras de desarrollo.
Conserva la estructura existente y verifica instalación si el entorno lo permite.
Explica qué queda pendiente de T003 y qué necesitan los demás integrantes.
No presentes la aplicación ni el pipeline como terminados por crear el manifiesto.
```

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T001**: Crear la estructura `src/proyecta/{domain,application,infrastructure,interfaces,seed}`, `tests/{unit/domain,integration,contract,e2e}`, `scripts/` y `deploy/` según `plan.md`.
- **T002**: Inicializar `pyproject.toml` con Python 3.12, FastAPI, Uvicorn, Pydantic v2, Jinja2, `google-cloud-datastore`, `google-cloud-secret-manager`, `google-cloud-logging`, `argon2-cffi`, `openpyxl` y extras de desarrollo.
- **T003**: Configurar `ruff`, `pytest`, `pytest-cov` y `mypy` en `pyproject.toml` con umbral de cobertura del dominio en 90 %.
- **T004**: [P] Crear `deploy/Dockerfile` y `deploy/.dockerignore` para una imagen Linux reproducible.
- **T005**: [P] Crear `deploy/cloudbuild.yaml` y `deploy/service.yaml` con variables de entorno, puerto y límites de Cloud Run.
- **T006**: [P] Crear `src/proyecta/config.py` y `.env.example` para `DATASTORE_EMULATOR_HOST`, `GOOGLE_CLOUD_PROJECT`, `PROYECTA_ENV`, `PROYECTA_SECRET_KEY` y `PROYECTA_AI_ENABLED`.
- **T007**: [P] Crear `src/proyecta/main.py` con la app FastAPI, el montaje de routers y `/health`.
- **T008**: [P] Crear `src/proyecta/interfaces/web/static/css/app.css` y `js/app.js` con Bootstrap, HTMX y Chart.js servidos localmente.
- **T009**: [P] Crear `tests/conftest.py` con fixtures de app, cliente HTTP, repositorios y emulador de Datastore.
- **T010**: [P] Crear `README.md` con requisitos, instalación, variables de entorno, comandos de prueba y advertencia de datos sintéticos.
- **T011**: Crear el pipeline de CI en `deploy/cloudbuild.yaml` que ejecute lint, pruebas y cobertura antes de desplegar.
- **T018**: Implementar serialización y mapeo Datastore de entidades en `src/proyecta/infrastructure/datastore/mappings.py`.
- **T019**: Implementar el repositorio de `Registro` en `src/proyecta/infrastructure/datastore/registro_repository.py`.
- **T020**: [P] Implementar repositorios de `Perfil`, `TarifaPerfil` y `AjusteHC` en `src/proyecta/infrastructure/datastore/perfil_repository.py`.
- **T021**: [P] Implementar repositorios de `Usuario`, `Sesion`, `Parametro` y `Catalogo` en `src/proyecta/infrastructure/datastore/config_repository.py`.
- **T022**: [P] Implementar repositorios de `Bitacora` y `EventoAuditoria` en `src/proyecta/infrastructure/datastore/audit_repository.py`.
- **T023**: [P] Implementar repositorios de `Corte` y `CorteDetalle` en `src/proyecta/infrastructure/datastore/corte_repository.py`.
- **T024**: Configurar índices compuestos y `datastore-indexes.xml` en `src/proyecta/infrastructure/datastore/indexes.py` según `data-model.md`.
- **T025**: Implementar hash y verificación Argon2id en `src/proyecta/infrastructure/auth/passwords.py`.
- **T026**: Implementar sesiones de servidor, expiración y bloqueo tras cinco intentos por cuenta e IP en `src/proyecta/infrastructure/auth/sessions.py`, persistiendo `intentos_fallidos` y `bloqueado_hasta` en `src/proyecta/infrastructure/datastore/config_repository.py`.
- **T027**: Implementar CSRF para formularios y HTMX en `src/proyecta/infrastructure/auth/csrf.py`.
- **T030**: Implementar el servicio de parámetros, catálogos y alias en `src/proyecta/application/services/config.py`.
- **T031**: Implementar manejadores de error JSON y mapeo a `400/401/403/404/405/409/422` en `src/proyecta/interfaces/api/errors.py`.
- **T032**: Configurar logging estructurado y trazas en `src/proyecta/infrastructure/logging.py`.
- **T034**: Crear el router `/api/v1` y el wiring de dependencias en `src/proyecta/interfaces/api/v1/router.py`.
- **T159**: Revisión de seguridad OWASP/ASVS, CSRF, sesión y secretos en `deploy/Dockerfile`, `src/proyecta/infrastructure/auth/sessions.py` y `csrf.py`.
- **T160** **(asignación complementaria propuesta)**: [P] Completar logging, métricas y alertas en `src/proyecta/infrastructure/logging.py`.
- **T173** **(asignación complementaria propuesta)**: [P] Configurar presupuesto y alertas de costo USD 10–30 en `deploy/billing-alerts.yaml` y `docs/costos.md`.
