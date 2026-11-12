# Feature Specification: Proyecta — Gestión de oportunidades, demandas y proyecciones

**Feature Branch**: `001-proyecta-mvp`

**Created**: 2026-10-27

**Status**: Draft — para validación con el sponsor

**Input**: User description: "Centralizar la gestión de oportunidades y demandas, controlar sus estados y mantener trazabilidad de los datos utilizados para analizar la operación y generar proyecciones."

**Fuentes prioritarias**: `docs/fuentes/requerimientos.md` v1.1 (2026-10-29) y sus anexos; `docs/fuentes/reunion_mejorada.md`; `docs/fuentes/resumen_transcripcion_reunion.md`; `docs/fuentes/Onepage-desafio.pdf`; `Heavy-Duty_APPGestionDeLaDemanda_V3.pdf` (no versionado por incluir datos personales del equipo; lo custodia el PO); `Octubre26.SemanaX.Demanda.GDN_Plantilla.xlsx` (no versionado por contener datos reales; lo custodia el PO); `.specify/memory/constitution.md` v1.0.1. No existe código de aplicación en el repositorio.

## Clarifications

### Session 2026-10-27

- Q: Cuando un registro se cancela con motivo `DUPLICADO`, ¿debe salir del Forecast desde el mes de cierre o prorratear hasta la fecha de cancelación como el resto de las cancelaciones? → A: El motivo prevalece: `DUPLICADO` sale desde el mes de cierre; `CANCELADA_CLIENTE` y `TERMINO_SERVICIO` prorratean hasta su fecha.
- Q: ¿Qué cambios deben exigir un motivo escrito además de la auditoría automática de valores y usuario? → A: Lista amplia: estado, tipo, flujo, probabilidad, confiabilidad, cierre, reapertura, tarifa, HC y meta.
- Q: Cuando Operaciones cambia la confiabilidad o la probabilidad con fecha efectiva, ¿cómo debe conservarse el valor de los meses anteriores? → A: Historial por mes: cada valor tiene vigencia mensual, cada mes usa el valor vigente y un cambio no reescribe los meses anteriores.
- Q: ¿El 90 % de una oportunidad adjudicada debe aplicarse siempre, o solo cuando ya fue levantada a Staffing? → A: 100 % al adjudicar: se elimina el 90 % y la probabilidad queda en 100 % al pasar a `Adjudicada`, como la práctica del Excel; requiere validación del sponsor y actualización de `requerimientos.md` porque reemplaza `D-04`.
- Q: Mientras el sponsor valida las 180 h, ¿qué valor debe usar el MVP para calcular y migrar los montos? → A: 180 h: se usa de forma provisional para cálculo y migración; la validación con el sponsor sigue abierta (`S-01`).

**Ronda 2 — solicitada por el PO (excepción al límite de 5):**

- Q: ¿El MVP debe permitir cambiar las horas mensuales durante el horizonte de 12 meses, o deben quedar fijas en 180 h? → A: Editables con vigencia mensual: Operaciones puede cambiar las horas con fecha efectiva; cada mes usa el valor vigente, el cambio no reescribe meses anteriores y el puente incluye el efecto horas.
- Q: ¿Dónde y cómo se migran los cuatro registros reales del Excel, si la demo y las pruebas deben usar datos sintéticos? → A: Sin migración real en el MVP: solo se carga la estructura de la plantilla con datos sintéticos; los cuatro registros reales se revisan en una etapa posterior, fuera de la demo.
- Q: ¿Cómo debe tratarse el Backlog confirmado en el dashboard y el Forecast? → A: Vista de la MAB, no bolsa separada: P=100 y confiabilidad aplicada, sin sumarse aparte; la Continuidad va al Backlog contractual.

## User Scenarios & Testing *(mandatory)*

### Actores y responsabilidades

| Actor | Responsabilidad | Alcance |
|---|---|---|
| **Líder** | Registra y mantiene sus oportunidades y demandas: datos comerciales, perfiles, HC, tarifas, fechas, estado, probabilidad, contexto y bitácora. | Solo los registros de los que es `owner`; lectura de sus agregados. No ajusta confiabilidad, metas, catálogos ni cierres de período. |
| **Operaciones** | Centraliza el seguimiento, valida la calidad del dato, ajusta confiabilidad, parámetros, catálogos, metas, contratos de continuidad, usuarios y cierres. | Todos los registros y la configuración. No edita ni borra auditoría ni bitácora. |
| **Ejecutivo** | Consume dashboards y reportes para tomar decisiones. | Lectura y exportación de todos los registros y reportes; sin edición. |
| **Staffing / Recruiting** | Proceso externo que busca y asigna personas. | No accede a la plataforma en el MVP; solo se registra el indicador `En Staffing`. |
| **Invoicing** | Proceso externo que registra la previsión de facturación. | No accede a la plataforma en el MVP; solo se registra el indicador `En Invoicing`. |
| **Sponsor** | Define metas, valida reglas de negocio y recibe proyecciones. | No es un rol operativo del sistema; participa en la validación de requisitos y decisiones abiertas. |

### Flujos principales y alternativos

**F1 · Alta y seguimiento de una oportunidad.** El líder crea una oportunidad en estado `Pendiente`, flujo 1 y probabilidad 10 %, con sus campos, perfiles, tarifas y fechas. Avanza por los flujos 2 a 5; cada avance registra bitácora y auditoría. Al adjudicarse, con fecha y al menos un perfil, pasa a `Adjudicada`, cambia a tipo `Demanda` y probabilidad 100 %. Al confirmar perfiles pasa al flujo 6 con probabilidad 100 % y aparece en la vista de Backlog confirmado. Al iniciar el servicio pasa a `En Curso`; al terminar se cierra con motivo.

**F2 · Demanda directa.** Operaciones o un líder registra una demanda ya adjudicada, con motivo de demanda directa, fecha de adjudicación y al menos un perfil; nace en `Adjudicada` con flujo 3 a 5 y probabilidad 100 %.

**F3 · Continuidad y Backlog.** Operaciones registra un contrato vigente como tipo `Continuidad`, con ficha de contrato, estado `En Curso`, flujo 6 y probabilidad y confiabilidad 100 %. Aporta al Backlog contractual, no a la MAB, y genera alertas de vencimiento.

**F4 · Proyección y consulta.** El sistema calcula Base, MAB, Backlog contractual, Backlog confirmado, Forecast, Ingreso potencial, HC proyectado, Gap y cobertura. El usuario consulta el dashboard, filtra y abre cada cifra hasta los registros y componentes que la explican.

**F5 · Cierre mensual y puente.** Operaciones cierra el período; el sistema congela por registro y mes la base, probabilidad, confiabilidad, MAB, Backlog y HC. Dos cortes del mismo mes se comparan con un puente que descompone la variación por causa.

**F6 · Corrección y reapertura.** Un registro cerrado o cancelado solo se reabre por Operaciones con motivo. Una corrección de bitácora o auditoría es una entrada nueva que referencia la anterior; nunca se edita ni se borra.

**F7 · Carga inicial.** La carga inicial importa la estructura de la plantilla con revisión de Operaciones, normaliza catálogos, crea el perfil migrado y los ajustes, recalcula los montos y reporta las inconsistencias por fila sin corregirlas en silencio.

**F8 · Calidad y pendientes.** El sistema evalúa las reglas de calidad, asigna semáforo y lista los pendientes del líder; Operaciones ve todos y puede priorizar la corrección.

**F9 · Apoyo opcional de IA y simulación.** El asistente propone ajustes citando la bitácora y requiere aprobación humana; el simulador calcula escenarios sobre una copia aislada. Ninguno de los dos modifica datos reales ni bloquea el MVP.

**Flujos alternativos:**

- **A1 · Pausa.** Cualquier estado no terminal pasa a `StandBy` con motivo; se guarda el estado previo, se congelan probabilidad y confiabilidad y el registro sale del cálculo. La reactivación restaura el estado previo.
- **A2 · Cancelación.** El registro pasa a `Cancelada` con motivo y fecha; `CANCELADA_CLIENTE` y `TERMINO_SERVICIO` prorratean hasta la fecha y luego salen; `DUPLICADO` sale desde el mes de cierre.
- **A3 · Pérdida o desestimación.** El registro se cierra con motivo `Pérdida` o `Desestimada` y sale del Forecast desde el mes de cierre.
- **A4 · Edición concurrente.** El segundo usuario que guarda sobre una versión desactualizada recibe un conflicto, conserva lo escrito y ve la versión vigente.
- **A5 · Datos incompletos.** El sistema bloquea el guardado si falta un campo obligatorio o una regla roja; si el registro puede existir incompleto, lo marca y lo muestra en la lista de pendientes.
- **A6 · Meta faltante.** Si el sector y mes no tienen meta, no se calcula el gap y se activa `DQ-12`.
- **A7 · Contrato vencido.** El contrato se marca `Vencido`, genera alerta roja y deja de sumar Backlog desde el mes siguiente al vencimiento.
- **A8 · Perfil rechazado.** Si el cliente rechaza un perfil, el registro vuelve de `Perfiles seleccionados` a `Adjudicada` o `Validando candidatos` con motivo; la probabilidad se mantiene en 100 % por seguir en `Adjudicada` (H-01).
- **A9 · Fechas heredadas inválidas.** La migración marca las fechas inválidas para revisión; no las corrige ni las inventa.
- **A10 · Simulación sobre un corte cerrado.** El simulador no altera el corte; el resultado se rotula como simulado y no se persiste.

### User Story 1 - Registrar y mantener una oportunidad o demanda (Priority: P1)

Un líder registra una oportunidad o demanda con sus datos comerciales, uno o más perfiles con HC y tarifa, fechas y observaciones; la mantiene actualizada, agrega bitácora y la cierra con motivo cuando corresponde.

**Why this priority**: sin un registro único y completo no existe pipeline, cálculo ni trazabilidad. Es la base de todo el MVP.

**Independent Test**: crear una oportunidad con dos perfiles y verificar que se guarda con código, estado, flujo y probabilidad iniciales, que muestra la previsualización de cálculo y que genera el evento de creación en la auditoría.

