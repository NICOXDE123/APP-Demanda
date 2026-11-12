# Roberto Villouta — Seguridad y QA

## Resultado esperado

Construir auditoría y controles de acceso de US8, y mantener evidencia reproducible de calidad, seguridad y operación. Cada integrante sigue siendo responsable de probar su implementación.

**Tareas base:** T029, T036, T124–T133, T157–T158, T163 y T168–T169. **Revisión compartida:** T159, implementada por Matías. **Complementarias propuestas:** T161 y T172. Lee [el flujo común](README.md), `AGENTS.md` y los documentos del frente. Las rutas parten de la raíz.

## Archivos y contenidos

Son entregables previstos. Los nombres abreviados de una fila comparten el directorio del primer archivo, salvo ruta explícita.

| Archivo o grupo | Contenido esperado |
|---|---|
| `src/proyecta/application/services/audit.py` | Eventos por campo con anterior/nuevo, usuario, fecha, motivo e impacto. Nicolás integra el cálculo en T077. |
| `tests/integration/test_foundation.py` | Autenticación, bloqueo, repositorios, configuración y auditoría base. |
| `src/proyecta/application/use_cases/auditoria.py`; `usuarios.py` | Consulta/exportación de auditoría y gestión de usuarios, sin desactivar al último Operaciones. |
| `src/proyecta/interfaces/api/v1/auditoria.py`; `usuarios.py` | Endpoints protegidos de consulta y administración. |
| `src/proyecta/interfaces/web/templates/registros/auditoria.html`; `src/proyecta/interfaces/web/templates/usuarios/index.html` | Historial consultable y gestión de usuarios; coordinar presentación con Bryam. |
| `src/proyecta/domain/permissions.py`; `src/proyecta/interfaces/api/errors.py` | Ampliar políticas de Felipe y errores de Matías: impedir escalamiento de rol, rechazar modificaciones de auditoría/bitácora y detectar conflictos de versión. |
| `tests/contract/test_auditoria.py`; `tests/integration/test_permissions_audit.py` | Contrato, acceso entre líderes, 403, inmutabilidad 405 y concurrencia 409. |
| `tests/integration/test_load.py`; `test_availability.py`; `test_retention.py`; `test_timezone.py` | Carga 5.000/50 concurrentes, restauración RTO/RPO, retención de cinco años y fechas/eventos UTC. |
| `src/proyecta/infrastructure/datastore/audit_repository.py` | Revisión/ajustes T169: ausencia de TTL o borrado incompatibles con retención. |
| `src/proyecta/interfaces/web/templates/base.html`; `dashboard/index.html` | Dentro de templates/: correcciones de accesibilidad T158 con Bryam y Leonardo. |
| `deploy/Dockerfile`; `src/proyecta/infrastructure/auth/sessions.py`; `csrf.py` | Revisar T159 con Matías; `csrf.py` está en infrastructure/auth/. Matías conserva la implementación principal. |
| `pyproject.toml`; `deploy/cloudbuild.yaml` | Comprobar cobertura del dominio ≥90 % y pipeline verde en T163. |
| `docs/operacion.md` | Respaldo, restauración, retención, responsables y resultados de ensayos. |
| `docs/evidencias/qa.md` | Archivo propuesto: versión, entorno, comandos, resultados reales, mediciones, defectos y limitaciones. |

## Orden de ejecución

1. Durante Fundación implementa T029 y T036 con Matías; acuerda cómo emiten auditoría los casos de uso y cómo Nicolás aporta el impacto.
2. Acompaña US1 en adelante con pruebas de roles, validación, concurrencia y errores esperados.
3. Con US1 y auditoría de US2 disponibles, implementa US8: consulta, usuarios y refuerzo de permisos.
4. Revisa T159 con Matías y coordina T158 con los autores de las plantillas. Cada corrección debe conservar su prueba de regresión.
5. Ejecuta carga, cobertura, restauración, retención y zonas horarias cuando exista el entorno; documenta bloqueos reales.

## Validación y entrega

Además del camino exitoso, comprueba 403/404/405/409/422 por rol y estado. Retención de cinco años se verifica con configuración y pruebas controladas. El ensayo debe medir RTO 4 h/RPO 24 h; documenta el alcance de la evidencia de disponibilidad 99,5 % sin convertir un test breve en un SLA acreditado.

