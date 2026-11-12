# Registro de uso de inteligencia artificial · Proyecta

Las Bases (§14) permiten y fomentan el uso de IA con cinco condiciones:

- que tenga una finalidad vinculada al proyecto;
- que use herramientas autorizadas;
- que no exponga datos personales ni confidenciales;
- que mantenga supervisión humana;
- que se informe cuando tenga un impacto relevante en la solución.

El equipo debe revisar lo generado, probar el código y explicar cómo la IA agrega valor. Este registro es la base de la declaración de uso de IA de la Entrega 3 (§16.3).

## 1. IA usada para construir Proyecta

| Fecha | Herramienta | Para qué | Qué datos vio | Cómo se verificó | Revisión del equipo |
|---|---|---|---|---|---|
| 11–12/10 | Claude Code; las versiones del PO, con otra herramienta (por confirmar) | Postulación: revisión y ajustes de la propuesta técnica | Documentos de la postulación | Revisión del equipo antes del envío | Equipo |
| 15/10 | Claude Code | Preparación de la reunión con el sponsor: guion y preguntas | OnePage y propuesta | Revisión del equipo antes de la reunión | Matías |
| 25/10 | Claude Code | Auditoría de los requerimientos internos contra el OnePage, la propuesta, el documento maestro y la transcripción | Documentos del proyecto, incluidas la transcripción de la reunión y capturas del Excel, que tienen nombres reales | Cada hallazgo cita su fuente; las decisiones quedaron para el equipo | Matías |
| 25–26/10 | Claude Code (Claude Opus 5.5) | Revisión del prototipo HTML de Bryam y corrección de errores y vacíos de prioridad 1 | Solo el prototipo, con datos sintéticos | 30 comprobaciones automáticas | Pendiente: Bryam |
| 26/10 | Claude Code (Claude Opus 5.5) | Prueba técnica: motor en Python y app FastAPI + HTMX en contenedor | Datos sintéticos | Pruebas automáticas con los casos de referencia de entonces | Pendiente: Nicolás |
| 27–28/10 | Spec Kit 1.2.4 con un asistente de IA (por confirmar cuál) | Constitución, especificación, sesiones de clarificación, plan, investigación técnica, modelo de datos, contrato OpenAPI y tareas | Requerimientos y fuentes del repositorio | Las respuestas de clarificación (H-01 a H-07) las decidió el equipo; la segunda ronda la pidió el PO | Matías y Alfredo (por confirmar) |
| 29/10 | Claude Code (Claude Opus 5.5) | Primer incremento en `src/`: motor, reglas del alta, rutas, plantillas y semilla. También sus 19 pruebas, `deploy/Dockerfile`, `ENTREGA_1.md` y las capturas de evidencia | Repositorio (requerimientos v1.1, spec, plan y tareas) y documentos de trabajo del equipo; la app usa solo datos sintéticos | 19 pruebas: los casos C-01 a C-08 tienen valores esperados calculados a mano desde `requerimientos.md` §10.9. Además, recorrido en Chromium e imagen Docker probada por HTTP | Pendiente en el merge request: Nicolás (motor), Bryam y Leonardo (pantallas), Roberto (pruebas) y Alfredo (`ENTREGA_1.md`) |
| 12/11 | Herramienta usada por Nicolás (por confirmar) | Dominio, motor con vigencias, casos de uso de cálculo, IA y simulación, semilla sintética y sus 66 pruebas (commit `8227340` en su repositorio) | Requerimientos y especificación; datos sintéticos | 66 pruebas; revisión del PO del 12/11 con 5 observaciones | Alfredo (revisión hecha) |
| 12/11 | Herramienta usada por Alfredo (por confirmar) | Guías del equipo, revisión del trabajo de Nicolás y mejora UX del mockup | Repositorio y mockup | Revisión del PO; verificación del mockup en Chrome | Alfredo |
| 12/11 | Claude Code (Claude Opus 5.5) | Entrega 2: integración del motor de Nicolás en el repositorio oficial. Además: máquina de estados, casos de uso de registros, sesión con Argon2, bloqueo y CSRF, permisos, repositorios en memoria, dashboard, pantallas, wiring de la API, 22 pruebas nuevas, ajuste del Dockerfile y `ENTREGA_2.md`. También corrigió en el motor el desempate de vigencias del mismo mes | Repositorio (requerimientos v1.1, spec, plan, tareas, guías y revisiones); la app usa solo datos sintéticos | 88 pruebas en verde (US1 a US4 y US8 por HTTP, más los casos de la spec); recorrido en Chromium sin errores de consola, a 1.440 y a 390 px; imagen Docker probada por HTTP | Pendiente en el merge request: Felipe (estados y permisos), Bryam (registros), Leonardo (dashboard), Roberto (auditoría, sesión y pruebas), Nicolás (integración con el motor) y Matías (fundación) |