**Acceptance Scenarios**:

1. **Dado** un líder autenticado, **cuando** crea una oportunidad con los campos obligatorios y dos perfiles con HC, dedicación, tarifa y fechas, **entonces** el sistema la guarda en `Pendiente`, flujo 1, probabilidad 10 % y confiabilidad 90 %, muestra Base/MAB/Forecast antes de guardar y registra el evento de creación.
2. **Dado** un registro en edición, **cuando** se intenta guardar un perfil con HC fuera de rango, tarifa no positiva o fechas incoherentes, **entonces** el sistema bloquea el guardado y explica el campo y la regla incumplida.
3. **Dado** un registro leído por dos usuarios, **cuando** el segundo guarda después del primero, **entonces** el sistema informa el conflicto, conserva lo escrito y muestra la versión vigente sin perder datos.
4. **Dado** un registro abierto, **cuando** el líder lo cierra con motivo y fecha, **entonces** el estado cambia a `Cerrada` o `Cancelada`, el registro sale del cálculo según el motivo, no se borra y queda auditado.
5. **Dado** un registro existente, **cuando** el líder agrega una entrada de bitácora con próxima acción y fecha compromiso, **entonces** la entrada queda con autor, fecha/hora y no puede editarse ni borrarse.

---

### User Story 2 - Avanzar el ciclo de vida, el flujo y la probabilidad (Priority: P1)

Un líder u Operaciones mueve el registro entre estados y etapas comerciales, ajusta la probabilidad dentro de las reglas y pausa, reactiva, cierra o reabre según corresponda.

**Why this priority**: el pipeline debe reflejar la realidad comercial y evitar que una venta desaparezca de la proyección o reaparezca como facturación no planificada.

**Independent Test**: recorrer una oportunidad desde `Pendiente` hasta `En Curso`, pasando por `Adjudicada` y `Perfiles seleccionados`, y verificar probabilidad, tipo, vista de Backlog confirmado y eventos de auditoría en cada transición.

**Acceptance Scenarios**:

1. **Dado** un registro `Pendiente` con 50 %, **cuando** el líder lo pasa a `Adjudicada` con fecha y al menos un perfil, **entonces** el tipo cambia a `Demanda`, la probabilidad pasa a 100 % y se audita el cambio.
2. **Dado** un registro `Adjudicada` con perfil activo, **cuando** pasa a `Perfiles seleccionados`, **entonces** la probabilidad se fija en 100 %, la MAB se recalcula aplicando confiabilidad y el registro aparece en la vista de Backlog confirmado.
3. **Dado** un registro en cualquier estado no terminal, **cuando** pasa a `StandBy` con motivo, **entonces** se guarda el estado previo, se congelan probabilidad y confiabilidad, sale del cálculo y la reactivación restaura el estado previo.
4. **Dado** un registro `Pendiente`, **cuando** se intenta pasar directamente a `En Curso`, **entonces** la transición se rechaza con un mensaje que indica el paso faltante.
5. **Dado** un registro `Adjudicada` sin perfil, **cuando** se intenta confirmar perfiles o pasar a `En Curso`, **entonces** el sistema bloquea la operación y solicita al menos un perfil con HC y fecha de ingreso.

---

### User Story 3 - Calcular y explicar la proyección (Priority: P1)

Operaciones y la capa ejecutiva consultan la Base, la MAB, el Backlog contractual, el Forecast, el Ingreso potencial, el HC proyectado y el Gap, y abren cada cifra hasta los registros y componentes que la respaldan.

**Why this priority**: el valor del producto es una proyección defendible; una cifra sin detalle no reemplaza la planilla.

**Independent Test**: cargar dos registros y un contrato, calcular la serie de 12 meses y verificar cada fórmula contra los casos de referencia C-01 a C-08 y el detalle de cada cifra.

**Acceptance Scenarios**:

1. **Dado** un registro con 3 HC y tarifa de $2.600/h, **cuando** se calcula la Base mensual con 180 h, **entonces** el resultado es $1.404.000 y la ficha muestra la fórmula y el parámetro utilizado.
2. **Dado** el mismo registro con probabilidad 50 % y confiabilidad 90 %, **cuando** se calcula la MAB, **entonces** el resultado es $631.800 y el detalle muestra Base, probabilidad y confiabilidad.
3. **Dado** un contrato de continuidad de $45.000.000 mensuales, **cuando** se consulta el Forecast, **entonces** el Backlog contractual aporta $45.000.000, la MAB es 0 y el registro aparece una sola vez.
4. **Dado** un registro en la MAB con probabilidad 100 %, **cuando** se consulta el Forecast, **entonces** el registro aparece una sola vez y no se suma también al Backlog contractual.
5. **Dado** una cifra del dashboard, **cuando** el usuario la abre, **entonces** ve los registros que la componen y los componentes de cálculo (HC, dedicación, tarifa, días activos, probabilidad y confiabilidad).
6. **Dado** una edición en curso, **cuando** el usuario previsualiza el cálculo, **entonces** el resultado es transitorio, no se persiste y no altera estados ni cortes.

---

### User Story 4 - Consultar el dashboard ejecutivo (Priority: P1)

La capa ejecutiva revisa los 11 datos críticos del OnePage más Backlog, Meta, Gap, calidad y pipeline, filtra por las dimensiones del negocio y abre el detalle de cada indicador.

**Why this priority**: reemplaza la consolidación manual de planillas y da una lectura ejecutiva única y semanal.

**Independent Test**: abrir el dashboard con datos sintéticos, aplicar filtros y verificar que los totales corresponden a los registros visibles y que cada cifra se puede abrir hasta su detalle.

**Acceptance Scenarios**:

1. **Dado** un conjunto de datos, **cuando** se abre el dashboard, **entonces** se muestran oportunidades activas, demandas confirmadas, HC proyectado, ingresos potenciales, MAB, Forecast, probabilidad, confiabilidad, fecha de ingreso, cliente/sector y responsable, más Backlog, Meta, Gap, calidad y pipeline.
2. **Dado** un dashboard con filtros de período, sector, cliente, manager, owner, tipo, estado, flujo, modalidad, Studio y tecnología, **cuando** se combinan, **entonces** los totales son la suma de los registros visibles y no se recalculan desde promedios.
3. **Dado** un registro con ingreso en 30, 60 o 90 días, **cuando** se consulta el dashboard, **entonces** aparece en la lista de próximos ingresos; los contratos por vencer se alertan a 90, 60 y 30 días y las liberaciones a 90 días.
4. **Dado** un usuario con rol Ejecutivo, **cuando** intenta editar o crear, **entonces** el sistema no ofrece la acción y rechaza la operación.
5. **Dado** cualquier indicador, **cuando** el usuario lo selecciona, **entonces** llega en no más de tres interacciones a los registros que lo respaldan.

---

### User Story 5 - Gestionar Backlog, metas y gap (Priority: P1b)

Operaciones mantiene la ficha de los contratos de continuidad, el monto mensual comprometido y las metas por sector y mes; el sistema calcula el Backlog contractual, el Gap y la cobertura.

**Why this priority**: el sponsor pidió explícitamente el módulo de Backlog, Meta y Gap; sin él la proyección no se compara con el objetivo comercial.

**Independent Test**: registrar un contrato de continuidad y una meta, y verificar Backlog mensual, clasificación de vencimiento, Gap y cobertura por sector.

**Acceptance Scenarios**:

1. **Dado** un contrato de continuidad con código, inicio, fin o indefinido, monto mensual o perfiles y HC comprometido, **cuando** se registra, **entonces** queda en `En Curso`, flujo 6, probabilidad y confiabilidad 100 %, y aporta al Backlog contractual del mes.
2. **Dado** un contrato vigente, **cuando** se consulta su estado, **entonces** se clasifica `Vigente`, `Por vencer` o `Vencido`, y se alerta a 90, 60 y 30 días del término.
3. **Dado** una meta de $1.700.000.000 y un Forecast de $1.500.000.000, **cuando** se consulta el dashboard, **entonces** el gap es $200.000.000, la cobertura es 88,2 % y el semáforo es rojo.
4. **Dado** un sector y mes sin meta, **cuando** se consulta el gap, **entonces** no se calcula y se activa `DQ-12`.
5. **Dado** un cambio de meta, **cuando** Operaciones lo guarda, **entonces** se audita con valor anterior, nuevo, usuario y fecha; los cortes cerrados conservan la meta congelada.

---

### User Story 6 - Cerrar el período y explicar la variación (Priority: P2)

Operaciones ejecuta el cierre mensual, congela el corte y compara dos cortes del mismo mes para explicar la variación del Forecast por causa.

**Why this priority**: permite defender la evolución de la proyección y separar decisiones comerciales de cambios de parámetros.

**Independent Test**: ejecutar dos cierres consecutivos con cambios de base, probabilidad y confiabilidad, y verificar que el puente suma exactamente la variación total.

**Acceptance Scenarios**:

1. **Dado** un período abierto, **cuando** Operaciones lo cierra, **entonces** el corte congela por registro y mes la base, probabilidad, confiabilidad, MAB, Backlog y HC, y queda inmutable.
2. **Dado** dos cortes del mismo mes, **cuando** se compara, **entonces** el puente descompone la variación en registros nuevos, cerrados, efecto base, probabilidad, confiabilidad, parámetros, Backlog y horizonte, y la suma coincide con la variación total.
3. **Dado** una diferencia de redondeo, **cuando** se muestra el puente, **entonces** se informa en una línea separada y no supera 1 CLP por registro-mes.
4. **Dado** un corte cerrado, **cuando** se corrige un dato, **entonces** se genera una nueva versión del corte y no se sobreescribe el anterior.
5. **Dado** un cierre ejecutado, **cuando** el equipo sigue editando el pipeline, **entonces** la edición no se bloquea y el siguiente corte refleja los cambios.

---

### User Story 7 - Evaluar la calidad del dato (Priority: P2)

Líderes y Operaciones consultan el semáforo de calidad, las reglas incumplidas y la lista de pendientes para corregir la información que afecta la proyección.

