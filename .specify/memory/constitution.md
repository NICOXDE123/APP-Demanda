# Constitución de Proyecta

Proyecta es la plataforma de gestión de oportunidades y demandas, seguimiento operacional y
proyecciones de negocio de Operaciones de NTT DATA GDN-e. Esta constitución fija los principios no
negociables que gobiernan su diseño, construcción y operación. Se apoya en `requerimientos.md`
v1.1 (2026-10-29), en sus anexos y en las decisiones D-01 a D-18; no los reemplaza ni resuelve por
sí sola las decisiones abiertas.

## Principios fundamentales

### I. Integridad de los datos (NO NEGOCIABLE)

- **Datos con origen.** Todo dato de negocio (cifras, fechas, HC, tarifas, probabilidad,
  confiabilidad, clientes, sectores, estados) DEBE provenir de una fuente identificable: ingreso
  humano autenticado, migración trazada o cálculo del motor. Un valor sin origen NO DEBE almacenarse
  como si fuera un hecho.
- **Prohibido inventar.** NO DEBE completarse un vacío con un valor plausible, interpolar cifras,
  fabricar registros de demostración sin declararlos como sintéticos ni «ajustar» un dato para que
  cuadre. Si falta información, se registra como faltante y se marca para revisión.
- **Valores por defecto.** Solo se permiten los definidos por una regla explícita del proyecto (por
  ejemplo, `No Aplica`, confiabilidad inicial o probabilidad sugerida por flujo). Todo valor por
  defecto DEBE ser visible, documentado y auditable; nunca sustituye un dato desconocido sin
  señalarlo.
- **Simulación aislada.** Toda simulación, escenario «¿y si…?», vista previa o cálculo hipotético
  DEBE ejecutarse sobre una copia aislada o en memoria, sin escribir en entidades de negocio, sin
  cambiar estados, sin alterar cortes cerrados, bitácora o auditoría, y sin persistir resultados.
  La salida DEBE rotularse como simulada y distinguirse de la referencia real.
- **Datos sintéticos.** Los datos de demo y prueba DEBEN ser sintéticos o seudonimizados y estar
  identificados como tales; NO DEBEN mezclarse con datos reales ni usarse para validar cifras de
  negocio.
- **Migración fiel.** La migración DEBE preservar el valor de origen, registrar la equivalencia
  aplicada y marcar la inconsistencia para revisión. NO DEBE corregir en silencio fechas, estados,
  catálogos ni importes.
- **Métricas sin fórmula.** NO DEBE implementarse ni mostrarse una métrica cuya fórmula no esté
  definida y sea reproducible; `Hot Mab` e `Ingreso Ponderado` quedan excluidas (D-12).

**Razón:** la promesa del producto es una fuente única confiable. El caso de la «plata mágica»
muestra el costo de una cifra que desaparece de la proyección y reaparece como facturación no
planificada.

### II. Reglas de negocio explícitas y cálculo determinista en el backend

- **Un solo motor.** Base, MAB, Backlog contractual, Backlog confirmado, Forecast, Ingreso
  potencial, HC proyectado, Gap, cobertura, tarifa media y puente DEBEN calcularse en un único
  módulo de dominio del backend. La interfaz, las plantillas, el dashboard, las exportaciones y
  cualquier consumidor NO DEBEN reimplementar ni corregir fórmulas.
- **Fórmulas publicadas.** Cada cálculo DEBE tener fórmula, variables, parámetros, regla de
  redondeo y casos de referencia documentados en `requerimientos.md` §10. Una fórmula nueva o
  modificada DEBE añadirse allí antes de implementarse.
- **Sin constantes ocultas.** Los valores que afectan cifras (horas mensuales, confiabilidad
  inicial, rangos de probabilidad, umbrales, aviso de término) DEBEN ser parámetros con vigencia y
  auditoría, no literales en el código. Las 163 h implícitas del Excel son el ejemplo de lo que NO
  DEBE repetirse.
- **Una sola bolsa.** Cada registro DEBE pertenecer exactamente a una bolsa por mes: Backlog
  contractual o MAB. `Backlog confirmado` es una vista de la MAB y NO DEBE sumarse por separado
  (D-09, RN-83).
- **Determinismo y reproducibilidad.** Dados los mismos datos, parámetros, fecha efectiva y versión
  de fórmula, el resultado DEBE ser idéntico. Un corte cerrado DEBE reproducir la cifra congelada.
