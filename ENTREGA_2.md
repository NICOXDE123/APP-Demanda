# Proyecta · Entrega 2: producto mínimo viable

**Build & Impact 2026 · Fundación NTT DATA Chile** · Desafío *APP Gestión de la Demanda* (Operaciones, NTT DATA GDN-e)
**Equipo:** Heavy-Duty · TEC-UCT · **Representante:** Matías Mcintire · **Product Owner:** Alfredo San Juan
**Sponsor:** Jorge Escobar, Gerente de Proyectos y responsable de Operaciones
**Fecha:** 12-11-2026 (plazo de las Bases: 11-11-2026; ver §11) · **Rama:** `entrega-2`, con merge request a `main`

Este documento responde los 10 puntos de la Entrega 2 en el orden de las Bases (§16.2).

| # | Punto de las Bases | Sección |
|:-:|---|:-:|
| 1 | Producto mínimo viable funcional | §1 |
| 2 | Aplicación desplegada y accesible mediante una URL | §2 |
| 3 | Funcionalidades principales implementadas | §3 |
| 4 | Acceso al repositorio | §4 |
| 5 | Instrucciones básicas de uso | §5 |
| 6 | Evidencias de pruebas | §6 |
| 7 | Limitaciones conocidas | §7 |
| 8 | Estado actualizado del backlog | §8 |
| 9 | Registro de la retroalimentación recibida | §9 |
| 10 | Plan de mejoras para la siguiente etapa | §10 |

---

## 1. Producto mínimo viable funcional

Proyecta reemplaza la planilla de demanda de Operaciones por una aplicación web con una sola fuente de datos:

1. Los líderes registran oportunidades y demandas con sus perfiles, HC, tarifas, fechas y bitácora.
2. El sistema calcula la Base, la MAB, el Backlog y el Forecast de 12 meses.
3. Cada cifra se puede abrir hasta los registros y componentes que la explican.
4. Cada cambio queda auditado con su impacto en la MAB y el Forecast.

El MVP cubre las **9 funcionalidades obligatorias del OnePage** (§3), con inicio de sesión y tres roles. Se agregan los estados y el flujo comercial, y una primera versión de Backlog, metas y gap.

**Arquitectura**, sin cambios respecto de la E1: Python 3.12 · FastAPI · Jinja2 + HTMX + Bootstrap + Chart.js, servidos desde la propia app · contenedor Linux.

**Capas:**

- **Dominio:** entidades, motor y reglas de estado, sin dependencias de framework.
- **Aplicación:** casos de uso.
- **Infraestructura:** persistencia y autenticación.
- **Interfaz:** rutas y plantillas.

**Persistencia:** en esta entrega va en memoria, detrás de los mismos puertos que usarán los repositorios de Datastore (§7).

**Integración:** esta entrega une en un solo repositorio el incremento de la E1 y el trabajo de Nicolás, que se hizo en otro repositorio y se trajo a la rama: dominio completo, motor único con vigencias y semilla sintética. El motor del incremento de la E1 se reemplazó por el de Nicolás, para no tener dos motores.

## 2. Aplicación desplegada

- **URL:** `<<COMPLETAR AL DESPLEGAR>>`
- **Contraseña de las cuentas de demostración:** se entrega por el canal oficial, no en el repositorio.

| Cuenta | Rol | Qué puede hacer |
|---|---|---|
| `operaciones@example.test` | Operaciones | Todo: registros de todos, confiabilidad, continuidades, parámetros, reapertura |
| `lider1@example.test` (y `lider2`, `lider3`) | Líder | Crear y mantener **sus** registros, bitácora, estados y probabilidad |
| `ejecutivo@example.test` | Ejecutivo | Solo lectura: dashboard, registros, detalle y auditoría |

Mientras NTT DATA habilita el proyecto de GCP (S-12), la misma imagen de Cloud Run (`deploy/Dockerfile`) corre en un servicio temporal gratuito. El paso a Cloud Run es un despliegue de la misma imagen; se hace apenas exista el proyecto. Este servicio tiene dos restricciones, descritas en §7:

- se suspende tras un rato sin uso, y la primera carga demora cerca de un minuto;
- al reiniciarse vuelve a los datos sintéticos iniciales.

## 3. Funcionalidades principales implementadas