**Why this priority**: la calidad del dato es la causa raíz del problema; sin semáforo, los errores se descubren tarde.

**Independent Test**: crear registros con cada regla de calidad y verificar semáforo, severidad, responsable y lista de pendientes por rol.

**Acceptance Scenarios**:

1. **Dado** un registro con al menos una regla roja, **cuando** se evalúa, **entonces** el semáforo es rojo; con solo amarillas, amarillo; sin hallazgos, verde.
2. **Dado** un líder, **cuando** abre sus pendientes, **entonces** ve solo los de sus registros; Operaciones ve todos.
3. **Dado** un registro `En Curso` sin `Invoicing`, **cuando** se evalúa, **entonces** aparece rojo por `DQ-07` con la alerta de facturación no planificada.
4. **Dado** un registro `Adjudicada` sin `En Staffing`, **cuando** se evalúa, **entonces** aparece amarillo por `DQ-06`.
5. **Dado** un campo obligatorio incompleto, **cuando** se intenta guardar, **entonces** la validación de campo bloquea el guardado y la regla de calidad no reemplaza esa validación.

---

### User Story 8 - Auditar cambios y controlar el acceso (Priority: P2)

Operaciones y la capa ejecutiva consultan quién cambió qué, cuándo, con qué valor anterior y nuevo y qué impacto tuvo; cada rol accede solo a lo que le corresponde.

**Why this priority**: sin historial y permisos, la fuente no es confiable ni defendible.

**Independent Test**: cambiar estado, HC, tarifa, probabilidad, confiabilidad y fechas; verificar un evento por campo con impacto; intentar editar auditoría y acceder a registros de otro líder.

**Acceptance Scenarios**:

1. **Dado** un cambio de estado, HC, tarifa, probabilidad, confiabilidad, fecha, contrato, meta o parámetro, **cuando** se guarda, **entonces** se genera un evento con usuario, fecha/hora, valor anterior, valor nuevo, origen, fecha efectiva, motivo cuando corresponda e impacto en MAB y Forecast.
2. **Dado** un evento de auditoría o una entrada de bitácora, **cuando** se intenta editar o borrar, **entonces** el sistema no ofrece la acción y rechaza la operación; la corrección es una entrada nueva que referencia la anterior.
3. **Dado** un líder, **cuando** intenta editar un registro de otro líder, **entonces** el sistema rechaza la operación y no modifica nada.
4. **Dado** un usuario Ejecutivo, **cuando** consulta o exporta, **entonces** solo lee y no puede crear, editar, cerrar ni ajustar.
5. **Dado** un evento, **cuando** se consulta por registro, usuario, campo o fecha, **entonces** se puede filtrar y exportar respetando permisos.

---

### User Story 9 - Reportar y exportar (Priority: P2)

Los tres roles consultan los reportes definidos y exportan vistas, dashboard y auditoría a Excel respetando filtros y permisos.

**Why this priority**: la operación actual vive en Excel; la exportación facilita la transición y la revisión externa sin perder el control de acceso.

**Independent Test**: generar cada reporte, exportarlo con filtros y verificar que un líder no recibe datos de otros owners y que las celdas no ejecutan fórmulas.

**Acceptance Scenarios**:

1. **Dado** un usuario autenticado, **cuando** abre un reporte permitido, **entonces** ve el contenido definido para su rol y filtros.
2. **Dado** una vista filtrada, **cuando** se exporta, **entonces** el archivo respeta los filtros, incluye solo los registros permitidos y protege las celdas contra inyección de fórmulas.
3. **Dado** una exportación de auditoría, **cuando** se genera, **entonces** incluye valor anterior, valor nuevo, usuario, fecha, motivo e impacto.
4. **Dado** un líder, **cuando** exporta, **entonces** no recibe datos de registros de otros owners.

---

### User Story 10 - Recibir sugerencias de IA y simular escenarios sin alterar datos (Priority: P2b)

Un usuario recibe sugerencias de coherencia con cita y aprobación humana, y simula escenarios sobre una copia aislada; ninguna de las dos funciones modifica datos reales ni bloquea el MVP.

**Why this priority**: son aportes de valor diferencial, pero no son necesarios para registrar, calcular y auditar.

**Independent Test**: generar una sugerencia, aceptarla y verificar el evento de auditoría; ejecutar una simulación y verificar que no persiste ni cambia estados ni cortes.

**Acceptance Scenarios**:

1. **Dado** un registro con una contradicción entre bitácora y campos, **cuando** el asistente sugiere un ajuste, **entonces** cita la entrada que lo respalda, requiere aceptación o descarte humano y, al aceptarse, genera auditoría con origen `IA`; la IA nunca escribe sola.
2. **Dado** cualquier salida asistida por IA, **cuando** se muestra, **entonces** se clasifica como dato verificado, cálculo del sistema, estimación o datos insuficientes, e indica la fuente o lo que falta.
3. **Dado** que la IA no está disponible, **cuando** el usuario opera, **entonces** puede registrar, calcular, cerrar y auditar sin bloqueo.
4. **Dado** un escenario hipotético, **cuando** se ejecuta, **entonces** usa una copia aislada, no persiste, no cambia estados ni cortes y se rotula como simulado.
5. **Dado** un modelo externo, **cuando** se envía información, **entonces** no se envían datos reales de clientes, tarifas o ingresos sin autorización expresa.

---

### User Story 11 - Cargar los datos iniciales (Priority: P3)

La carga inicial importa la estructura de la plantilla con datos sintéticos y revisión de Operaciones, normaliza los catálogos, reconstruye perfiles y ajustes y reporta las inconsistencias por fila sin inventar ni corregir en silencio. Los cuatro registros reales no se migran en el MVP.

**Why this priority**: permite arrancar con la información existente, pero el MVP puede demostrarse con datos sintéticos.

**Independent Test**: importar un conjunto sintético con la estructura de la plantilla y cuatro registros de prueba, y verificar los cuatro registros creados, el recálculo a 180 h y el reporte de inconsistencias por fila.

**Acceptance Scenarios**:

1. **Dado** un conjunto sintético con la estructura de la plantilla y cuatro registros de prueba, **cuando** se ejecuta la importación, **entonces** se crean cuatro registros sintéticos, se informan las inconsistencias por fila y los montos se recalculan con 180 h.
2. **Dado** un registro sintético con HC cero en todos los meses, **cuando** se importa, **entonces** se migra sin perfil y se marca para revisión.
3. **Dado** un registro sintético con una fecha inválida, **cuando** se importa, **entonces** se marca para revisión y no se corrige automáticamente.
4. **Dado** una importación repetida, **cuando** se ejecuta, **entonces** es idempotente y no duplica registros.
5. **Dado** un ambiente de demo, **cuando** se carga, **entonces** usa datos sintéticos y no tarifas, clientes ni ingresos reales.

---

### Edge Cases

- **Registro cerrado con HC activo**: se marca como inconsistencia para revisión (`A-16`, `S-03`); no se corrige ni se borra automáticamente.
- **Cierre de HC negativo**: se bloquea el guardado y se explica la causa; no se ajusta a cero en silencio.
- **Perfil sin tarifa o tarifa no positiva**: se bloquea el guardado (`DQ-09`).
- **Tarifas superpuestas en un mismo perfil**: se rechaza la segunda (`RI-06`).
- **Meta duplicada para sector y mes**: se rechaza (`RI-07`).
- **Contrato sin fin de contrato o sin monto**: se bloquea el cierre del registro (`DQ-08`).
- **Cancelación con motivo `DUPLICADO`**: sale del Forecast desde el mes de cierre; `CANCELADA_CLIENTE` y `TERMINO_SERVICIO` prorratean hasta su fecha.
- **Cambio de confiabilidad con fecha efectiva**: el mes efectivo y los siguientes usan el nuevo valor; los meses anteriores conservan el suyo (`RN-37`, `AC-04`).
- **Cambio de horas con fecha efectiva**: los meses anteriores conservan su cálculo; el mes efectivo y los siguientes usan el nuevo valor y el puente lo muestra como efecto parámetros.
- **Sector o mes sin meta**: no se calcula el gap y se activa `DQ-12`.
- **Edición concurrente**: se informa el conflicto y se conserva lo escrito (`AC-13`).
- **Intento de borrado**: no existe borrado físico; se cierra con motivo y se rechaza la eliminación (`RN-81`).
- **Fechas heredadas inválidas** (`23-07-20206`, `28-06.2026`): se marcan para revisión; no se corrigen en silencio (`A-17`).
- **Comparación con la planilla**: los montos a 163 h no son comparables con los de 180 h; la diferencia de +10,43 % se explica al sponsor antes de la primera carga (`§16.3`, `S-01`).
- **Backlog confirmado con confiabilidad menor a 100 %**: se muestra como vista de la MAB con P=100 y C aplicada; no se presenta como peso pleno (`H-07`).
- **Corte cerrado**: no se edita; una corrección genera una nueva versión (`RN-72`).
- **Simulación sobre un corte**: no altera el corte ni se persiste; se rotula como simulada (`RF-35`).

## Requirements *(mandatory)*

> **Convención de identificadores**: `FR-###` y `NFR-###` son identificadores de esta especificación; `RF-xx`, `RN-xx`, `RNF-xx` y `AC-xx` son los identificadores fuente de `requerimientos.md`. La especificación no renumera los requisitos fuente.

### Functional Requirements

#### Registro y campos