- **Redondeo único.** Los montos se calculan en decimal y se redondean a CLP entero half-up al final
  de cada registro-mes; los totales suman valores ya redondeados (RN-86 a RN-88).
- **Error explícito.** Una entrada inválida, una división por cero, un rango de fechas imposible o
  un parámetro faltante DEBE producir un error explícito y trazable; NO DEBE devolver cero, nulo o
  una cifra aproximada como si fuera válida.

**Razón:** un cálculo defendible exige una sola implementación auditable. Si la fórmula vive en la
vista, en el Excel de exportación y en el motor, tarde o temprano difieren.

### III. Trazabilidad y auditoría

- **Evento por cambio relevante.** Todo cambio en los datos auditados del proyecto (estado, tipo,
  flujo, HC, perfiles, tarifa, probabilidad, confiabilidad, fechas, contrato, meta, parámetros,
  usuarios y permisos) DEBE generar un evento con usuario, fecha/hora UTC, valor anterior, valor
  nuevo, origen (`UI`, `API`, `Carga`, `IA`, `Migración`), fecha efectiva, motivo cuando la regla lo
  exija e impacto en MAB y Forecast.
- **Solo inserción.** Bitácora y auditoría DEBEN ser de solo inserción. La interfaz y la API NO
  DEBEN exponer edición ni borrado; una corrección DEBE ser un evento nuevo que referencia al
  anterior. La API DEBE responder `405` a `PUT` y `DELETE` sobre estos recursos (RN-78).
- **Estados.** Toda transición DEBE registrar estado anterior y nuevo, usuario, fecha efectiva y
  motivo cuando corresponda (RN-21). `StandBy` DEBE conservar el estado previo para restaurarlo
  (RN-26).
- **Cortes.** Un corte cerrado DEBE ser inmutable; una corrección DEBE generar una nueva versión
  del corte, nunca sobreescribirlo (RN-72).
- **Sin borrado físico.** Ningún registro, perfil, contrato, meta, corte, entrada de bitácora ni
  evento DEBE borrarse físicamente; el cierre es un cambio de estado con motivo (RN-81, RN-82).
- **Lectura gobernada.** El acceso a la auditoría DEBE respetar rol y propiedad; ni Operaciones
  puede modificar el historial (RN-03).
- **Retención.** La auditoría DEBE conservarse al menos cinco años (RNF-07, RNF-20).

**Razón:** sin historial no se puede explicar una variación del Forecast ni defender una cifra ante
el sponsor; la auditoría es parte del producto, no un extra.

### IV. Separación de responsabilidades

- **Cuatro capas.** Presentación, aplicación/API, dominio y persistencia DEBEN estar separadas; las
  integraciones (IA, exportación, servicios externos) DEBEN aislarse detrás de interfaces.
- **Dominio puro.** El dominio NO DEBE depender de HTTP, plantillas, framework web, ORM,
  almacenamiento ni SDK de IA. El motor DEBE poder probarse sin base de datos ni red.
- **Persistencia aislada.** El acceso a datos DEBE pasar por repositorios; cambiar
  Firestore/Datastore por otra base NO DEBE exigir reescribir reglas de negocio (Anexo C.4).
- **Autorización en servidor.** La autorización DEBE resolverse en la capa de aplicación/servidor;
  ocultar un botón o una ruta en la interfaz NO ES control de acceso (RN-01).
- **Una sola fuente de cálculo.** El mismo caso de uso DEBE invocar el mismo servicio de dominio
  para API, dashboard, reportes, exportación y simulador.
- **Sin lógica duplicada.** Las validaciones de negocio DEBEN vivir en el dominio y reutilizarse; la
  validación de presentación es complementaria, no sustituta.
- **Monolito modular.** Se prefiere un único despliegue con módulos separados; separar un servicio
  exige justificación de escala u operación, no preferencia estilística.
- **Contratos.** La API DEBE publicar OpenAPI 3 versionado en `/api/v1`; los cambios incompatibles
  DEBEN versionarse o anunciarse (RNF-10).

**Razón:** el proyecto debe poder cambiar de base de datos, de interfaz o de proveedor de IA sin
reescribir las reglas que producen las cifras.

### V. Calidad verificable

- **Validación de entrada.** Toda entrada DEBE validarse en el servidor (tipo, rango,
  obligatoriedad, coherencia entre fechas, catálogo, permisos) antes de persistir; los errores DEBEN
  ser explícitos, en español y con código estable.
