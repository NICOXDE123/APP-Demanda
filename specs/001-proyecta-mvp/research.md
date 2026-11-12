# Research: Proyecta — MVP

**Feature**: `001-proyecta-mvp`

**Date**: 2026-10-27

**Spec**: [spec.md](spec.md)

**Plan**: [plan.md](plan.md)

## Summary

La especificación no contiene marcadores de clarificación pendientes. Las decisiones `S-xx` que siguen abiertas son validaciones de negocio o dependencias externas, no incógnitas técnicas; el plan las aísla mediante catálogos, parámetros y datos sintéticos para que no bloqueen la arquitectura. La investigación fija un monolito modular en Python 3.12 con FastAPI, interfaz server-rendered con Jinja2/HTMX, Firestore en modo Datastore y un motor de cálculo puro y determinista.

## Decisions

### R-01 · Runtime y framework

- **Decision**: Python 3.12 con FastAPI y Uvicorn.
- **Rationale**: es el stack de referencia del Anexo C, el equipo lo declara en la propuesta y permite un dominio puro, tipado y testeable. FastAPI aporta validación con Pydantic y un contrato OpenAPI alineado con `RNF-10`.
- **Alternatives considered**: Django (más baterías incluidas, pero acopla dominio y ORM y no es el stack del equipo); Node/NestJS (equipo sin experiencia declarada); Flask (menos validación y contrato integrados).

### R-02 · Interfaz web

- **Decision**: Jinja2 + HTMX + Bootstrap 5 + Chart.js, con assets servidos localmente.
- **Rationale**: el Anexo C fija esta interfaz; reduce el JavaScript propio, mantiene accesibilidad y permite renderizar el dashboard sin una SPA separada.
- **Alternatives considered**: React/Vue SPA (duplica despliegue y estado); Alpine.js (menos maduro para formularios complejos); server-side puro sin HTMX (peor experiencia en filtros y modales).

### R-03 · Persistencia

- **Decision**: Firestore en modo Datastore mediante `google-cloud-datastore`, detrás de un puerto de repositorio. Emulador local para desarrollo y pruebas.
- **Rationale**: es la base de referencia del Anexo C, tiene transacciones ACID, escala a cero con Cloud Run y evita administrar un motor SQL en el MVP. El puerto de repositorio deja abierta la alternativa Cloud SQL.
- **Alternatives considered**: Cloud SQL/PostgreSQL (mejor para consultas agregadas y reportes, pero más costo operativo y no es la referencia); BigQuery (no apto para transacciones); archivos planos (sin concurrencia ni auditoría).

### R-04 · Identidad, sesión y CSRF

- **Decision**: sesiones del lado del servidor en la entidad `Sesion`; cookie `proyecta_session` con `HttpOnly`, `Secure` y `SameSite=Strict`; Argon2id para contraseñas; token CSRF de sincronización en formularios y en el encabezado de HTMX; bloqueo tras cinco intentos por cuenta e IP.
- **Rationale**: la sesión del servidor permite revocar accesos y aplicar bloqueo; cumple `RNF-05`/`RNF-06`. Argon2id es el algoritmo indicado por la propuesta.
- **Alternatives considered**: JWT sin estado (no revocable con facilidad, difícil de invalidar al cambiar rol); cookie firmada con `itsdangerous` (válida, pero sin revocación central); autenticación básica (inadmisible).

### R-05 · Motor de cálculo

- **Decision**: módulo `domain/engine` puro, con `Decimal` para cálculos y almacenamiento de dinero en enteros CLP, tarifas en centavos y porcentajes en puntos base (0–10.000). Sin fórmulas en plantillas, JavaScript ni consultas de base de datos.
- **Rationale**: cumple el Principio II y evita errores de coma flotante; los casos C-01 a C-08 se ejecutan contra el mismo motor que la API, el dashboard, la exportación y el simulador.
- **Alternatives considered**: fórmulas en SQL/vistas (difíciles de probar y portar); cálculo en el navegador (duplica lógica y permite manipulación); `float` (pierde exactitud en CLP).

### R-06 · Auditoría y bitácora