- **FR-001**: El sistema DEBE crear oportunidades, demandas y continuidades con los campos del modelo, entre ellos: manager, owner, sector, cliente, servicio o proyecto, tecnologías requeridas para el servicio y para la interfaz, Studio y práctica, cuenta, identificador externo, tipo, estado, flujo, probabilidad, confiabilidad, fechas de creación, adjudicación, cancelación, cierre, ingreso y fin de vigencia, indicadores `En Staffing` y `En Invoicing`, y observaciones (`RF-01`, `§7.3`).
- **FR-002**: El sistema DEBE asignar un código único `OPD-####` y exigir manager y owner como campos distintos y obligatorios (`RF-09`, `RF-10`, `D-13`).
- **FR-003**: El sistema DEBE permitir editar un registro con control de versión; si otro usuario guardó antes, DEBE informar el conflicto, conservar lo escrito y mostrar la versión vigente (`RF-02`, `AC-13`).
- **FR-004**: El sistema DEBE validar campos obligatorios, rangos, catálogos y coherencia entre tipo, estado y flujo antes de guardar; un error DEBE ser explícito y no guardar parcialmente (`RF-03`).
- **FR-005**: El sistema DEBE cerrar un registro con motivo y fecha, sin borrarlo; el efecto en el Forecast DEBE depender del motivo: `PERDIDA`, `DESESTIMADA` y `DUPLICADO` salen desde el mes de cierre; `CANCELADA_CLIENTE` y `TERMINO_SERVICIO` prorratean hasta su fecha (`RF-04`, `§8.5`).
- **FR-006**: El sistema DEBE buscar y filtrar por código, cliente, sector, estado, flujo, owner, manager, modalidad y fechas (`RF-08`).
- **FR-007**: El sistema DEBE crear una demanda directa con motivo, estado `Adjudicada`, flujo 3 a 5, fecha de adjudicación y al menos un perfil (`RF-05`, `S-07`).
- **FR-008**: El sistema DEBE crear una continuidad con ficha de contrato, estado `En Curso`, flujo 6 y probabilidad y confiabilidad 100 % (`RF-06`, `D-11`).
- **FR-009**: El sistema DEBE mostrar Base, MAB, Backlog y Forecast antes de guardar, sin persistir el resultado (`RF-07`, `RF-35`).
- **FR-010**: El sistema DEBE mantener las observaciones separadas de la bitácora; una observación no reemplaza el historial cronológico (`RF-01`, `§7.3`).

#### Perfiles, HC y tarifas

- **FR-011**: El sistema DEBE permitir agregar, editar y quitar perfiles de un registro mientras no esté cerrado (`RF-11`).
- **FR-012**: El sistema DEBE validar HC entero entre 1 y 999, dedicación entre 1 % y 100 %, y fechas de perfil coherentes con la vigencia del registro (`RF-12`, `RI-03`).
- **FR-013**: El sistema DEBE mantener la historia de tarifas por perfil con fecha de vigencia, sin superposición; un cambio de tarifa no reescribe meses anteriores y exige motivo cuando reemplaza una tarifa anterior (`RF-13`, `RI-06`, `RN-44`).
- **FR-014**: El sistema DEBE calcular la tarifa media como `Σ(HC × tarifa) / Σ(HC)`, sin edición manual (`RF-14`, `RN-45`).
- **FR-015**: El sistema DEBE calcular el HC actual como la suma de HC de los perfiles activos a la fecha de consulta (`RF-14`, `RN-46`).
- **FR-016**: El sistema DEBE mostrar la grilla mensual de Altas, Bajas y Cierre de 12 meses, bloquear un cierre negativo y permitir ajustes de HC solo a Operaciones con motivo (`RF-15`, `RF-16`, `RF-17`, `RN-47`, `RN-48`, `RN-49`).
- **FR-017**: El sistema DEBE calcular el HC proyectado por mes, perfil, sector y grado de certeza: confirmado, por confirmar y oportunidad (`RF-18`, `RN-51`).

#### Estados, flujo, probabilidad y confiabilidad

- **FR-018**: El sistema DEBE aplicar únicamente las transiciones de estado permitidas, exigir el motivo de la transición y rechazar las inválidas con un mensaje que indique la regla incumplida (`RF-19`, `RF-22`, `§9.1`).
- **FR-019**: El sistema DEBE asignar la probabilidad por defecto según el flujo cuando el estado sea `Pendiente`, fijar 100 % en `Adjudicada`, `En Curso` y `Continuidad`, y validar cualquier otro valor contra el rango del estado (`RF-20`, `RN-29`, clarificación 2026-10-27).
- **FR-020**: El sistema DEBE fijar la probabilidad en 100 % al entrar a `Adjudicada`, `Perfiles seleccionados`, `En Curso` o `Continuidad`, sin edición (`RF-21`, `RN-31`, clarificación 2026-10-27).
- **FR-021**: El sistema DEBE fijar la probabilidad en 100 % al pasar a `Adjudicada`, sin rango 80–95 %; cada cambio de probabilidad DEBE exigir motivo y fecha efectiva, y la probabilidad DEBE tener vigencia mensual sin reescribir meses anteriores. Esta decisión de la sesión 2026-10-27 reemplaza `D-04` y `RN-30`, está incorporada en `requerimientos.md` v1.1 (`A-21`) y requiere validación del sponsor (clarificación 2026-10-27).
- **FR-022**: El sistema DEBE preservar el estado previo al pasar a `StandBy`, congelar probabilidad y confiabilidad, excluir el registro del cálculo y restaurar el estado al reactivar (`RF-24`, `RF-26`, `RN-34`).
- **FR-023**: El sistema DEBE tratar `Cerrada` y `Cancelada` como estados terminales; solo Operaciones puede reabrir con motivo y la reapertura vuelve a `Pendiente` o `Adjudicada` según el tipo (`RF-04`, `RN-20`, `RN-25`).
- **FR-024**: El sistema DEBE cambiar el tipo a `Demanda` al adjudicar una oportunidad; solo Operaciones puede revertirlo con motivo y el cambio DEBE auditarse (`RN-24`).
- **FR-025**: El sistema DEBE usar siempre el flujo 6 en `Continuidad`; una continuidad no recorre las etapas comerciales ni puede estar en `Pendiente` o `Adjudicada` (`RN-09`, `RN-23`, `RN-27`).
- **FR-026**: El sistema DEBE iniciar la confiabilidad en 90 % (100 % en continuidad), permitir solo a Operaciones cambiarla con motivo y fecha efectiva, y hacerla vigente por mes sin reescribir meses anteriores (`RF-23`, `RN-35`, `RN-36`, `RN-37`).
- **FR-027**: El sistema DEBE auditar todo cambio de probabilidad y confiabilidad con valor anterior, valor nuevo, usuario, fecha y motivo cuando corresponda (`RF-22`, `RF-47`).
- **FR-028**: El sistema DEBE admitir los catálogos de tres tipos, seis estados, seis flujos y los valores de probabilidad 5, 10, 12, 20, 25, 30, 50, 75, 80, 90, 95 y 100 %, normalizando los valores heredados y sus alias; los valores 80, 90 y 95 % se conservan para migración e históricos, pero una `Adjudicada` usa 100 % (`§8`, `RN-14`, `D-14`, clarificación 2026-10-27).

#### Cálculo y proyección

- **FR-029**: El sistema DEBE calcular la Base mensual de un registro como `Σ [HC × dedicación × tarifa vigente × horas del mes × fracción activa]`, prorrateando por días el ingreso, el término y la cancelación (`RF-27`, `RF-30`, `§10.2`, `§10.3`).
- **FR-030**: El sistema DEBE calcular la MAB de un registro en la bolsa MAB como `Base × probabilidad × confiabilidad` (`RF-28`, `§10.4`).
- **FR-031**: El sistema DEBE calcular el Backlog contractual de una continuidad como `monto mensual × fracción activa del contrato`; si no hay monto, DEBE usar la Base de sus perfiles al 100 % (`RF-28`, `RF-37`, `RN-61`).
- **FR-032**: El sistema DEBE calcular el Backlog confirmado como vista de la MAB con probabilidad 100 % y confiabilidad aplicada; no DEBE sumarse por separado (`RF-28`, `RN-38`, `RN-83`). La expresión «100 % (Backlog)» del resumen no implica confiabilidad 100 % (`H-07`).
- **FR-033**: El sistema DEBE calcular el Forecast como `Backlog contractual + MAB`; cada registro DEBE pertenecer a una sola bolsa por mes y no DEBE contarse dos veces (`RF-29`, `RN-83`, `AC-05`).
- **FR-034**: El sistema DEBE calcular el Ingreso potencial como la Base sin ponderar de la MAB más el Backlog contractual (`RF-31`, `§10.4`).
- **FR-035**: El sistema DEBE calcular el HC proyectado como la dotación al cierre de cada mes, con `Cierre = Cierre anterior + Altas − Bajas` (`RF-18`, `§10.5`).
- **FR-036**: El sistema DEBE calcular una serie de 12 meses móviles con vistas de 3, 6 y 12; los montos DEBEN redondearse a CLP entero half-up al final de cada registro-mes y los totales DEBEN sumar valores ya redondeados (`RF-27`, `RF-34`, `§10.8`, `RN-86` a `RN-88`).
- **FR-037**: El sistema DEBE mantener las horas mensuales como parámetro editable por Operaciones, con fecha efectiva y vigencia mensual; cada mes DEBE usar el valor vigente, un cambio NO DEBE reescribir meses anteriores y DEBE registrar motivo, usuario y fecha efectiva. La confiabilidad inicial, los rangos y los umbrales también son parámetros con vigencia y auditoría (`RF-33`, `RF-51`). El valor inicial es 180 h y su validación con el sponsor sigue abierta (`S-01`).
- **FR-038**: El sistema DEBE reproducir los casos de referencia `C-01` a `C-08` como resultados esperados del motor (`§10.9`).

#### Backlog, metas y gap

- **FR-039**: El sistema DEBE mantener la ficha de contrato de una continuidad con código único, inicio, fin o condición de indefinido, monto mensual o perfiles, HC comprometido, renovación automática, aviso de término y estado del contrato (`RF-36`, `§7.5`).
- **FR-040**: El sistema DEBE clasificar el contrato como `Vigente`, `Por vencer` o `Vencido`, alertar a 90, 60 y 30 días y dejar de sumar Backlog desde el mes siguiente al vencimiento sin cierre (`RF-38`, `RN-64`, `RN-65`, `RN-66`).
- **FR-041**: El sistema DEBE mostrar el Backlog contractual separado de la MAB y del Forecast, sin doble conteo (`RF-39`, `RN-63`).
- **FR-042**: El sistema DEBE mantener una meta única por sector y mes, en CLP y mayor o igual a cero; solo Operaciones puede crearla o modificarla y cada cambio DEBE auditarse con motivo (`RF-41`, `RF-44`, `RN-90`, `RN-91`).
- **FR-043**: El sistema DEBE calcular `Gap = Meta − Forecast` y `Cobertura = Forecast / Meta` cuando la meta sea mayor que cero; gap positivo es brecha y negativo es exceso (`RF-42`, `RF-43`, `§10.6`).
- **FR-044**: El sistema DEBE omitir el cálculo del gap cuando falta la meta del sector y mes, y activar `DQ-12` (`RN-92`, `DQ-12`).
- **FR-045**: El sistema DEBE aplicar un cambio de meta al mes editado y a los meses siguientes; un corte cerrado DEBE conservar la meta congelada (`RF-44`, `RN-93`).