- **Pruebas de reglas críticas.** Las reglas de cálculo, transición de estados, permisos, auditoría,
  no doble conteo, redondeo y migración DEBEN tener pruebas automatizadas. Los casos de referencia
  C-01 a C-08 son obligatorios y DEBEN fallar si la fórmula cambia sin actualizar la especificación.
- **Cobertura.** El dominio DEBE tener al menos 90 % de cobertura (RNF-13); la cobertura no
  sustituye casos de negocio bien elegidos.
- **Regresión primero.** Un defecto en una fórmula o regla DEBE reproducirse con una prueba que
  falle antes de corregirse.
- **Contratos y extremo a extremo.** La API DEBE tener pruebas de contrato; los flujos críticos
  (alta, adjudicación, cierre, cierre de período, exportación) DEBEN tener al menos una prueba E2E.
- **Errores esperados.** `403`, `404`, `405`, `409` y `422` DEBEN probarse por rol y por estado, no
  solo el camino feliz.
- **Calidad de interfaz.** La interfaz DEBE cumplir WCAG 2.1 AA, `axe` ≥ 90 y SUS ≥ 70 (RNF-08); la
  accesibilidad es parte de la definición de terminado.
- **CI y revisión.** Ningún cambio DEBE integrarse con pipeline rojo o sin revisión de otra persona
  (RNF-13).

**Razón:** las reglas de negocio son el activo principal. Una prueba que no reproduce un caso real
no protege la cifra que el sponsor va a usar.

### VI. Consistencia documental y trazabilidad de extremo a extremo

- **Fuente normativa.** `requerimientos.md` (v1.0 y sus enmiendas) es la fuente de requisitos; el
  Anexo A es el registro canónico de discrepancias resueltas y el §14 el de decisiones abiertas.
  Esta constitución no los reemplaza.
- **Cadena trazable.** Todo requisito (`RF-xx`, `RN-xx`, `RNF-xx`) DEBE poder seguirse hasta su
  especificación, plan, tarea y prueba; toda tarea DEBE declarar el requisito que sirve y todo
  criterio `AC-xx` DEBE tener prueba.
- **Identificadores estables.** Los identificadores no se renumeran; un requisito retirado se marca
  como superado y conserva su historia.
- **Cambio de regla.** Cambiar una regla de negocio exige actualizar, en el mismo cambio:
  `requerimientos.md` (versión e historial), los casos de referencia afectados, las
  especificaciones, las tareas y las pruebas.
- **Documentación mínima.** README, contrato OpenAPI, manual de usuario, ADR de decisiones y guion
  de demo DEBEN existir y estar actualizados (RNF-18).
- **Idioma y formato.** La documentación y la interfaz DEBEN estar en español de Chile; fechas
  `dd-mm-aaaa` en la interfaz, `YYYY-MM-DD` en documentos técnicos, meses `YYYY-MM`, montos CLP
  (RNF-01).
- **Sin decisiones huérfanas.** Una decisión que no esté en `requerimientos.md` o en un ADR NO
  EXISTE para efectos de implementación.

**Razón:** el proyecto se evalúa por la coherencia entre lo que promete, lo que diseña y lo que
prueba; un requisito sin prueba o una prueba sin requisito rompe esa cadena.

### VII. Cambios mínimos y respeto de las decisiones existentes

- **Inspeccionar antes de cambiar.** Antes de proponer o aplicar un cambio, se DEBE leer el código,
  los documentos y las decisiones vigentes del área afectada.
- **No reemplazar sin justificación.** Un componente funcional, esquema, catálogo, plantilla, script
  o decisión arquitectónica NO DEBE reemplazarse sin justificación escrita, análisis de alternativas
  y aprobación del PO; si afecta la estructura, también de arquitectura.
- **Decisiones vigentes.** D-01 a D-18 y los catálogos normalizados son vinculantes mientras no se
  enmienden; el desacuerdo se tramita como enmienda, no como excepción silenciosa.
- **Cambio quirúrgico.** Se prefieren cambios pequeños y reversibles; un refactor DEBE preservar
  comportamiento y estar cubierto por pruebas. No se mezcla refactor estructural con cambio
  funcional en el mismo cambio.