Con tareas y entorno disponibles:

```powershell
uv run pytest tests/integration/test_foundation.py tests/contract/test_auditoria.py tests/integration/test_permissions_audit.py -q
uv run pytest --cov=proyecta.domain --cov-fail-under=90
uv run pytest tests/integration/test_load.py tests/integration/test_availability.py tests/integration/test_retention.py tests/integration/test_timezone.py -q
uv run pytest tests/e2e -k accessibility -q
```

La última selección requiere pruebas E2E de accesibilidad implementadas y Playwright/axe-core disponibles; cero pruebas seleccionadas no acredita accesibilidad. Registra defectos con pasos y datos sintéticos reproducibles. Entrega a Alfredo la evidencia; a cada autor, sus correcciones. No sustituyas aceptación humana por un informe de la IA.

## Prompt personal para una IA

Añade al prompt común:

```text
Soy Roberto Villouta, responsable de Seguridad y QA.
Lee docs/guias-equipo/roberto-villouta.md.
Primer lote: T029, después de comprobar los puertos acordados con Nicolás.
Implementa auditoría por campo con pruebas de los datos obligatorios y la inmutabilidad.
Coordina el contrato de impacto del motor; si no existe, documenta la dependencia.
No inventes importes, resultados de ejecución ni evidencias de cumplimiento.
```

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T029**: Implementar el servicio de auditoría por campo, con impacto MAB/Forecast, en `src/proyecta/application/services/audit.py`.
- **T036**: Crear pruebas de fundación (auth, bloqueo por intentos, auditoría, repositorios, configuración) en `tests/integration/test_foundation.py`.
- **T124**: [P] [US8] Contrato de auditoría y usuarios en `tests/contract/test_auditoria.py`.
- **T125**: [P] [US8] Integración de `403`, `405` y `409` en `tests/integration/test_permissions_audit.py`.
- **T126**: [US8] Consulta y exportación de auditoría en `src/proyecta/application/use_cases/auditoria.py`.
- **T127**: [US8] Ruta API de auditoría en `src/proyecta/interfaces/api/v1/auditoria.py`.
- **T128**: [US8] Pantalla de auditoría en `src/proyecta/interfaces/web/templates/registros/auditoria.html`.
- **T129**: [US8] Administración de usuarios y roles, sin permitir desactivar al último usuario de Operaciones (FR-065), en `src/proyecta/application/use_cases/usuarios.py`.
- **T130**: [US8] Rutas API y pantalla de usuarios en `src/proyecta/interfaces/api/v1/usuarios.py` y `templates/usuarios/index.html`.
- **T131**: [US8] Aplicar políticas de rol/propiedad, incluido impedir que un líder cambie su propio rol o el de otra persona (FR-064), en `src/proyecta/domain/permissions.py`.
- **T132**: [US8] Rechazo `405` en bitácora/auditoría y `409` por versión en `src/proyecta/interfaces/api/errors.py`.
- **T133**: [US8] Ejecutar la suite de US8 y corregir fallos en `tests/contract/test_auditoria.py` y `tests/integration/test_permissions_audit.py`.
- **T157**: [P] Prueba de carga con 5.000 registros y 50 concurrentes; ajustar índices y proyección en `tests/integration/test_load.py`.
- **T158**: [P] Auditoría de accesibilidad con axe y correcciones en `src/proyecta/interfaces/web/templates/base.html` y `dashboard/index.html`.
- **T161** **(asignación complementaria propuesta)**: [P] Documentar respaldo, restauración y retención en `docs/operacion.md`.
- **T163**: Verificar cobertura ≥ 90 % del dominio y pipeline en verde en `pyproject.toml` y `deploy/cloudbuild.yaml`.
- **T168**: Verificar disponibilidad 99,5 %, RTO 4 h y RPO 24 h con simulación de restauración en `tests/integration/test_availability.py`.
- **T169**: Verificar retención de cinco años y ausencia de TTL/borrado en `tests/integration/test_retention.py` y `src/proyecta/infrastructure/datastore/audit_repository.py`.
- **T172** **(asignación complementaria propuesta)**: [P] Verificar fechas de negocio sin hora y eventos UTC mostrados en America/Santiago en `tests/integration/test_timezone.py`.