#### Dashboard, consulta y reportes

- **FR-046**: El sistema DEBE mostrar los 11 datos críticos del OnePage y los indicadores de Backlog, Meta, Gap, calidad y pipeline (`RF-57`, `§13.1`, `§13.2`).
- **FR-047**: El sistema DEBE permitir abrir cada cifra hasta los registros que la componen y los componentes de cálculo (`RF-58`, `AC-15`).
- **FR-048**: El sistema DEBE ofrecer filtros combinables por período, sector, cliente, manager, owner, tipo, estado, flujo, modalidad, Studio, tecnología, tramos de probabilidad y confiabilidad, calidad y texto libre; los totales DEBEN ser la suma de los registros visibles (`RN-94`, `§13.3`).
- **FR-049**: El sistema DEBE listar próximos ingresos a 30, 60 y 90 días, contratos por vencer o vencidos y liberaciones de perfiles a 90 días (`§13.2`, `R-09`).
- **FR-050**: El sistema DEBE mostrar la distribución y el promedio de probabilidad, la distribución y el promedio ponderado por base de confiabilidad, y agregados por sector, cliente y responsable (`§13.1`, `RN-39`).
- **FR-051**: El sistema DEBE ofrecer al rol Ejecutivo una vista de solo lectura, incluida la exportación (`RN-04`, `§5.2`).
- **FR-052**: El sistema DEBE generar los reportes `R-01` a `R-13` definidos en `§13.4`.

#### Bitácora, auditoría y concurrencia

- **FR-053**: El sistema DEBE registrar entradas de bitácora con tipo de evento, contenido, autor, fecha/hora, próxima acción y fecha compromiso cuando exista (`RF-45`, `§7.7`).
- **FR-054**: El sistema DEBE generar un evento por campo auditado con valor anterior, valor nuevo, usuario, fecha/hora, origen (`UI`, `API`, `Carga`, `IA` o `Migración`; Principio III), fecha efectiva e impacto en MAB y Forecast; el motivo es obligatorio en cambios de estado, tipo, flujo, probabilidad, confiabilidad, cierre, reapertura, tarifa, HC, meta y horas (`RF-22`, `RF-47`, `RF-48`, `§9.9`).
- **FR-055**: El sistema DEBE impedir la edición y el borrado de bitácora y auditoría, no exponer esas acciones y rechazar la operación; no DEBE existir borrado físico de registros, perfiles, contratos, metas, cortes, bitácoras ni eventos (`RF-46`, `RN-78`, `RN-81`, `AC-09`).
- **FR-056**: El sistema DEBE registrar una corrección de bitácora como entrada nueva que referencia la anterior (`RN-79`).
- **FR-057**: El sistema DEBE permitir consultar la auditoría por registro, usuario, campo y fecha, y exportarla respetando permisos (`RF-49`, `RF-50`).
- **FR-058**: El sistema DEBE informar un conflicto de versión cuando dos usuarios editan el mismo registro y conservar la versión vigente sin perder lo escrito (`RF-02`, `RN-80`, `AC-13`).
- **FR-059**: El sistema DEBE conservar la auditoría al menos cinco años (`RNF-07`, `RNF-20`).
- **FR-060**: El sistema DEBE reabrir un registro cerrado o cancelado solo con motivo de Operaciones, dejando el evento correspondiente (`RN-20`).

#### Usuarios y permisos

- **FR-061**: El sistema DEBE distinguir tres roles: Líder, Operaciones y Ejecutivo (`§5.1`).
- **FR-062**: El sistema DEBE aplicar la matriz de permisos de `§5.2`: líder sobre sus registros, Operaciones sobre todos y la configuración, Ejecutivo de solo lectura (`RF-62`).
- **FR-063**: El sistema DEBE validar rol y propiedad en cada operación; una operación no autorizada DEBE rechazarse y no modificar datos (`RN-01`, `RF-06`).
- **FR-064**: El sistema DEBE impedir que un líder cambie su propio rol o el de otra persona (`RN-02`).
- **FR-065**: El sistema DEBE permitir a Operaciones mantener usuarios y roles, sin poder desactivar al último usuario de Operaciones (`RF-63`).
- **FR-066**: El sistema DEBE autenticar con correo y contraseña, sesión segura y bloqueo tras cinco intentos por cuenta e IP (`RF-61`, `RNF-05`).
- **FR-067**: El sistema DEBE limitar la lectura y exportación del líder a sus propios registros y permitir a Operaciones y Ejecutivo el acceso a todos, con edición solo para Operaciones (`§5.2`).

#### Calidad del dato

- **FR-068**: El sistema DEBE evaluar las reglas `DQ-01` a `DQ-13` con su severidad y responsable (`§9.7`).
- **FR-069**: El sistema DEBE asignar semáforo rojo si hay al menos una regla roja, amarillo si solo hay amarillas y verde si no hay hallazgos (`RN-67`).
- **FR-070**: El sistema DEBE listar los pendientes del líder solo sobre sus registros; Operaciones DEBE ver todos (`RN-68`).
- **FR-071**: El sistema DEBE tratar las reglas de calidad como una capa adicional; no reemplazan la validación de campos (`RN-69`).
- **FR-072**: El sistema DEBE mostrar el semáforo y los hallazgos en la ficha y en el dashboard, con alertas específicas para `DQ-06`, `DQ-07` y `DQ-08`.

#### Cierre de período y puente

- **FR-073**: El sistema DEBE ejecutar el cierre mensual por Operaciones y congelar, por registro y mes, la base, probabilidad, confiabilidad, MAB, Backlog y HC (`RF-55`, `RN-70`, `RN-71`).
- **FR-074**: El sistema DEBE impedir la modificación de un corte cerrado; una corrección DEBE generar una nueva versión del corte (`RN-72`).
- **FR-075**: El sistema DEBE descomponer la variación entre dos cortes en registros nuevos, cerrados, efecto base, probabilidad, confiabilidad, parámetros (incluidas las horas), Backlog y horizonte; la suma DEBE igualar la variación total, con línea de redondeo separada (`RF-56`, `RN-73`, `RN-74`).
- **FR-076**: El sistema DEBE permitir seguir editando el pipeline después del cierre; el siguiente corte DEBE reflejar los cambios (`RN-75`).
- **FR-077**: El sistema DEBE comparar dos cortes del mismo mes y presentar el puente por causa (`RF-56`, `R-12`).

#### Reportes y exportación

- **FR-078**: El sistema DEBE exportar a `.xlsx` toda vista y todo reporte, respetando filtros y permisos (`RF-59`, `§13.5`).
- **FR-079**: El sistema DEBE proteger las celdas exportadas contra inyección de fórmulas (`§13.5`).
- **FR-080**: El sistema DEBE incluir en la exportación de auditoría valor anterior, valor nuevo, usuario, fecha, motivo e impacto (`§13.5`).
- **FR-081**: El sistema DEBE impedir que un líder exporte datos de registros de otros owners (`§13.5`, `RN-04`).

#### IA y simulación

- **FR-082**: El sistema DEBERÍA ofrecer un asistente que sugiera ajustes cuando la bitácora contradiga los campos; si se ofrece, DEBE citar la evidencia, requerir aprobación humana y, al aceptarse, generar auditoría con origen `IA`, sin escribir por sí solo (`RF-64`, `D-17`).
- **FR-083**: El sistema DEBE clasificar toda salida asistida por IA como dato verificado, cálculo del sistema, estimación o datos insuficientes, con su fuente o la información faltante (`Principio VIII`).
- **FR-084**: El sistema DEBE funcionar sin el asistente; su ausencia o falla no DEBE bloquear registro, cálculo, cierre ni auditoría (`D-17`, prioridad 2).
- **FR-085**: El sistema PUEDE ofrecer un simulador de escenarios; si se ofrece, DEBE ejecutarse sobre una copia aislada, sin persistir, sin cambiar estados ni cortes y rotulando el resultado como simulado (`RF-35`, prioridad 2b).
- **FR-086**: El sistema NO DEBE enviar datos reales de clientes, tarifas o ingresos a un modelo externo sin autorización expresa y base de tratamiento definida (`RNF-15`).

#### Carga inicial y migración

- **FR-087**: El sistema DEBE importar la estructura de la plantilla con datos sintéticos o de prueba, sin cargar datos reales en el MVP, con validación y reporte de errores por fila (`RF-65`, `§16`).
- **FR-088**: El sistema DEBE normalizar tipo, estado, flujo, sector, manager, cliente, Studio y fechas; crear el perfil migrado y los ajustes; marcar las inconsistencias y recalcular los montos con el valor vigente de horas (180 h, `S-01`) (`RF-65`, `§16.2`).
- **FR-089**: El sistema DEBE ejecutar la importación de forma idempotente, sin duplicar registros (`RNF-19`).
- **FR-090**: El sistema DEBE preservar el valor de origen y no corregir en silencio fechas, estados, catálogos ni importes; toda diferencia DEBE informarse por fila (`§16.2`, `Principio I`).

### Non-Functional Requirements