- **Dependencias.** Una dependencia, framework o servicio nuevo DEBE justificarse por necesidad,
  costo y mantenimiento; la arquitectura del Anexo C es referencia, no imposición, pero el cambio
  de stack requiere ADR.
- **Compatibilidad.** Los datos y contratos existentes DEBEN migrarse o mantenerse compatibles;
  romper un contrato exige versión y plan de transición.
- **Alto.** Si el cambio necesario contradice un principio, se DEBE detener la implementación y
  escalar; no se implementa una excepción local.

**Razón:** el mayor riesgo del proyecto no es escribir poco, sino reescribir lo que ya funciona y
perder las decisiones que costó acordar con el sponsor.

### VIII. Transparencia de la información asistida por IA

- **Cuatro etiquetas.** Toda salida de una funcionalidad asistida por IA DEBE clasificarse
  explícitamente como **dato verificado** (con fuente y fecha), **cálculo del sistema** (con fórmula
  y parámetros), **estimación** (con supuestos, método y rango de incertidumbre) o **datos
  insuficientes** (indicando qué falta). NO se permite presentar una estimación como hecho.
- **La IA no escribe.** La IA NO DEBE crear, modificar, cerrar, borrar ni cambiar el estado de datos
  de negocio, ni alterar cortes o auditoría. Sus sugerencias DEBEN requerir aprobación humana
  explícita y, al aceptarse, generar un evento de auditoría con origen `IA` (D-17).
- **Cita obligatoria.** Toda sugerencia DEBE citar la evidencia que la sustenta (entrada de
  bitácora, campo, documento) y la versión del prompt o del modelo utilizado.
- **Sin datos reales sin autorización.** NO DEBE enviarse información real de clientes, tarifas o
  ingresos a un modelo externo sin autorización expresa y base de tratamiento definida (RNF-15).
- **Distinción visible.** La interfaz DEBE distinguir visualmente una sugerencia de IA de un cálculo
  determinista del sistema y de un dato ingresado por una persona.
- **No bloqueante.** La ausencia o falla de la IA NO DEBE impedir registrar, calcular, cerrar o
  auditar; el MVP DEBE funcionar sin ella (D-17, prioridad 2).
- **Sin confianza fabricada.** La IA NO DEBE inventar cifras, fuentes, citas ni grados de certeza;
  si no hay evidencia, la salida correcta es «datos insuficientes».

**Razón:** una sugerencia sin procedencia es indistinguible de una cifra inventada. La etiqueta de
origen es lo que permite al comité decidir si confía en el dato.

### IX. Seguridad y protección de datos

- **Autenticación.** Contraseñas con Argon2; sesión en cookie `HttpOnly`, `Secure` y
  `SameSite=Strict`; CSRF en formularios y HTMX; bloqueo tras cinco intentos por cuenta e IP
  (RNF-05).
- **Autorización.** Roles y propiedad DEBEN validarse en el servidor; una petición no autorizada
  DEBE responder `403`; el rol Ejecutivo es de solo lectura, incluida la exportación (RN-04,
  RNF-06).
- **Mínimo privilegio.** Usuarios, cuentas de servicio y accesos a GCP DEBEN tener el mínimo
  privilegio necesario; los secretos DEBEN vivir en Secret Manager y NUNCA en el repositorio ni en
  logs.
- **Protección de datos.** Consultas y DTO DEBEN limitar los datos al propósito; no se registran
  datos personales ni tarifas en logs; la exportación DEBE respetar filtros y permisos y protegerse
  contra inyección de fórmulas.
- **Datos de demo.** La demo y las pruebas DEBEN usar datos sintéticos o seudonimizados; NO DEBEN
  cargarse tarifas, clientes ni ingresos reales (RNF-15).
- **Respaldo y retención.** Respaldo diario con 30 días de retención y restauración probada al menos
  una vez por trimestre; retención de datos de negocio y auditoría según RNF-20.
- **Estándares.** La aplicación DEBE cumplir OWASP Top 10 y ASVS nivel 1; las dependencias DEBEN
  escanearse y las vulnerabilidades críticas corregirse antes de la entrega.

**Razón:** los datos del pipeline son información comercial sensible; una fuga o un permiso mal
validado destruye la confianza que justifica reemplazar el Excel.

## Restricciones adicionales

Las siguientes restricciones son vinculantes para el MVP. No reemplazan los requisitos detallados de
`requerimientos.md`; los acotan y evitan que una decisión local los contradiga.