| # | Funcionalidad del OnePage | Dónde se ve | Qué hace |
|:-:|---|---|---|
| 1 | Crear oportunidad o demanda con sus campos | *Nuevo registro* | Tres tipos: oportunidad (Pendiente, flujo 1, P 10 %, C 90 %), demanda directa (Adjudicada, flujo 3–5, P 100 %, con motivo) y continuidad con ficha de contrato (solo Operaciones). Código `OPD-####`, validación en el servidor sin guardado parcial y vista previa del cálculo antes de guardar |
| 2 | Bitácora | Ficha › *Bitácora* | Entradas con tipo, autor, fecha y hora, próxima acción y fecha compromiso; no se editan ni se borran. Cada cambio de estado deja su entrada |
| 3 | Perfiles y HC | Ficha › *Perfiles* | Agregar, editar y quitar perfiles. HC de 1 a 999 y dedicación de 1 a 100 %. Un cambio de HC exige motivo |
| 4 | Tarifas | Ficha › *Perfiles* › *Cambiar tarifa* | Historia de tarifas por perfil, sin superposición; la nueva rige desde su mes y no reescribe los anteriores |
| 5 | Probabilidad y confiabilidad | Ficha › *Probabilidad · Confiabilidad* | P del catálogo en Pendiente; 100 % fijo al adjudicar (H-01). C solo por Operaciones. Ambas con motivo y vigencia mensual. El cambio de flujo en Pendiente sugiere la P |
| 6 | Observaciones y fechas | Ficha › *Datos del registro* | Observaciones separadas de la bitácora; fechas de ingreso, fin de vigencia, adjudicación y cierre. Bloqueo optimista: si otra persona guardó antes, se informa el conflicto (409) sin pisar los datos |
| 7 | Mantenedor de la MAB | *Parámetros MAB* | Horas mensuales con vigencia mensual (180 h iniciales, S-01), solo Operaciones, auditadas con su impacto en el Forecast. El detalle del cálculo de cada registro muestra la fórmula y sus componentes |
| 8 | Dashboard ejecutivo | *Dashboard* | Los 11 datos del OnePage, más Backlog contractual, Backlog confirmado, meta, gap y cobertura. Además: gráfico de 12 meses con tabla equivalente, vista de 3, 6 o 12 meses y 11 filtros combinables. Cortes por sector, owner, cliente, estado y flujo; alertas de ingresos a 30, 60 y 90 días, contratos por vencer y liberaciones. Cada indicador abre su lista de registros, y cada registro, su detalle mes a mes (3 interacciones o menos, SC-009) |
| 9 | Auditoría completa | *Auditoría* y ficha | Un evento por campo, con usuario, fecha y hora, valor anterior y nuevo, motivo, fecha efectiva e impacto en la MAB y el Forecast de 12 meses. Filtros por registro, campo, usuario y fechas. Solo lectura: `PUT` y `DELETE` responden 405 |

**Estados y flujo (US2):**

- Pendiente → Adjudicada → En Curso, con las condiciones de la máquina de estados (`data-model.md`). Adjudicar cambia el tipo a Demanda y fija P en 100 %.
- StandBy guarda el estado previo, sale del cálculo y la reactivación lo restaura.
- Para cerrar o cancelar se exige un motivo del catálogo; el efecto en el Forecast depende de él (FR-005).
- Solo Operaciones reabre. Las transiciones inválidas se rechazan con un mensaje que indica el paso faltante.

**Seguridad (RNF-05):**

- **Contraseñas y sesión:** Argon2id; sesión de servidor en cookie `HttpOnly`, `SameSite=Strict` y `Secure`, con expiración a los 30 minutos de inactividad.
- **Bloqueo:** 15 minutos tras 5 intentos fallidos, por cuenta y por IP.
- **CSRF:** token en todo `POST`, también en HTMX.
- **Cabeceras:** CSP sin scripts en línea, `X-Frame-Options`, `nosniff` y HSTS.
- **Permisos:** se aplican en el servidor, no solo en la interfaz.

## 4. Acceso al repositorio

- **Repositorio:** GitLab de NTT DATA, proyecto `FUNDCH/app-demanda`.
- **Ramas:** `entrega-1` y `entrega-2`, cada una con su merge request a `main`.