- **NFR-001**: El dashboard DEBE responder en menos de 2 segundos p95 con 1.000 registros y 300 activos; las listas en menos de 1 segundo y las consultas en menos de 500 ms p95 (`RNF-03`).
- **NFR-002**: El diseño DEBE soportar 5.000 registros y 50 usuarios concurrentes sin cambios de arquitectura (`RNF-14`).
- **NFR-003**: El servicio DEBE tener 99,5 % de disponibilidad mensual en el período de demo, con RTO de 4 horas y RPO de 24 horas (`RNF-04`).
- **NFR-004**: La aplicación DEBE cumplir OWASP Top 10 y ASVS nivel 1; la autorización DEBE validarse en el sistema y no solo en la interfaz (`RNF-05`, `RNF-06`).
- **NFR-005**: La demo y las pruebas DEBEN usar datos sintéticos o seudonimizados; no DEBEN cargarse tarifas, clientes ni ingresos reales (`RNF-15`, `S-13`).
- **NFR-006**: La auditoría DEBE ser de solo inserción, conservarse cinco años y rechazar edición o borrado (`RNF-07`, `RNF-20`).
- **NFR-007**: La interfaz DEBE cumplir WCAG 2.1 AA, con `axe` mayor o igual a 90 y SUS mayor o igual a 70 con al menos cinco usuarios de los tres roles (`RNF-08`).
- **NFR-008**: La aplicación DEBE funcionar en Chrome y Edge de las últimas dos versiones y ser responsive desde 360 px (`RNF-09`).
- **NFR-009**: La interfaz y la documentación DEBEN estar en español de Chile, con fechas `dd-mm-aaaa`, montos CLP y porcentajes con coma decimal (`RNF-01`).
- **NFR-010**: Las fechas de negocio DEBEN ser fechas sin hora; los eventos DEBEN registrarse en UTC y mostrarse en America/Santiago (`RNF-02`, `RN-57`).
- **NFR-011**: El sistema DEBE registrar de forma estructurada los eventos, las métricas de uso y los errores, y alertar sobre disponibilidad y latencia (`RNF-11`).
- **NFR-012**: La información DEBE respaldarse a diario, retenerse 30 días y probar la restauración al menos una vez por trimestre (`RNF-12`).
- **NFR-013**: El dominio DEBE tener al menos 90 % de cobertura de pruebas; ningún cambio DEBE integrarse sin pruebas en verde y revisión de otra persona (`RNF-13`).
- **NFR-014**: Las escrituras DEBEN ser transaccionales; la importación DEBE ser idempotente y reportar errores por fila (`RNF-19`).
- **NFR-015**: El costo mensual estimado DEBE mantenerse entre USD 10 y USD 30, con presupuesto y alertas (`RNF-16`).
- **NFR-016**: DEBE existir README, contrato de interfaz, manual de usuario, registro de decisiones y guion de demo actualizados (`RNF-18`).
- **NFR-017**: El servicio DEBE desplegarse de forma reproducible en el entorno autorizado por NTT DATA (`RNF-17`).
- **NFR-018**: Los datos de negocio DEBEN conservarse mientras el registro esté activo y cinco años después; la auditoría, cinco años (`RNF-20`).

### Business Rules & State Transitions

#### Catálogos y coherencia

| Tipo | Estados permitidos | Flujos permitidos | Bolsa |
|---|---|---|---|
| **Oportunidad** | `Pendiente`, `StandBy`, `Cerrada`, `Cancelada` | 1–5 en `Pendiente` | MAB |
| **Demanda** | `Adjudicada`, `En Curso`, `StandBy`, `Cerrada`, `Cancelada` | 1–5 en `Adjudicada`; 6 en `Adjudicada` o `En Curso` | MAB |
| **Continuidad** | `En Curso`, `StandBy`, `Cerrada`, `Cancelada` | 6 | Backlog contractual |

**Estados:**

| Estado | Significado | Bolsa | Probabilidad |
|---|---|---|---|
| `Pendiente` | Oportunidad abierta, aún no adjudicada | MAB | Según flujo, 5–75 % |
| `Adjudicada` | Cliente adjudicó; perfiles no confirmados | MAB | 100 % fija |
| `En Curso` | Perfiles incorporados y servicio en ejecución | MAB con P=100; Backlog si es `Continuidad` | 100 % fija |
| `StandBy` | Detenida temporalmente | Excluida | Congelada |
| `Cerrada` | Fin del ciclo, con motivo | Según el motivo (FR-005) | Congelada |
| `Cancelada` | Cancelación formal, con motivo | Según el motivo (FR-005) | Congelada |

> **Precedencia de la bolsa:** la bolsa depende del `Tipo`; una `Continuidad` en `En Curso` pertenece al Backlog contractual, no a la MAB (`RN-83`). La tabla de `§8.2` se interpreta con esta precedencia (`H-07`).

**Flujos:**

| # | Flujo | Estados permitidos | Probabilidad sugerida |
|---:|---|---|---:|
| 1 | `Pendiente RFP` | `Pendiente` | 10 % |
| 2 | `Propuesta en curso` | `Pendiente` | 25 % |
| 3 | `Propuesta entregada` | `Pendiente`, `Adjudicada` | 50 % |
| 4 | `Pendiente candidatos` | `Pendiente`, `Adjudicada` | 50 % |
| 5 | `Validando candidatos` | `Pendiente`, `Adjudicada` | 75 % |
| 6 | `Perfiles seleccionados` | `Adjudicada`, `En Curso` | 100 % fija |

> En `Adjudicada` la probabilidad es 100 % (clarificación 2026-10-27); las sugerencias de los flujos 1–5 aplican a `Pendiente`.

#### Transiciones de estado

| Desde | Hacia | Quién | Condiciones | Efecto |
|---|---|---|---|---|
| Nueva oportunidad | `Pendiente` | Líder | Tipo `Oportunidad` | Flujo 1, P 10 %, C 90 % |
| Nueva demanda directa | `Adjudicada` | Líder | Motivo «Demanda directa», fecha y al menos un perfil | Flujo 3–5, P 100 % |
| Nueva continuidad | `En Curso` | Operaciones | Ficha de contrato | Flujo 6, P y C 100 % |
| `Pendiente` | `Adjudicada` | Líder | Fecha de adjudicación y al menos un perfil | Tipo `Demanda`, P 100 %, auditoría |
| `Adjudicada` | `En Curso` | Líder | Perfiles con fecha de ingreso | P 100 %, vista de Backlog confirmado |
| Cualquiera no terminal | `StandBy` | Líder u Operaciones | Motivo | Guarda estado previo, sale del cálculo |
| Cualquiera no terminal | `Cerrada` | Líder u Operaciones | Motivo y fecha | Según el motivo: `TERMINO_SERVICIO` prorratea hasta su fecha; el resto sale desde el mes de cierre (FR-005) |
| Cualquiera no terminal | `Cancelada` | Líder u Operaciones | Motivo y fecha | Prorratea hasta la fecha; con `DUPLICADO` sale desde el mes de cierre |
| `StandBy` | Estado previo | Líder u Operaciones | Motivo de reactivación | Restaura estado, P y C previos |
| `Cerrada` / `Cancelada` | `Pendiente` o `Adjudicada` | Operaciones | Motivo de reapertura | Vuelve al pipeline, auditoría |

**Transiciones inválidas:** `Pendiente → En Curso` sin pasar por `Adjudicada`; `Continuidad` en `Pendiente` o `Adjudicada`; `Perfiles seleccionados` en `Pendiente`; cierre o cancelación sin motivo; reapertura por un rol distinto de Operaciones (`RN-19`, `RN-20`, `RN-23`, `RN-26`, `RN-27`).

#### Reglas de cálculo e integridad

- **Una sola bolsa:** cada registro pertenece a Backlog contractual o MAB, nunca a ambas (`RN-83`).
- **Base:** `Base(r,m) = Σ_p [HC × dedicación × tarifa vigente × horas del mes × fracción activa]` (`§10.3`).
- **MAB:** `MAB(r,m) = Base(r,m) × P(r) × C(r)` (`§10.4`).
- **Backlog contractual:** `monto_mensual × fracción_activa_del_contrato`; si no hay monto, Base al 100 % (`RN-61`).
- **Forecast:** `Backlog contractual + MAB` (`§10.4`).
- **Ingreso potencial:** Base sin ponderar de la MAB más Backlog contractual (`§10.4`).
- **HC:** `Cierre(r,m) = Cierre(r,m−1) + Altas − Bajas`; nunca negativo (`RN-47`, `RN-48`).
- **Gap:** `Meta − Forecast`; **cobertura:** `Forecast / Meta` si `Meta > 0` (`§10.6`).
- **Redondeo:** CLP entero half-up al final de cada registro-mes; los totales suman valores redondeados (`RN-86` a `RN-88`).
- **Vigencia mensual:** probabilidad y confiabilidad se aplican por mes según su fecha efectiva; los meses anteriores conservan el valor que tenían (`RN-37`, `AC-04`).
- **Horas:** parámetro editable con vigencia mensual; 180 h es el valor inicial y cada mes usa el valor vigente; los cambios no reescriben meses anteriores y se auditan (`D-06`, `S-01`).
- **Referencia:** `C-01` a `C-08` son los resultados esperados del motor (`§10.9`).

#### Reglas de auditoría y concurrencia

- Todo cambio de estado, tipo, flujo, HC, perfil, tarifa, probabilidad, confiabilidad, fecha, contrato, meta, parámetro, usuario o permiso DEBE generar un evento por campo (`RN-76`).
- El motivo es obligatorio en cambios de estado, tipo, flujo, probabilidad, confiabilidad, cierre, reapertura, tarifa, HC, meta y horas (`RF-22`, `§9.9`).
- El evento DEBE guardar MAB y Forecast antes y después del cambio (`RN-77`).
- Bitácora y auditoría son de solo inserción; el sistema rechaza la edición o el borrado y no expone la acción en la interfaz (`RN-78`).
- Una corrección es una entrada nueva que referencia la anterior (`RN-79`).
- Toda edición viaja con la versión leída; un conflicto de versión se informa y se conserva la versión vigente (`RN-80`).
- No hay borrado físico (`RN-81`); el cierre es un cambio de estado con motivo (`RN-82`).
- La corrección de un corte genera una nueva versión; el corte anterior no se sobreescribe (`RN-72`).

#### Reglas de calidad del dato