### Dominio y datos

- **Moneda y horizonte.** CLP único, sin multimoneda ni tasa de cambio; horizonte de 12 meses
  móviles con vistas de 3, 6 y 12 (D-07, RN-89).
- **Horas mensuales.** Es un parámetro con vigencia. El valor vigente es 180 h (D-06) y su
  validación con el sponsor sigue abierta (S-01); no se fija en el código ni se cambia por
  conveniencia.
- **Unidad temporal.** Un mes se identifica `YYYY-MM`; las fechas de negocio son `DATE` sin hora;
  los eventos son `TIMESTAMP` UTC y se muestran en America/Santiago (RN-57, RN-58).
- **Porcentajes.** Se representan como decimal 0,00–1,00 en el dominio y se muestran 0 %–100 %;
  la persistencia puede guardarlos como entero en puntos base (0–10.000) sin pérdida de precisión.
- **Modelo.** `Registro` es la raíz; `Tipo`, `Estado` y `Flujo` son campos distintos y coherentes
  entre sí; los catálogos se normalizan con alias y no se borran, se desactivan (D-01, D-14).
- **Integridad.** Una sola bolsa por registro y mes; `Forecast = Backlog contractual + MAB`;
  `Backlog confirmado` es una vista de la MAB; sin doble conteo (D-09, RN-83).
- **Sin borrado.** No hay borrado físico; el cierre es un cambio de estado con motivo; toda edición
  viaja con versión y responde `409` si hay conflicto (RN-80 a RN-82).
- **Métricas retiradas.** `Hot Mab` e `Ingreso Ponderado` no se implementan (D-12).

### Plataforma y arquitectura

- **Estilo.** Monolito modular con capas separadas; la arquitectura del Anexo C es una referencia y
  NTT DATA puede fijar otra si el proyecto GCP lo exige, con ADR y sin cambiar los requisitos.
- **API.** REST versionada en `/api/v1`, contrato OpenAPI 3, respuestas JSON (RNF-10).
- **Persistencia.** Firestore en modo Datastore como referencia, con transacciones y emulador
  local; los repositorios aíslan el cambio a Cloud SQL si se requiere (Anexo C.4).
- **Despliegue.** Cloud Run en GCP, entornos `dev` y `demo`, HTTPS, escala a cero; secretos en
  Secret Manager; observabilidad con Cloud Logging y métricas (RNF-11, RNF-17).
- **Interfaz.** Jinja2 + HTMX + Bootstrap + Chart.js como referencia; español de Chile; WCAG 2.1
  AA; Chrome y Edge de las últimas dos versiones; responsive desde 360 px (RNF-01, RNF-08, RNF-09).
- **Rendimiento.** Dashboard < 2 s p95 con 1.000 registros y 300 activos; listas < 1 s; API < 500
  ms p95; el diseño soporta 5.000 registros y 50 usuarios concurrentes (RNF-03, RNF-14).
- **Costo.** Entre USD 10 y USD 30 mensuales con alertas de presupuesto (RNF-16).

### Datos sensibles y entornos

- **Demo sintética.** La demo y las pruebas usan datos sintéticos o seudonimizados; no se cargan
  tarifas, clientes ni ingresos reales (RNF-15, S-13).
- **Migración real.** Queda fuera del MVP (S-11, H-05). En una etapa posterior se ejecutará con
  revisión de Operaciones, preservando el origen y marcando inconsistencias, en un entorno
  autorizado y separado de la demo.
- **Exportación.** Toda exportación respeta filtros y permisos, no expone datos de otros owners y
  protege las celdas contra inyección de fórmulas (§13.5).
- **Secretos y logs.** Sin secretos, credenciales ni datos personales en el repositorio o en logs.

### Fuera de alcance del MVP

No forman parte del MVP y no DEBEN introducirse sin enmienda y reestimación (S-15): ERP global de
dotación o asignación individual; costos, márgenes y contabilidad; integración transaccional con
Invoicing o Staffing; reemplazo de CRM; SSO corporativo, notificaciones por correo o Teams, tipo de
cambio automático, API para Staffing y BigQuery; nómina, evaluación de desempeño o banco de
talentos; multimoneda y consolidación en USD (§4.2).

## Flujo de desarrollo y puertas de calidad

### Ciclo de especificación