| Qué | Dónde |
|---|---|
| Código | `src/proyecta/`: `domain/` (entidades, motor y estados), `application/` (casos de uso), `infrastructure/` (memoria y autenticación) e `interfaces/` (web y API) |
| Pruebas | `tests/unit/domain/` (motor, casos C-01 a C-08, redondeo y estados) y `tests/integration/` (casos de uso, semilla, IA simulada y la app por HTTP) |
| Imagen | `deploy/Dockerfile` |
| Especificación | `specs/001-proyecta-mvp/` y `docs/fuentes/requerimientos.md` (v1.1) |
| Guías del equipo | `docs/guias-equipo/`, `docs/revisiones-tareas/` y `docs/mockups/` |

## 5. Instrucciones básicas de uso

### Recorrido de 5 minutos

1. **Operaciones:** entra al *Dashboard*. Revisa el Forecast y la serie mensual contra la meta. Abre una cifra (por ejemplo, *Backlog confirmado*) para ver sus registros y, desde ahí, un registro con su cálculo mes a mes; cada mes se despliega con sus componentes.
2. **Líder 1:** crea una oportunidad en *Nuevo registro* con un perfil de 3 HC a $2.600/h. Antes de guardar, la vista previa muestra una Base de $1.404.000 al mes con 180 h.
3. En la ficha, cambia el flujo a *2 · Propuesta en curso* (la P sugerida pasa a 25 %). Después adjudica: el tipo pasa a Demanda, la P a 100 % y el registro aparece en el Backlog confirmado.
4. Agrega una entrada de bitácora y revisa la *Auditoría* de la ficha: cada campo cambiado tiene su motivo y su impacto en el Forecast.
5. **Operaciones:** en *Parámetros MAB*, cambia las horas mensuales desde un mes futuro. Los meses anteriores no cambian; los siguientes sí, y el cambio queda auditado.
6. **Ejecutivo:** entra y comprueba que solo puede leer. Las acciones de edición no aparecen, y el servidor las rechaza con 403 si se fuerzan.