| ID | Regla | Severidad | Responsable | Efecto |
|---|---|---|---|---|
| `DQ-01` | Campos obligatorios incompletos | Rojo | Líder | Bloquea el guardado |
| `DQ-02` | Sin actualización por más de 14 días | Amarillo | Líder | Aparece en pendientes |
| `DQ-03` | Ingreso a 30 días o menos sin `Perfiles seleccionados` | Rojo | Líder | Alerta en ficha y dashboard |
| `DQ-04` | Oportunidad sin próxima acción | Amarillo | Líder | Aparece en pendientes |
| `DQ-05` | Probabilidad fuera del rango del estado | Rojo | Líder | Bloquea el guardado |
| `DQ-06` | `Adjudicada` sin `En Staffing` | Amarillo | Líder | Alerta de staffing |
| `DQ-07` | `En Curso` sin `Invoicing` | Rojo | Operaciones | Alerta de facturación no planificada |
| `DQ-08` | `Continuidad` sin fin de contrato o sin monto | Rojo | Operaciones | Bloquea el cierre del registro |
| `DQ-09` | Perfil sin tarifa o tarifa no positiva | Rojo | Líder | Bloquea el guardado |
| `DQ-10` | Fechas de perfil fuera de la vigencia del registro | Rojo | Líder | Bloquea el guardado |
| `DQ-11` | Contrato con fin anterior al inicio | Rojo | Operaciones | Bloquea el guardado |
| `DQ-12` | Sector o mes sin meta | Amarillo | Operaciones | Alerta en el gap |
| `DQ-13` | Cliente o manager duplicado | Informativo | Operaciones | Sugerencia de fusión |

#### Matriz de permisos

| Acción | Líder | Operaciones | Ejecutivo |
|---|---|---|---|
| Crear registro | Sí | Sí | No |
| Editar registro, perfiles, fechas y estado | Solo propios | Todos | No |
| Escribir bitácora | Solo propios | Todos | Solo lectura |
| Cambiar tipo y flujo | Solo propios | Todos | No |
| Ajustar confiabilidad con motivo | No | Sí | No |
| Ajustar HC mensual con motivo | No | Sí | No |
| Mantener parámetros, catálogos y usuarios | No | Sí | No |
| Mantener metas comerciales | No | Sí | No |
| Mantener Backlog y contratos | Solo propios | Todos | Solo lectura |
| Cerrar período y comparar cortes | No | Sí | Solo lectura |
| Ver dashboard y reportes | Propios | Todos | Todos |
| Consultar auditoría | Propios | Todos | Solo lectura |
| Exportar | Propios | Todos | Todos |
| Eliminar | No; se cierra con motivo | No; se cierra con motivo | No |

#### Validaciones transversales

| Validación | Regla |
|---|---|
| Campos obligatorios | No se guarda si falta un obligatorio (`DQ-01`, `FR-004`). |
| Motivo | Obligatorio en estado, tipo, flujo, probabilidad, confiabilidad, cierre, reapertura, tarifa, HC, meta y horas (`RF-22`, `§9.9`). |
| Fechas | Creación no futura; adjudicación, cancelación y cierre posteriores a la creación; fin de vigencia posterior al ingreso (`RN-52` a `RN-54`). |
| Perfiles | HC entero 1–999; dedicación 1–100; fechas dentro de la vigencia; fin posterior al ingreso (`RI-03`, `RN-42`, `RN-55`). |
| Tarifas | Mayores que cero; sin superposición por perfil (`RI-04`, `RI-06`). |
| Contratos | Solo en `Continuidad`; exactamente uno; fin posterior al inicio (`RI-08`, `RI-09`). |
| Metas | Única por sector y mes; mayor o igual a cero (`RI-07`, `RN-90`). |
| Probabilidad y confiabilidad | Entre 0 y 1; probabilidad dentro del rango del estado (`RI-02`, `RN-10` a `RN-13`). |
| Versión | Toda edición exige la versión leída (`RN-80`). |
| Autorización | Rol y propiedad validados en el sistema (`RN-01`). |
| Borrado | No existe borrado físico (`RI-11`, `RN-81`). |

### Acceptance Criteria

| ID | Dado | Cuando | Entonces |
|---|---|---|---|
| `AC-01` | Un líder autenticado | Registra una oportunidad con dos perfiles, HC, tarifa y fechas | El sistema muestra Base, MAB y Forecast antes de guardar y registra el evento de creación |
| `AC-02` | Un registro `Pendiente` con 50 % | El líder lo pasa a `Adjudicada` con fecha | El tipo cambia a `Demanda`, la probabilidad pasa a 100 % y se audita |
| `AC-03` | Un registro `Adjudicada` con perfil activo | Pasa a `Perfiles seleccionados` | La probabilidad se fija en 100 %, la MAB se recalcula con confiabilidad y aparece en Backlog confirmado |
| `AC-04` | Un registro en MAB con confiabilidad 90 % | Operaciones la baja a 80 % con motivo y fecha efectiva | La MAB se recalcula, el evento guarda valores, motivo e impacto y los meses anteriores no cambian |
| `AC-05` | Un registro en MAB con P=100 | Se consulta el Forecast | Aparece una sola vez en la MAB y no se suma al Backlog contractual |
| `AC-06` | Un contrato de $45.000.000 mensuales | Operaciones lo registra con inicio y fin | El Backlog contractual del mes es $45.000.000, la MAB es 0 y aparece en vencimientos |
| `AC-07` | Una meta de $1.700.000.000 y un Forecast de $1.500.000.000 | Se consulta el dashboard | El gap es $200.000.000, la cobertura es 88,2 % y el semáforo es rojo |
| `AC-08` | Dos cortes consecutivos | Operaciones cierra el período | El puente descompone la variación por causa, la suma coincide y hay línea de redondeo |
| `AC-09` | Un evento de auditoría existente | Se intenta editar o borrar | La interfaz no ofrece la acción y el sistema rechaza la operación |
| `AC-10` | Un líder autenticado | Intenta editar un registro de otro líder | El sistema rechaza la operación y no modifica nada |
| `AC-11` | Un registro `En Curso` sin `Invoicing` | Se abre el panel de calidad | Aparece rojo por `DQ-07` con alerta de facturación no planificada |
| `AC-12` | Un registro de 2 HC con tarifa $2.600/h | Se calcula la Base mensual | El resultado es $936.000 y la ficha muestra la fórmula con 180 h (`S-01`) |
| `AC-13` | Un registro leído por dos usuarios | El segundo guarda después del primero | El sistema informa el conflicto, conserva lo escrito y muestra la versión vigente |
| `AC-14` | Un conjunto sintético con la estructura de la plantilla y cuatro registros de prueba | Se ejecuta la importación | Se crean cuatro registros sintéticos, se informan inconsistencias por fila y los montos se recalculan con 180 h (`S-01`) |
| `AC-15` | Un conjunto de datos sintéticos | Se abre el dashboard | Se muestran los 11 datos, Backlog, Meta y Gap, y cada cifra se abre hasta sus registros |
| `AC-16` | Un registro `Cancelada` con motivo `DUPLICADO` | Se consulta el Forecast del mes de cancelación | Sale desde el mes de cierre y no prorratea; con `CANCELADA_CLIENTE` o `TERMINO_SERVICIO` prorratea hasta la fecha |
| `AC-17` | Un registro con horas vigentes de 180 h | Operaciones cambia a 176 h con motivo y fecha efectiva | Los meses anteriores conservan su cálculo, el mes efectivo y siguientes usan 176 h y el puente muestra el efecto parámetros |

### Key Entities

- **Usuario**: persona que accede al sistema; tiene un rol, sectores asignados y estado activo. Se relaciona con los registros de los que es owner.
- **Registro**: raíz del pipeline; representa una oportunidad, demanda o continuidad. Contiene los datos comerciales, tipo, estado, flujo, probabilidad, confiabilidad, fechas, indicadores y observaciones. Se relaciona con perfiles, bitácora, auditoría, ajustes y, si es continuidad, con un contrato.
- **Perfil**: rol técnico requerido dentro de un registro; tiene nombre, HC, dedicación, fecha de ingreso y fecha de fin. Se relaciona con una o más tarifas.
- **Tarifa de perfil**: valor por hora en CLP con vigencia desde y hasta; no se superpone con otra tarifa del mismo perfil y no reescribe el pasado.
- **Vigencia de probabilidad y confiabilidad**: valor de P y C por registro con fecha efectiva y vigencia mensual; cada mes usa el valor vigente y un cambio no reescribe los meses anteriores.
- **Ajuste de HC**: corrección manual de altas o bajas en un mes, con cantidad, motivo y usuario de Operaciones; el cierre no se ajusta, se calcula.
- **Contrato**: ficha de una continuidad; código, inicio, fin o indefinido, monto mensual o perfiles, HC comprometido, renovación, aviso de término y estado calculado.
- **Bitácora**: entrada cronológica e inmutable con tipo, contenido, autor, fecha/hora, próxima acción y fecha compromiso; una corrección referencia la entrada anterior.
- **Evento de auditoría**: cambio trazable por campo con valor anterior, valor nuevo, usuario, fecha/hora, origen, fecha efectiva, motivo e impacto en MAB y Forecast.
- **Parámetro**: valor configurable con vigencia (horas mensuales, confiabilidad inicial, rangos, umbrales); su cambio se audita.
- **Catálogo**: valores normalizados de sector, cliente, manager, perfil, tecnología, práctica de Studio, motivo de cierre y otros; se desactivan, no se borran.
- **Meta comercial**: objetivo de ingreso por sector y mes, en CLP; única por sector y mes y auditada.
- **Corte**: fotografía mensual congelada de un período; contiene el detalle por registro y mes y es inmutable cuando está cerrado.
- **Detalle de corte**: valores congelados por registro y mes: base, probabilidad, confiabilidad, MAB, Backlog y HC; su suma debe coincidir con el Forecast.
- **Sugerencia de IA**: propuesta de ajuste con campo, valor sugerido, cita de bitácora, estado, revisor y versión del prompt; nunca se aplica sola.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los registros activos tiene owner, sector, cliente, tipo, estado, flujo, probabilidad y confiabilidad; si no tiene perfil, queda marcado como incompleto.
- **SC-002**: Un líder registra una oportunidad completa con dos perfiles en menos de 3 minutos.
- **SC-003**: El 100 % de los cambios en los datos auditados genera un evento con valor anterior, valor nuevo e impacto en MAB y Forecast.
- **SC-004**: En el 100 % de los meses y cortes, `Forecast = Backlog contractual + MAB` y ningún registro se cuenta dos veces.
- **SC-005**: El dashboard responde en menos de 2 segundos p95 con 1.000 registros y 300 activos; las listas en menos de 1 segundo.
- **SC-006**: El 100 % de los cortes cerrados reproduce las cifras congeladas y el puente suma la variación total, con diferencia de redondeo no mayor a 1 CLP por registro-mes.
- **SC-007**: El 100 % de los intentos de acceso o edición no autorizados se rechaza; cero fugas de datos entre owners en las pruebas de aceptación.
- **SC-008**: El 100 % de las sugerencias de IA cita su evidencia y requiere aprobación humana; cero escrituras autónomas de IA.
- **SC-009**: Cualquier cifra del dashboard se puede rastrear hasta sus registros y componentes en no más de tres interacciones.
- **SC-010**: El dominio alcanza al menos 90 % de cobertura de pruebas y el 100 % de las reglas críticas tiene al menos una prueba automatizada.
- **SC-011**: Al menos 90 % de los registros se actualiza en los últimos 14 días y al menos 95 % tiene los campos críticos completos en la carga inicial (`propuesta`, metas del MVP).
- **SC-012**: Cero registros con datos reales en la demo, la carga inicial y las pruebas; cero tarifas, clientes o ingresos reales en esos ambientes.
- **SC-013**: El cierre mensual se completa sin planillas externas y produce un corte reproducible y un puente explicable.

