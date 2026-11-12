# Bryam Beltrán — Frontend / Bitácora

## Resultado esperado

Entregar el flujo de registros y la experiencia de seguimiento/calidad. La asignación actual también incluye casos de uso y API de US1 y US7, además de las plantillas.

**Tareas base:** T033, T037–T039, T042–T051, T060 y T116–T123. **Complementarias propuestas:** T170–T171. Lee [el flujo común](README.md), `AGENTS.md` y los documentos del frente. Las rutas parten de la raíz.

## Archivos y contenidos

Son entregables previstos. Los nombres abreviados de una fila comparten el directorio del primer archivo, salvo ruta explícita.

| Archivo o grupo | Contenido esperado |
|---|---|
| `src/proyecta/interfaces/web/templates/base.html`; `login.html` | Layout, navegación por rol, mensajes y login conectado a la autenticación del servidor. |
| `src/proyecta/application/use_cases/registros.py` | Alta, edición, cierre de registro, búsqueda y paginación, con permisos y auditoría. Distinguir cierre de registro de cierre de período. |
| `src/proyecta/application/use_cases/perfiles.py` | Altas/cambios de perfiles, tarifas y ajustes con validación del servidor. |
| `src/proyecta/interfaces/api/v1/registros.py`; `perfiles.py` | API de registros, perfiles y tarifas conforme a OpenAPI. |
| `src/proyecta/interfaces/web/routes/registros.py`; `estados.py` | Rutas web y acciones HTMX que delegan a casos de uso. |
| `src/proyecta/interfaces/web/templates/registros/form.html`; `detail.html`; `list.html` | Formularios con perfiles/tarifas, detalle, filtros, paginación y errores visibles. |
| `src/proyecta/interfaces/web/templates/registros/bitacora.html` | Historial, nuevas entradas y correcciones referenciadas. No ofrecer edición/borrado de entradas existentes. |
| `src/proyecta/interfaces/web/static/css/app.css`; `src/proyecta/interfaces/web/static/js/app.js` | Estilos/comportamiento comunes coordinados con Matías, sin fórmulas de negocio. |
| `src/proyecta/domain/quality.py` | Reglas DQ-01 a DQ-13, como funciones de dominio puro con pruebas. |
| `src/proyecta/application/use_cases/calidad.py`; `src/proyecta/interfaces/api/v1/calidad.py` | Evaluación/consulta de semáforos y pendientes según visibilidad del usuario. |
| `src/proyecta/interfaces/web/templates/calidad/index.html` | Panel de alertas y acciones para corregir registros. |
| `tests/contract/test_registros.py`; `tests/integration/test_registro_create.py`; `tests/unit/domain/test_registro_rules.py` | Contrato, alta con dos perfiles, obligatorios y coherencia tipo/estado/flujo. Felipe entrega los validadores. |
| `tests/unit/domain/test_quality.py`; `tests/integration/test_quality.py` | Reglas DQ y casos DQ-06/07/08/12, incluidos permisos. |
| `tests/e2e/test_compatibility.py`; `test_localization.py` | Chrome/Edge, pantalla desde 360 px, es-CL, CLP, fechas y porcentajes. |

## Orden de ejecución

1. Durante Fundación crea T033; coordina recursos T008 con Matías y la integración de sesión/CSRF.
2. Con Fundación lista, escribe T037–T039 e integra T040–T041 entregados por Felipe.
3. Construye casos de uso, API, rutas y formularios de US1, con auditoría y conflictos de versión.
4. Implementa T060 consumiendo los casos de uso de Felipe. Acuerden parámetros, errores y permisos antes de conectar las acciones.
5. Tras US1 y US2, implementa US7, incluidas reglas y API. Completa compatibilidad/localización durante el endurecimiento.

## Validación y entrega

El alta debe guardar dos perfiles y generar auditoría. La validación visual acompaña a la del servidor. Un 409 conserva lo ingresado e informa el conflicto; los permisos deben comprobarse aunque una acción esté oculta en la interfaz. Verifica navegación por rol, mensajes accesibles, fechas `dd-mm-aaaa`, CLP y coma decimal.

Cuando existan las implementaciones y el entorno, ejecuta:

```powershell
uv run pytest tests/contract/test_registros.py tests/integration/test_registro_create.py tests/unit/domain/test_registro_rules.py -q
uv run pytest tests/unit/domain/test_quality.py tests/integration/test_quality.py -q
uv run pytest tests/e2e/test_compatibility.py tests/e2e/test_localization.py -q
```

Adjunta capturas y resultados. Felipe revisa reglas/estados; Roberto, formularios, calidad y accesibilidad. Entrega componentes comunes a Leonardo y coordina su modificación de `list.html` en T139.