### Correrlo localmente

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
pytest
uvicorn proyecta.main:app --reload                      # http://127.0.0.1:8000
# o con la imagen de producción:
docker build -f deploy/Dockerfile -t proyecta .
docker run -p 8080:8080 -e PROYECTA_DEMO_PASSWORD=<clave> proyecta
```

| Variable | Uso | Por defecto |
|---|---|---|
| `PROYECTA_ENV` | `dev` habilita `/api/docs` y la cookie sin `Secure` (solo para HTTP local) | `prod` en la imagen; `dev` fuera de ella |
| `PROYECTA_DEMO_PASSWORD` | Contraseña de las cuentas sintéticas | `proyecta-demo` (cambiarla al desplegar) |
| `PORT` | Puerto del servicio (Cloud Run y Render lo entregan) | `8080` |

## 6. Evidencias de pruebas

| Evidencia | Resultado | Dónde |
|---|---|---|
| Pruebas automáticas | **88 aprobadas, 0 fallidas**: motor (C-01 a C-08, redondeo), dominio, estados, casos de uso, semilla, simulación y la app completa por HTTP (sesión, bloqueo, CSRF, permisos por rol, alta, cálculo, ciclo de vida, conflicto de versión, auditoría de solo lectura, horas con vigencia y totales del dashboard iguales a la suma por sector) | [`evidencias/pruebas.txt`](docs/entrega-2/evidencias/pruebas.txt) |
| Cobertura del dominio | **93 %** (meta: 90 %, SC-010) | [`evidencias/pruebas.txt`](docs/entrega-2/evidencias/pruebas.txt) |
| Casos de la especificación | US3 esc. 1: Base $1.404.000 (3 HC × $2.600 × 180 h). US3 esc. 2: MAB $631.800 con P 50 % y C 90 % | `tests/integration/test_app.py` |
| Recorrido en navegador | Chromium sin errores de consola; sin desplazamiento horizontal a 390 px (teléfono) | [`evidencias/`](docs/entrega-2/evidencias/) (capturas 00 a 11) |
| Rendimiento | Dashboard con 1.000 registros: p95 de 0,79 s en local (meta: menos de 2 s, SC-005) | Medición del 12/11 con el cliente de pruebas |
| Imagen Docker | Construida y probada por HTTP: `/health`, estáticos, inicio de sesión y `/api/docs` cerrado sin sesión. Corre como usuario `nobody` | `deploy/Dockerfile` |

## 7. Limitaciones conocidas

| Limitación | Efecto | Cuándo se resuelve |
|---|---|---|
| **Persistencia en memoria**, no Datastore: falta el proyecto de GCP (S-12) | Al reiniciar el servicio se vuelve a los 60 registros sintéticos y se pierde lo creado | Cuando NTT DATA entregue el proyecto: los repositorios de Datastore (T018–T024) implementan los mismos puertos |
| **Hosting temporal gratuito**, no Cloud Run | Se suspende sin uso; la primera carga tarda cerca de un minuto | Con el proyecto de GCP |
| Cuentas compartidas de demostración; sin administración de usuarios ni recuperación de contraseña | No hay altas de usuarios desde la app | E3 (US8, T130) |
| Metas sintéticas, sin mantenedor | El gap y la cobertura se calculan, pero las metas no se editan | E3 (US5) |
| Sin cierre de período ni puente (US6), sin semáforo de calidad (US7, solo un conteo) y sin exportación a Excel (US9) | Funcionalidades de prioridad 2 | E3 |
| Sin grilla de altas y bajas ni ajustes de HC en la interfaz (FR-016) | El motor ya considera los ajustes; falta la pantalla | E3 |
| Asistente de IA y simulador (US10) no expuestos en la interfaz | El código existe y tiene pruebas, pero quedan 5 observaciones de la revisión del 12/11 (§9) | E3 o con holgura |
| Reglas sin validación del sponsor: 180 h (S-01), 100 % al adjudicar (H-01), sexta etapa (S-02) | Pueden cambiar los montos | Las horas y la confiabilidad son parámetros con vigencia; un cambio de regla no exige rehacer pantallas |
| El bloqueo por IP usa la IP que informa el proxy del hosting | Un atacante podría variarla; el bloqueo por cuenta sigue activo | Revisión de seguridad T159 |
| Sin pipeline de CI: las pruebas corren en local | Falta un runner de GitLab | Cuando haya runner (T011) |
| Accesibilidad sin auditoría WCAG completa | Hay etiquetas visibles, foco visible, tabla alternativa al gráfico y diseño adaptable; faltan lector de pantalla y medición de contraste | E3 (T158) |

## 8. Estado actualizado del backlog

Estado al 12/11. «Implementado» significa que hay código y pruebas en la rama `entrega-2`. Ninguna tarea se marca como cerrada en `tasks.md` hasta que la revise su responsable (regla de [`docs/guias-equipo/README.md`](docs/guias-equipo/README.md)).

| Orden | Historia | Entrega | Estado al 12/11 | Revisa |
|:-:|---|:-:|---|---|
| 0 | Fundación | E2 | **Implementado, salvo Datastore y CI**: app, configuración por entorno, sesión con tres roles, Argon2, bloqueo, CSRF, permisos, auditoría, wiring de la API, recursos locales y semilla | Matías, Felipe y Roberto |
| 1 | US1 · Registrar y mantener | E2 | **Implementado**: alta de los tres tipos, edición con versión, perfiles, tarifas con historia, observaciones, fechas, bitácora y vista previa | Bryam |
| 2 | US2 · Ciclo de vida, flujo y probabilidad | E2 | **Implementado**: máquina de estados, StandBy, cierre y cancelación con motivo, reapertura por Operaciones, P y C con vigencia mensual | Felipe |
| 3 | US3 · Calcular y explicar | E2 | **Implementado**: motor único (Nicolás) con C-01 a C-08 y detalle por mes y componente | Nicolás |
| 4 | US4 · Dashboard ejecutivo | E2 | **Implementado**: 11 datos, filtros, gráfico, cortes, alertas y detalle en 3 interacciones o menos | Leonardo |
| 5 | US8 · Auditoría y acceso (núcleo) | E2 | **Implementado**: auditoría por campo con impacto, consulta filtrable y permisos por rol y propiedad. Falta: exportar la auditoría y administrar usuarios | Roberto |
| 6 | US5 · Backlog, metas y gap | E3 | **Parcial**: continuidad con ficha de contrato, Backlog contractual, alertas de vencimiento, meta y gap por sector. Falta: mantenedor de metas y estado del contrato | Felipe |
| 7 | US6 · Cierre de período y puente | E3 | Pendiente | Felipe |
| 8 | US7 · Calidad del dato | E3 | Pendiente (solo el conteo de registros sin perfiles) | Bryam |
| 9 | US9 · Reportes y exportación | E3 | Pendiente | Leonardo |
| 10 | US10 · IA y simulador | E3 o con holgura | Código y pruebas listos (Nicolás); 5 observaciones abiertas; no expuesto en la interfaz | Nicolás |
| 11 | US11 · Carga inicial sintética | Con holgura | Generador, fixture y CLI listos (Nicolás) | Nicolás y Roberto |
| 12 | Cierre: seguridad, accesibilidad, documentación y demo | E3 | Pendiente | Todo el equipo |

## 9. Registro de la retroalimentación recibida

| Fecha | De quién | Retroalimentación | Qué se hizo |
|---|---|---|---|
| 15/10 | Sponsor (reunión) | Necesidad de una fuente única, trazabilidad de cambios y proyección explicable | Base del alcance (E1). En la E2: auditoría por campo con impacto y detalle de cada cifra |
| 12/11 | Alfredo (PO): revisión del trabajo de Nicolás | 5 observaciones en IA, simulación y carga: horas de la simulación, botones de sugerencias que no coinciden con la API, anonimización y citas, aplicador opcional y contador del cargador. Además: API sin wiring y plantillas sin `base.html` | API de forecast conectada (T034) y `base.html` disponible. Se corrigió además un empate de vigencias en el motor (dos cambios en el mismo mes). Las 5 observaciones siguen abiertas: el módulo de IA no se expone en esta entrega ([`revisiones-tareas/nicolas-huenchual.md`](docs/revisiones-tareas/nicolas-huenchual.md)) |
| 12/11 | Alfredo (PO): revisión UX del mockup | Foco de teclado, etiquetas visibles, alternativa textual al gráfico, adaptación móvil, la tarjeta MAB debe abrir todos los activos | Aplicado en la app: etiquetas persistentes, foco visible, tabla junto al gráfico, sin desborde a 390 px y cada indicador abre exactamente los registros que suma ([`mockups/revision-ux.md`](docs/mockups/revision-ux.md)) |
| `<<COMPLETAR>>` | Fundación: comentarios a la E1 | `<<COMPLETAR con lo recibido>>` | `<<COMPLETAR>>` |
| Pendiente | Sponsor | Validación de S-01 a S-06, H-01 y quién edita | Se pedirá con la URL de esta entrega |

## 10. Plan de mejoras para la siguiente etapa (E3, 25/11)

| Prioridad | Mejora | Responsable | Para |
|:-:|---|---|---|
| 1 | Datastore y Cloud Run, apenas exista el proyecto de GCP (T018–T024, T005) | Matías y Nicolás | Apenas llegue S-12 |
| 1 | Revisión de esta entrega por cada responsable (§8) y merge request a `main` | Todo el equipo | 16/11 |
| 1 | Validación con el sponsor sobre la URL: reglas S-01, H-01, quién edita, y un usuario por rol para probar | Alfredo | 18/11 |
| 2 | US5 completa: mantenedor de metas y estado del contrato | Felipe | 20/11 |
| 2 | US9: exportación a Excel con los filtros aplicados; US7: semáforo de calidad | Leonardo y Bryam | 21/11 |
| 2 | US6: cierre de período y puente | Felipe | 23/11 |
| 3 | US10: corregir las 5 observaciones y exponer el asistente con aprobación humana | Nicolás | 23/11 (si hay holgura) |
| 3 | Seguridad (T159), accesibilidad (T158), CI (T011) y prueba con 5 usuarios (SUS) | Roberto y Matías | 23/11 |
| 3 | Documentación, declaración de uso de IA, pitch y guion de la demo | Alfredo, con todo el equipo | 25/11 |

## 11. Atraso de esta entrega

El plazo era el 11/11 a las 23:59. La entrega se completó el 12/11. Hubo tres causas:

- el trabajo de dominio y motor se hizo en un repositorio paralelo y hubo que integrarlo;
- todavía no existe el proyecto de GCP para publicar en Cloud Run;
- la fundación (sesión, permisos y persistencia) se atrasó respecto del plan de la E1.

Se informa a la organización junto con esta entrega, según las Bases (§17). Para no repetirlo, el trabajo de todos entra al repositorio oficial mediante merge request, con revisión semanal del avance.