## Out of Scope

- ERP global de dotación o asignación individual de cada consultor a proyectos.
- Costos, márgenes y contabilidad; el MVP trabaja ingresos, HC y proyección comercial.
- Registro contable de facturación o integración transaccional con Invoicing.
- Integración transaccional con Staffing o Recruiting; solo se registra el indicador `En Staffing`.
- Reemplazo de la gestión de relaciones con clientes; si existe, se guarda un identificador externo para conciliar.
- Inicio de sesión único corporativo, notificaciones por correo o mensajería, tipo de cambio automático y analítica avanzada; se consideran etapa posterior.
- Gestión de nómina, evaluación de desempeño o banco de talentos.
- Multimoneda y consolidación en USD.
- Migración de datos reales en el MVP; la carga inicial se limita a la estructura de la plantilla con datos sintéticos.

## Assumptions

- El MVP sirve a Operaciones de NTT DATA GDN-e Chile y a los sectores de la operación actual; no es multiempresa ni multimoneda.
- La moneda es CLP y el horizonte es de 12 meses móviles, con vistas de 3, 6 y 12 (`D-07`).
- Las horas mensuales son un parámetro editable con vigencia mensual; el valor inicial es 180 h y su validación con el sponsor está abierta (`S-01`).
- El modelo de trabajo es un registro único que avanza de estado, sin recapturar datos al adjudicarse (`D-01`).
- El dashboard es en línea y el cierre es mensual; no hay cierre semanal obligatorio (`D-18`).
- La demo, las pruebas y la carga inicial del MVP usan datos sintéticos; los cuatro registros reales no se migran en el MVP y quedan para una etapa posterior con revisión de Operaciones (`S-11`).
- Operaciones dispondrá de los contratos, montos, fechas y metas por sector y mes (`S-05`, `S-06`).
- El catálogo histórico de clientes, managers y sectores se normaliza con alias y revisión de Operaciones (`S-04`, `S-10`).
- El asistente de IA y el simulador son prioridad 2 y 2b: agregan valor, pero el MVP debe funcionar sin ellos (`D-17`).
- Las decisiones de negocio `D-01` a `D-18` se tratan como vigentes; las que dependen de validación del sponsor se marcan con `S-xx`.
- La jerarquía documental es: constitución, `requerimientos.md` y sus anexos, esta especificación, plan y tareas.
- No existe código de aplicación en el repositorio; la especificación se basa en documentos y en la plantilla Excel.

## Open Decisions & Contradictions

Las decisiones de la tabla siguiente no se resuelven en esta especificación. El plan y la implementación NO DEBEN asumir un valor distinto al vigente sin una decisión registrada.

### Decisiones pendientes y de alcance

| ID | Tema | Estado | Dueño | Impacto en esta especificación |
|---|---|---|---|---|
| `S-01` | 180 h y recálculo de +10,43 % respecto de la planilla | Validar; 180 h inicial | PO / Sponsor | `FR-029`, `FR-036`, `FR-037`, `FR-038`, `AC-12`; comparación histórica |
| `S-02` | La sexta etapa es `Perfiles seleccionados` | Validar | PO / Sponsor | `FR-020`, `FR-025`, catálogo de flujo y regla del 100 % |
| `S-03` | «Cerrada» significa fin de ciclo, no «perdida» | Validar | Operaciones | `FR-005`, `FR-023`, reglas de calidad, migración de la fila 10 |
| `S-04` | Normalización de sectores, managers y clientes | Validar | Operaciones | `FR-006`, `FR-028`, migración y filtros |
| `S-05` | Operaciones dispone de contratos, montos y fechas | Validar | Operaciones | `FR-039` a `FR-041`, módulo Backlog |
| `S-06` | Operaciones entrega metas por sector y mes | Validar | Operaciones | `FR-042` a `FR-045`, Gap y cobertura |
| `S-10` | Catálogo histórico de 157 clientes | Pendiente | Operaciones | `FR-006`, `FR-028`, migración |
| `S-11` | Migración real de los cuatro registros, fuera del MVP | Fuera del MVP | PO | `FR-087` a `FR-090` (solo estructura sintética), `AC-14` |
| `S-12` | Entorno de despliegue autorizado | Pendiente | NTT DATA | `NFR-003`, `NFR-017`; no cambia el alcance funcional |
| `S-15` | Reestimación del plan por Backlog, Meta y Gap | Pendiente | PO / Equipo | Alcance y cronograma, no comportamiento funcional |

### Contradicciones resueltas

Las contradicciones `H-01` a `H-07` quedaron resueltas en las sesiones del 2026-10-27; no queda ninguna abierta con identificador `H`.

**Resueltas en la sesión 2026-10-27:** `H-01` (90 % vs `En Staffing`): se fija 100 % al adjudicar; `D-04` y `RN-30` quedan reemplazadas y la decisión requiere validación del sponsor y actualización de `requerimientos.md`. `H-02` (prorrateo de `Cancelada`): el motivo de cierre prevalece; `DUPLICADO` sale desde el mes de cierre y `CANCELADA_CLIENTE` y `TERMINO_SERVICIO` prorratean. `H-03` (motivos): se adopta la lista amplia de `RF-22` y `§9.9` (estado, tipo, flujo, probabilidad, confiabilidad, cierre, reapertura, tarifa, HC, meta y horas). `H-04` (horas): se permiten cambios con vigencia mensual; cada cambio exige motivo, usuario y fecha efectiva y el puente incluye el efecto horas. `H-05` (migración): se retira del MVP; la carga inicial usa solo datos sintéticos y los cuatro registros reales quedan para una etapa posterior con revisión de Operaciones. `H-06` (vigencia): probabilidad y confiabilidad se conservan con vigencia mensual y no reescriben meses anteriores. `H-07` (Backlog confirmado): es una vista de la MAB con P=100 y C aplicada, no una bolsa separada; la Continuidad va al Backlog contractual.

Estas resoluciones están incorporadas en `requerimientos.md` v1.1 (Anexo A, `A-21` a `A-27`, y §14). `H-01` reemplaza `D-04` y requiere validación expresa del sponsor.

## Traceability

| Historia / capacidad | Requisitos fuente | Reglas y criterios |
|---|---|---|
| US1 · Registro y mantenimiento | `RF-01` a `RF-10`, `§7.3`, `§7.9` | `AC-01`, `AC-12`, `RI-01` a `RI-11` |
| US2 · Ciclo de vida y probabilidad | `RF-19` a `RF-26`, `§9.1`, `§9.2`, `§9.3` | `AC-02`, `AC-03`, `AC-16` |
| US3 · Cálculo y detalle | `RF-27` a `RF-35`, `§10.1` a `§10.9` | `AC-04`, `AC-05`, `AC-12`, `AC-17` |
| US4 · Dashboard ejecutivo | `RF-57` a `RF-60`, `§13.1` a `§13.3` | `AC-15` |
| US5 · Backlog, metas y gap | `RF-36` a `RF-44`, `§9.6`, `§9.10`, `§10.6` | `AC-06`, `AC-07` |
| US6 · Cierre y puente | `RF-55`, `RF-56`, `§9.8`, `§10.7` | `AC-08` |
| US7 · Calidad del dato | `RF-53`, `RF-54`, `§9.7` | `AC-11` |
| US8 · Auditoría y permisos | `RF-45` a `RF-50`, `RF-61` a `RF-63`, `§5.2`, `§9.9` | `AC-09`, `AC-10`, `AC-13` |
| US9 · Reportes y exportación | `RF-59`, `RF-60`, `§13.4`, `§13.5` | `R-01` a `R-13`, `§13.5` |
| US10 · IA y simulación | `RF-35`, `RF-64`, `D-17` | `Principio VIII`, prioridad 2/2b |
| US11 · Carga inicial | `RF-65`, `§16.1` a `§16.4` | `AC-14` |

**Cobertura:** las 9 funcionalidades obligatorias del OnePage están cubiertas por US1, US2, US3, US4 y US8; el módulo Backlog/Meta/Gap por US5; el cierre y el puente por US6; la calidad del dato por US7; los reportes y la exportación por US9; la IA y la simulación por US10; la carga inicial por US11. Las reglas `RN-01` a `RN-94` se conservan en `requerimientos.md §9` y se citan en las secciones anteriores.