## Prompt personal para una IA

Añade al prompt común:

```text
Soy Bryam Beltrán, responsable de Frontend / Bitácora.
Lee docs/guias-equipo/bryam-beltran.md.
Primer lote: T033, comprobando antes los recursos y contratos de autenticación.
Implementa layout y login con Jinja2/HTMX y navegación por rol.
Usa la sesión y CSRF de Matías; si faltan, documenta esa dependencia.
No simules una autenticación funcional ni declares listo el flujo sin probarlo.
```

## Catálogo de tareas del frente

Detalle tomado de `specs/001-proyecta-mvp/tasks.md` al preparar esta guía. Ese archivo conserva el estado oficial y las dependencias; si cambia, actualiza este catálogo. Las rutas abreviadas se interpretan con el directorio de la primera ruta y la tabla de archivos anterior. Las etiquetas [P] no permiten omitir dependencias ni editar un archivo compartido al mismo tiempo.

- **T033**: Crear layout base, navegación por rol y pantalla de login en `src/proyecta/interfaces/web/templates/base.html` y `login.html`.
- **T037**: [P] [US1] Contrato de `/registros`, `/registros/{id}`, `/perfiles` y `/tarifas` en `tests/contract/test_registros.py`.
- **T038**: [P] [US1] Integración de alta con dos perfiles en `tests/integration/test_registro_create.py`.
- **T039**: [P] [US1] Unitarias de código, obligatorios y coherencia tipo/estado/flujo en `tests/unit/domain/test_registro_rules.py`.
- **T042**: [US1] Caso de uso de alta, edición y cierre de registro en `src/proyecta/application/use_cases/registros.py`.
- **T043**: [US1] Casos de uso de perfiles, tarifas y ajustes en `src/proyecta/application/use_cases/perfiles.py`.
- **T044**: [US1] Rutas API de registros en `src/proyecta/interfaces/api/v1/registros.py`.
- **T045**: [US1] Rutas API de perfiles y tarifas en `src/proyecta/interfaces/api/v1/perfiles.py`.
- **T046**: [US1] Búsqueda, filtros y paginación en `src/proyecta/application/use_cases/registros.py`.
- **T047**: [P] [US1] Plantillas de alta y detalle con perfiles y tarifas en `src/proyecta/interfaces/web/templates/registros/form.html` y `detail.html`.
- **T048**: [P] [US1] Plantilla de listado con filtros en `src/proyecta/interfaces/web/templates/registros/list.html`.
- **T049**: [US1] Rutas web de alta, edición, detalle y listado en `src/proyecta/interfaces/web/routes/registros.py`.
- **T050**: [US1] Integrar auditoría de creación, edición, perfil y tarifa en `src/proyecta/application/use_cases/registros.py`.
- **T051**: [US1] Ejecutar la suite de US1 y corregir fallos en `tests/contract/test_registros.py` y `tests/integration/test_registro_create.py`.
- **T060**: [US2] Acciones web y bitácora en `src/proyecta/interfaces/web/routes/estados.py` y `templates/registros/bitacora.html`.
- **T116**: [P] [US7] Unitarias de las reglas DQ en `tests/unit/domain/test_quality.py`.
- **T117**: [P] [US7] Integración del panel de calidad en `tests/integration/test_quality.py`.
- **T118**: [P] [US7] Reglas `DQ-01` a `DQ-13` en `src/proyecta/domain/quality.py`.
- **T119**: [US7] Servicio de calidad, semáforo y pendientes en `src/proyecta/application/use_cases/calidad.py`.
- **T120**: [US7] Ruta API de calidad en `src/proyecta/interfaces/api/v1/calidad.py`.
- **T121**: [US7] Panel de calidad y alertas en `src/proyecta/interfaces/web/templates/calidad/index.html`.
- **T122**: [US7] Pruebas de `DQ-06`, `DQ-07`, `DQ-08` y `DQ-12` en `tests/integration/test_quality.py`.
- **T123**: [US7] Ejecutar la suite de US7 y corregir fallos en `tests/unit/domain/test_quality.py` y `tests/integration/test_quality.py`.
- **T170** **(asignación complementaria propuesta)**: [P] Prueba de compatibilidad Chrome/Edge de las últimas dos versiones y responsive desde 360 px en `tests/e2e/test_compatibility.py`.
- **T171** **(asignación complementaria propuesta)**: [P] Verificar es-CL, fechas `dd-mm-aaaa`, montos CLP y porcentajes con coma decimal en `tests/e2e/test_localization.py`.