- **Decision**: `EventoAuditoria` y `Bitacora` como entidades de solo inserción, con un evento por campo auditado. La capa de aplicación no expone `update` ni `delete`; los routers no definen `PUT`/`DELETE` y el framework responde `405`.
- **Rationale**: cumple `RN-78`, `RN-81`, `RNF-07` y el Principio III. El evento guarda valores, usuario, fecha/hora UTC, origen, fecha efectiva, motivo e impacto en MAB/Forecast.
- **Alternatives considered**: triggers de base de datos (Datastore no los ofrece); historial por diferencias en un JSON (difícil de consultar); logs de aplicación (no auditables ni consultables por registro).

### R-07 · Concurrencia

- **Decision**: campo `version` en `Registro` y en las entidades editables; lectura + comparación + escritura dentro de una transacción de Datastore; `409` si la versión no coincide.
- **Rationale**: cumple `RN-80` y `AC-13`; evita pérdida de escrituras sin bloquear la edición.
- **Alternatives considered**: bloqueo pesimista por registro (peor experiencia y riesgo de bloqueos); último gana (pierde datos); bloqueo por base (no disponible en Datastore).

### R-08 · Cierre de período y puente

- **Decision**: `Corte` con estados `CREANDO`, `CERRADO` y `ERROR`; el cierre escribe `CorteDetalle` en lotes idempotentes y solo marca `CERRADO` al completar. El puente se calcula con los detalles congelados.
- **Rationale**: un cierre con 5.000 registros × 12 meses no cabe en una sola transacción; el proceso por lotes permite reanudar y mantiene la inmutabilidad al final.
- **Alternatives considered**: una transacción única (excede límites y bloquea); cálculo del puente sobre datos vivos (no reproducible); cierre en el navegador (inadmisible).

### R-09 · Dashboard y rendimiento

- **Decision**: consultas indexadas para el mes en curso y una proyección `ResumenMensual` (no fuente de verdad) para los agregados del dashboard; reconstruible por comando. Si el p95 supera 2 s, se materializa por sector/owner/tipo/estado.
- **Rationale**: 5.000 registros × 12 meses es demasiado para recalcular todo en cada carga; la proyección mantiene el dashboard bajo 2 s sin alterar el dominio.
- **Alternatives considered**: calcular todo en cada request (riesgo de p95); cache en memoria por instancia (se pierde al escalar); BigQuery (fuera de alcance y costo).

### R-10 · Exportación a Excel

- **Decision**: `openpyxl` en streaming; se sanitizan las celdas que comienzan con `=`, `+`, `-` o `@`; se respetan filtros y permisos antes de generar el archivo.
- **Rationale**: cumple `RF-59` y la protección contra inyección de fórmulas; no requiere servicio externo.
- **Alternatives considered**: CSV (pierde formato y fórmulas); servicio de reportes (costo y complejidad); exportación desde el navegador (no respeta permisos del servidor).

### R-11 · Asistente de IA y simulación

- **Decision**: adaptador opcional a Vertex AI Gemini detrás de una interfaz `AsistenteIA`; `SugerenciaIA` con cita, estado y versión del prompt; aprobación humana y evento de auditoría con origen `IA`; simulación en memoria sobre una copia aislada, sin persistencia.
- **Rationale**: cumple el Principio VIII y las prioridades 2/2b. Si no hay credenciales o el modelo falla, la aplicación sigue operando.
- **Alternatives considered**: IA que escriba directo (viola el Principio VIII); modelo local (costo/operación); simulación persistida (rompe la integridad).

### R-12 · Pruebas y calidad

- **Decision**: `pytest` + `pytest-cov` para dominio e integración; `httpx`/`TestClient` para API; pruebas de contrato desde OpenAPI; Playwright + axe-core para E2E y accesibilidad; `ruff` y `mypy` para lint y tipos; casos C-01 a C-08 como regresión obligatoria; cobertura de dominio ≥ 90 %.
- **Rationale**: cubre `RNF-13`, `RNF-08` y los criterios de aceptación; el mismo stack permite ejecutar todo en CI.
- **Alternatives considered**: unittest puro (menos ecosistema); Cypress (más pesado); pruebas manuales (no repetibles).

### R-13 · Despliegue y operación

- **Decision**: un servicio en Cloud Run, imagen en Artifact Registry, secretos en Secret Manager, logs y métricas en Cloud Logging; entornos `dev` y `demo`; CI/CD con Cloud Build (o el pipeline que fije NTT DATA) que ejecuta pruebas antes de desplegar.
- **Rationale**: es la referencia del Anexo C, escala a cero y mantiene el costo dentro de USD 10–30. La decisión final de proyecto/región depende de `S-12`.
- **Alternatives considered**: GKE (sobredimensionado); App Engine (menos control del contenedor); VM (más operación).

