# Equipo y asignación por carpetas

**Proyecto**: Proyecta — APP Gestión de la Demanda y Oportunidades  
**Iniciativa**: Build & Impact 2026 · Fundación NTT DATA Chile  
**Equipo**: Heavy-Duty · TEC-UCT  
**Product Owner**: Alfredo San Juan  
**Fuente de roles**: `docs/fuentes/Heavy-Duty_APPGestionDeLaDemanda_V3.pdf` y `docs/fuentes/resumen_transcripcion_reunion.md`

> Esta es una **propuesta inicial** de asignación por carpetas. La fuente de verdad de las tareas es `specs/001-proyecta-mvp/tasks.md`; el PO puede mover tareas entre integrantes sin cambiar la estructura.

## Tabla de responsabilidades

| Integrante | Rol | Carpetas y archivos de trabajo | Frentes principales | Tareas guía |
|---|---|---|---|---|
| **Alfredo San Juan** | Product Owner | `specs/`, `docs/equipo.md`, `docs/fuentes/requerimientos.md`, `specs/001-proyecta-mvp/quickstart.md` | Alcance, prioridades, validación con sponsor, aceptación y coordinación | T164, T166, T167 |
| **Matías Mcintire** | Arquitectura y seguridad | `deploy/`, `src/proyecta/config.py`, `src/proyecta/main.py`, `src/proyecta/infrastructure/auth/`, `docs/adr/` | Fundación, configuración, sesión, CSRF, despliegue, revisión de seguridad | T001–T011, T018–T024, T025–T027, T030–T032, T034, T159 |
| **Felipe Astete** | Backend / Estados | `src/proyecta/domain/states.py`, `rules.py`, `registro_rules.py`, `application/use_cases/estados.py`, `bitacora.py`, `backlog.py`, `metas.py`, `cierre.py`, `interfaces/api/v1/estados.py`, `bitacora.py` | Ciclo de vida, probabilidad/confiabilidad, bitácora, Backlog, metas, cierre y puente | T028, T040–T041, T052–T063, T092–T115 |
| **Leonardo Aguilera** | UI / Dashboards | `src/proyecta/interfaces/web/templates/dashboard/`, `static/js/`, `application/use_cases/dashboard.py`, `interfaces/api/v1/dashboard.py`, `scripts/rebuild_resumen.py` | Dashboard, filtros, detalle, proyección `ResumenMensual`, reportes visuales | T080–T091, T134–T141 |
| **Bryam Beltrán** | Frontend / Bitácora | `src/proyecta/interfaces/web/templates/registros/`, `routes/registros.py`, `routes/estados.py`, `static/css/`, `bitacora.html`, `calidad/index.html` | Formularios, listado, detalle, bitácora, navegación y calidad visual | T033, T037–T051, T060, T116–T123 |
| **Nicolás Huenchual** | Líder Backend / Motor / IA | `src/proyecta/domain/engine/`, `application/use_cases/calculo.py`, `ia.py`, `simulacion.py`, `infrastructure/ai/`, `scripts/seed_synthetic.py` | Motor Base/MAB/Backlog/Forecast/HC/Gap, vigencias, IA opcional y simulación | T012–T017, T035, T064–T079, T142–T149 |
| **Roberto Villouta** | Seguridad y QA | `tests/`, `docs/operacion.md`, `deploy/` (revisión), `tests/integration/test_permissions_audit.py`, `test_availability.py`, `test_retention.py` | Auditoría, permisos, pruebas de seguridad, disponibilidad, retención, evidencias | T029, T036, T124–T133, T157–T159, T163, T168–T169 |

## Reglas de trabajo por carpeta

- **`domain/`**: lo comparten Felipe (estados/reglas) y Nicolás (motor). No importar FastAPI, Datastore ni Jinja2.
- **`application/use_cases/`**: un archivo por caso de uso; el dueño del frente lo mantiene.
- **`infrastructure/`**: Matías (auth/config), Roberto (auditoría/seguridad), Nicolás (IA). No cambiar contratos sin avisar a `interfaces/`.
- **`interfaces/web/templates/`**: Leonardo (dashboard) y Bryam (registros/bitácora/calidad). Evitar editar la plantilla del otro sin coordinación.
- **`tests/`**: cada integrante escribe las pruebas de su tarea; Roberto mantiene la estrategia y la evidencia.
- **`specs/` y `docs/`**: Alfredo coordina; Matías mantiene ADR; Roberto mantiene operación.

## Orden de arranque

1. **Matías**: T001–T011 (estructura, configuración, app base, CI).
2. **Fundación compartida**: T012–T036 según la tabla (Nicolás entidades y seed, Matías repos/auth/config, Felipe permisos, Roberto auditoría y pruebas, Bryam layout). Matías coordina la integración.
3. **Felipe, Bryam, Nicolás y Leonardo**: US1–US4 en el orden de `tasks.md`.
4. **Roberto**: pruebas transversales y seguridad desde el inicio, no al final.

## Definition of Done por tarea

- Código en la carpeta acordada, sin lógica de negocio en plantillas.
- Pruebas en `tests/` que fallen antes y pasen después.
- Auditoría y permisos verificados cuando corresponda.
- Sin datos reales, secretos ni credenciales en el repositorio.
- Documentación o ADR actualizado si cambia una decisión.
- Tarea marcada en `tasks.md` solo cuando el revisor lo confirme.

## Coordinación

- Los contratos entre capas se acuerdan en `application/ports.py` y `contracts/openapi.yaml`.
- Un cambio de esquema se refleja en `data-model.md` y en la migración de datos sintéticos.
- Las decisiones abiertas `S-xx` no se implementan como supuestos; se consultan con el PO.