1. `/speckit.specify` produce la especificación de la funcionalidad con criterios de aceptación.
2. `/speckit.clarify` resuelve ambigüedades antes de diseñar; una decisión abierta del proyecto se
   escala a su dueño, no se responde por suposición.
3. `/speckit.plan` produce el plan técnico y ejecuta la puerta constitucional.
4. `/speckit.tasks` descompone el plan en tareas trazables a requisitos.
5. `/speckit.implement` ejecuta las tareas con pruebas y evidencia.

- NO se implementa código sin especificación y plan aprobados.
- La especificación NO DEBE contradecir `requerimientos.md`; si lo hace, se corrige el requisito o
  se enmienda la constitución, no el código.
- Cada entrega se compone de cortes verticales pequeños que dejan el sistema funcionando y probado.

### Puerta constitucional (Constitution Check)

- Todo `plan.md` DEBE incluir una tabla `Principio | Estado (PASS/FAIL) | Evidencia | Excepción`
  para los nueve principios.
- Un `FAIL` bloquea el paso a diseño. La excepción se registra en `Complexity Tracking` con
  necesidad, alternativa descartada, riesgo, responsable y fecha de revisión; requiere aprobación
  del PO.
- La puerta se re-evalúa después del diseño; una violación nueva se trata igual.
- La evidencia DEBE ser verificable: referencia a prueba, documento, decisión o cambio, no una
  afirmación.

### Definición de terminado

Un incremento está terminado solo si:

1. Los criterios `AC-xx` afectados tienen pruebas automatizadas en verde.
2. Las reglas de cálculo, transiciones, permisos, auditoría y no doble conteo están cubiertas.
3. Los errores `403`, `405`, `409` y `422` están probados por rol y por estado.
4. Los cálculos usan el motor único; no hay fórmulas ni parámetros embebidos en el código.
5. Los eventos de auditoría incluyen valor anterior, nuevo, usuario, fecha, origen e impacto cuando
   aplique.
6. La documentación afectada (requisitos, OpenAPI, ADR, pruebas) está actualizada.
7. No hay secretos ni datos reales en el repositorio, los seeds ni los logs.
8. La interfaz cumple accesibilidad y rendimiento, o la excepción está registrada.
9. El cambio fue revisado por otra persona y el pipeline está en verde.

### Pruebas obligatorias

- Casos de referencia C-01 a C-08 como regresión del motor.
- Transiciones válidas e inválidas del ciclo de vida (§9.1).
- `Forecast = Backlog contractual + MAB` sin doble conteo; `Backlog confirmado` no se suma aparte.
- Redondeo half-up y totales que suman valores redondeados.
- Auditoría inmutable (`405`), permisos (`403`) y concurrencia optimista (`409`).
- Migración idempotente con reporte de errores por fila (RNF-19).
- Contrato OpenAPI y al menos un E2E por flujo crítico.
- IA: no escritura, cita obligatoria, aprobación humana y evaluación con al menos 40 casos.
- Simulador: no persiste, no cambia estados y rotula el resultado como simulado.

### Revisión, evidencia y defectos

- Cada cambio DEBE ser revisado por otra persona y dejar evidencia en la tarea o el PR.
- Un defecto de fórmula o regla se reproduce con una prueba que falla antes de corregirse; si el
  caso no existía, se agrega a los casos de referencia.
- Un cambio de regla sigue el orden: requisito actualizado, caso de referencia, prueba, código.
- NO se acepta un cambio que silencie una validación, omita auditoría o amplíe permisos para
  cumplir una fecha.

## Gobierno

### Supremacía y jerarquía

Esta constitución prevalece sobre especificaciones, planes, tareas y código. En caso de conflicto,
el orden es:

1. Esta constitución (principios y restricciones).
2. `requerimientos.md` y sus anexos (requisitos y decisiones del proyecto).
3. La especificación de la funcionalidad (`spec.md`).
4. El plan, las tareas y el código.

- Las reglas de negocio y el alcance pertenecen al sponsor y a Operaciones; la interpretación
  técnica pertenece al PO y a arquitectura. Ninguna de las dos puede modificar las decisiones de la
  otra por conveniencia.
- Un conflicto no se resuelve en el código: se detiene el trabajo y se escala.
- Esta constitución no sustituye `requerimientos.md`; lo obliga a ser explícito y verificable.

### Procedimiento de enmienda

1. Propuesta escrita con: principio o sección afectada, motivación, impacto en requisitos,
   especificaciones, pruebas y datos, y tipo de cambio (MAJOR, MINOR o PATCH).