### R-14 · Datos sintéticos y migración

- **Decision**: generador `seed_synthetic` con 1.000 registros, 12 sectores, 30 % multiperfil, 20 % probabilidad intermedia, 10 % continuidad, 5 rojos/10 amarillos/3 fechas inválidas. No se migran los cuatro registros reales en el MVP (`H-05`, `S-11`).
- **Rationale**: cumple `RNF-15`, `S-13` y el Principio I; permite demostrar la carga inicial y la calidad sin datos del cliente.
- **Alternatives considered**: migrar los cuatro registros reales a demo (prohibido); usar datos reales seudonimizados (requiere autorización y tratamiento que no están en el MVP).

### R-15 · Fechas, moneda y zona horaria

- **Decision**: fechas de negocio como `date` ISO `YYYY-MM-DD`; eventos como `timestamp` UTC; visualización en `America/Santiago`; montos en CLP entero; tarifas en centavos; porcentajes en puntos base. `zoneinfo` para la conversión.
- **Rationale**: cumple `RNF-02`, `RN-57`, `RN-86` a `RN-88`; evita ambigüedad de zona horaria y errores de redondeo.
- **Alternatives considered**: almacenar fechas con hora local (ambigüedad); `float` para dinero (error); timestamps en la zona del servidor (inconsistencia).

### R-16 · Contrato de interfaz

- **Decision**: API REST versionada en `/api/v1`, OpenAPI 3.1 en `contracts/openapi.yaml`, respuestas JSON y errores con código estable. La interfaz web consume los mismos casos de uso que la API.
- **Rationale**: cumple `RNF-10` y permite pruebas de contrato; la UI no reimplementa reglas.
- **Alternatives considered**: GraphQL (no es la referencia y complica permisos por campo); API no versionada (rompe clientes); contract-first con otro formato (OpenAPI es el estándar del equipo).

## Resolved technical unknowns

| Unknown | Resolution | Source |
|---|---|---|
| Runtime y framework | Python 3.12 + FastAPI | Anexo C, propuesta |
| Interfaz | Jinja2 + HTMX + Bootstrap + Chart.js | Anexo C |
| Base de datos | Firestore Datastore + repositorio | Anexo C |
| Sesión y CSRF | Sesión de servidor + Argon2 + token CSRF | RNF-05 |
| Cálculo | Dominio puro con `Decimal` | Principio II, §10 |
| Concurrencia | Versión + transacción + `409` | RN-80 |
| Cierre | Lotes idempotentes + `Corte` | §9.8 |
| Dashboard | Proyección `ResumenMensual` | RNF-03 |
| Exportación | `openpyxl` + sanitización | RF-59 |
| IA | Adaptador opcional Vertex AI | D-17, Principio VIII |
| Pruebas | pytest + Playwright + axe | RNF-08, RNF-13 |
| Despliegue | Cloud Run + Artifact Registry | Anexo C |

## Open business decisions

No hay incógnitas técnicas pendientes. Las decisiones `S-xx` de la spec siguen abiertas y el plan las aísla:

- `S-01`: 180 h iniciales; el motor lee el parámetro con vigencia, no una constante.
- `S-02`: el nombre de la sexta etapa es un valor de catálogo; un cambio no afecta el esquema.
- `S-03`: la semántica de `Cerrada` se resuelve con motivo de cierre; el cálculo excluye el registro.
- `S-04`: los alias de catálogos se cargan en la tabla de equivalencias; no se codifican en el motor.
- `S-05`/`S-06`: contratos y metas se cargan con datos sintéticos; los módulos existen y se prueban con fixtures.
- `S-10`: el catálogo de clientes se siembra con datos sintéticos.
- `S-11`: la migración real queda fuera del MVP.
- `S-12`: el despliegue usa la referencia Cloud Run; la región/proyecto se confirma con NTT DATA.
- `S-15`: este plan es una línea base; la reestimación se hace al cerrar el alcance.

Las decisiones `H-01` a `H-07` ya están integradas en la spec y se implementan tal como quedaron: 100 % al adjudicar, prorrateo por motivo, lista amplia de motivos, horas con vigencia mensual, sin migración real en el MVP, vigencia mensual de P/C y Backlog confirmado como vista de la MAB.