2. Revisión del PO y de arquitectura; seguridad para el principio IX; sponsor cuando cambie
   alcance, reglas de negocio o supuestos abiertos.
3. Aprobación registrada en el historial de este documento.
4. Actualización de la línea de versión, el historial y los documentos dependientes en el mismo
   cambio.
5. Comunicación al equipo; las especificaciones abiertas se revisan contra la nueva versión.

- Una enmienda NO DEBE modificar las plantillas de `.specify/templates/`; solo este documento y los
  artefactos del proyecto.
- Una corrección de redacción que no cambie el significado es PATCH y no requiere revisión de
  arquitectura.
- No hay enmiendas implícitas: un cambio de práctica que no esté aquí es una propuesta pendiente.

### Política de versionado

- **MAJOR:** se elimina o redefine un principio, o se cambia una regla no negociable que invalida
  especificaciones o planes existentes (por ejemplo, moneda, bolsa única o auditoría inmutable).
- **MINOR:** se agrega un principio o una sección, o se amplía materialmente una guía existente.
- **PATCH:** aclaraciones, correcciones de redacción o referencias, sin cambio semántico.

La versión se expresa `MAJOR.MINOR.PATCH` y se actualiza junto con `Ratified` y `Last Amended` en
formato `YYYY-MM-DD`.

### Cumplimiento y excepciones

- La puerta constitucional se aplica en cada `plan.md`; la revisión de cumplimiento, en cada cambio
  y en cada entrega (E1, E2, E3).
- El PO mantiene el registro de excepciones; arquitectura revisa la separación de capas; seguridad
  revisa el principio IX; QA revisa las pruebas y la trazabilidad.
- Un incumplimiento sin excepción aprobada es un defecto bloqueante, no una deuda técnica.
- Las excepciones son temporales y tienen fecha de revisión; si se repiten, se convierten en
  enmienda o se eliminan.
- Indicadores mínimos: cobertura del dominio ≥ 90 %, pipeline en verde y cero hallazgos críticos de
  permisos o auditoría abiertos al cierre de cada entrega.

### Decisiones abiertas y discrepancias

- El registro canónico de decisiones abiertas es `requerimientos.md` §14 (`S-xx`); el de
  discrepancias resueltas es el Anexo A (`A-xx`). Esta constitución no los resuelve.
- Ninguna especificación, plan, tarea o código DEBE asumir un valor para una decisión abierta. Si
  bloquea el trabajo, la funcionalidad queda en `NEEDS CLARIFICATION` y se escala a su dueño.
- Las decisiones abiertas que condicionan la arquitectura son: `S-01` (180 h y recálculo), `S-02`
  (sexta etapa), `S-03` (semántica de Cerrada), `S-04` (normalización de catálogos), `S-05`
  (contratos), `S-06` (metas), `S-10` (clientes), `S-12` (GCP) y `S-15` (plan). `S-11` quedó
  decidida: sin migración real en el MVP (H-05).
- Los hallazgos `H-01` a `H-07` de la revisión inicial quedaron resueltos en la sesión del
  2026-10-27 y registrados en el Anexo A de `requerimientos.md` v1.1 (`A-21` a `A-27`). `H-01`
  reemplaza `D-04` y requiere validación expresa del sponsor.
- Toda nueva discrepancia se registra en el Anexo A con su resolución y estado; una decisión que
  solo vive en el código o en una conversación no existe.

### Historial de ratificación y enmiendas

| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-27 | Alfredo San Juan (PO) | Adopción inicial: nueve principios, restricciones adicionales y flujo de desarrollo |
| 1.0.1 | 2026-10-29 | Matías Mcintire | PATCH: retira el Sync Impact Report temporal tras registrar H-01 a H-07 en el Anexo A; referencia a `requerimientos.md` v1.1; `S-11` pasa a decidida; aclara que los porcentajes se representan como decimal en el dominio y pueden persistirse como enteros en puntos base |

Esta constitución rige desde su ratificación por el PO (2026-10-27). La validación del sponsor sobre
los requisitos es un acto separado (Anexo D de `requerimientos.md`) y no condiciona la vigencia de
los principios técnicos, pero sí el cierre de las decisiones `S-xx`.

**Version**: 1.0.1 | **Ratified**: 2026-10-27 | **Last Amended**: 2026-10-29
