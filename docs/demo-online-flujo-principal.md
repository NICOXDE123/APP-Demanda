# Demo online de Proyecta · flujo principal

**Preparado para:** reunión con Jorge del 20/11/2026.  
**Duración:** 15–20 minutos; versión abreviada de 7 minutos al final.  
**Objetivo:** mostrar cómo una oportunidad con personas y tarifas se convierte en demanda, cambia la proyección y deja trazabilidad.  
**Pauta de decisiones:** [Preguntas y reglas para Jorge](reunion-jorge-2026-11-20.md).

> Guion basado en el código local revisado. La URL de E2 sigue como `<<COMPLETAR AL DESPLEGAR>>`; no se verificó un servicio online ni que su versión coincida con esta copia. Completar el acceso y ensayar este recorrido antes de la reunión.

## 1. Preparación del acceso online

Completar esta ficha fuera de la presentación. La contraseña se consulta por el canal privado del equipo; no se escribe en este archivo.

| Dato | Completar antes de presentar |
|---|---|
| URL HTTPS de la demo | ____________________ |
| Responsable de la instancia | ____________________ |
| Rama / commit efectivamente desplegado | ____________________ |
| Último ensayo completo y resultado | ____________________ |
| Persona que presenta / persona que toma acuerdos | ____________________ |
| Código OPD creado durante la demo | ____________________ |

### 30 minutos antes

1. Abrir la URL publicada y verificar `URL/health`: debe devolver `{"status":"ok"}`. Esto verifica disponibilidad, no el flujo completo.
2. Abrir `URL/login` y entrar con las cuentas necesarias. Si el hosting temporal se suspendió, esperar su arranque antes de comenzar; E2 documenta que la primera carga puede demorar cerca de un minuto.
3. Confirmar que está desplegada la versión ensayada y que los datos son sintéticos. La aplicación arranca normalmente con 60 registros; lo creado después depende de la sesión del servidor.
4. Revisar en **Parámetros MAB** que estén vigentes **180 h** y **90 % de confiabilidad inicial**, y que no haya cambios futuros que alteren el caso. Si hay valores diferentes, adaptar y recalcular el ejemplo antes de presentarlo.
5. Ensayar el alta, un cambio de flujo y una adjudicación con un registro distinto, llamado `ENSAYO DEMO`. Reservar `DEMO JORGE 20-11` para la presentación. No asumir un número OPD fijo.
6. Preparar sesiones independientes: un perfil de navegador para Operaciones, otro para Líder 1 y otro para Ejecutivo. Dos pestañas del mismo perfil comparten la sesión. También puede usarse cierre de sesión entre roles.
7. Preparar capturas de respaldo del dashboard, la ficha, el cálculo y la auditoría. Una captura demuestra un resultado previamente obtenido; no sustituye una prueba en vivo.

### Justo antes de compartir pantalla

- Compartir la ventana de la aplicación y comprobar que los textos y cifras se lean en la videollamada.
- Mantener un único presentador editando; otra persona registra respuestas de Jorge.
- Mantener activa la sesión: expira tras 30 minutos sin actividad.
- Dejar preparada la [pauta de preguntas](reunion-jorge-2026-11-20.md), especialmente horas, P al adjudicar, Invoicing y gap.

### Si todavía no existe URL pública

Para la reunión se puede ejecutar la aplicación localmente y compartir su ventana por la videollamada. Los asistentes verán la demo, pero `127.0.0.1` solo abre en el computador del presentador. No presentarlo como acceso remoto para Jorge.

Desde la raíz del repositorio, con el entorno ya instalado:

```powershell
.\.venv\Scripts\python.exe -m uvicorn proyecta.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000`. Para una instalación nueva con Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m uvicorn proyecta.main:app --host 127.0.0.1 --port 8000
```

Si Jorge necesita entrar desde su propio equipo, falta publicar o recuperar una instancia HTTPS con el responsable técnico. La imagen disponible se construye con `docker build -f deploy/Dockerfile -t proyecta .`; las dependencias de GCP siguen registradas como S-12. Esta guía prepara la demostración, no acredita un despliegue realizado.

## 2. Cuentas y alcance actual

| Cuenta sintética | Uso en la demo | Comportamiento web actual |
|---|---|---|
| `operaciones@example.test` | Apertura, parámetros y ajuste de C | Ve todos los registros y puede mantenerlos |
| `lider1@example.test` | Crear y avanzar la oportunidad | Ve y mantiene los propios; también puede modificar su meta |
| `ejecutivo@example.test` | Mostrar consulta sin edición | Está asociado a Líder 1 y ve sus registros; no tiene acceso a las páginas globales de Parámetros ni Auditoría |

La visibilidad del Ejecutivo y la edición de metas por líderes son temas de validación, porque difieren de los requerimientos iniciales. No prometer acceso ejecutivo consolidado para esta cuenta.

## 3. Caso sintético y cifras de control

Usar un perfil con 3 personas, tarifa de $2.600/h y dedicación del 100 %. En el alta la dedicación queda en 100 % por defecto. Las fechas elegidas evitan prorrateos y mantienen el ejemplo activo durante tres meses completos.

| Campo | Valor a ingresar |
|---|---|
| Tipo | Oportunidad |
| Servicio o proyecto | `DEMO JORGE 20-11` |
| Cliente, sector y manager | Elegir valores disponibles del catálogo sintético y anotar cuáles |
| Modalidad | NTT |
| Fecha de ingreso del registro | 01/12/2026 |
| Fin de vigencia del registro | Dejar vacío para no introducir otra condición |
| Cuenta | `No Aplica` |
| ID externo | `DEMO-JORGE-20261120` |
| Observaciones | `Caso sintético para validar cálculo, estados y trazabilidad.` |
| Perfil 1 | Elegir un perfil del catálogo |
| HC | `3` |
| Tarifa CLP/h | `2600` — reemplazar el valor que venga precargado |
| Ingreso del perfil | 01/12/2026 |
| Fin del perfil | 01/03/2027, primer día sin actividad |
| Studio, En Staffing, En Invoicing | Inicialmente desmarcados |
| Perfiles 2–4 | Vacíos |

Si se reutiliza el guion después de noviembre, mover el ingreso al primer día del mes siguiente y el fin al primer día posterior a tres meses activos. Una oportunidad nueva no admite perfiles con ingreso anterior a su creación.

**Cifras por mes completo, con 180 h y C = 90 %:**

| Momento del recorrido | P | Base mensual | MAB mensual |
|---|---:|---:|---:|
| Oportunidad nueva | 10 % | $1.404.000 | $126.360 |
| Flujo 2 · Propuesta en curso | 25 % | $1.404.000 | $315.900 |
| Flujo 3 · Propuesta entregada | 50 % | $1.404.000 | $631.800 |
| Adjudicada / En Curso | 100 % | $1.404.000 | $1.263.600 |

`Base = 3 × $2.600 × 180 × 100 % de dedicación × mes completo`.

`MAB = Base × P × C`. Al adjudicar, P = 100 % no elimina C: con C = 90 %, el monto sigue siendo $1.263.600 y no $1.404.000.

Son valores mensuales del caso. Las tarjetas del dashboard suman su horizonte y los registros visibles; no deben compararse directamente con una sola mensualidad.

## 4. Recorrido principal · 15–20 minutos

### Paso 1 · Mostrar el problema que resolvemos · 2 minutos

**Cuenta:** Operaciones. **Pantalla:** Dashboard.

1. Abrir **Resumen financiero** y señalar Forecast, MAB, Backlog contractual, Meta y Gap.
2. Abrir la ayuda de un indicador para mostrar su definición y cálculo.
3. Señalar el gráfico y su tabla **Ver datos mensuales**. La vista predeterminada combina tres meses anteriores y tres futuros. El selector del gráfico cambia gráfico y tabla; las tarjetas conservan el horizonte de la consulta de página.
4. Abrir brevemente **Detalle operativo y comercial** para mostrar que el análisis también permite revisar capacidad y cartera.

**Qué decir:** «Aquí queremos responder cuánto esperamos ingresar, de qué negocios viene y qué falta para la meta. Ahora vamos a crear uno y seguir su impacto».

**Precaución al explicar gap:** en el dashboard actual `Gap = Forecast − Meta`; negativo significa brecha. Los requerimientos usan `Meta − Forecast`. Presentar la diferencia como decisión pendiente P04, sin afirmar que ambas fórmulas usan el mismo signo.

### Paso 2 · Crear la oportunidad y explicar la vista previa · 3 minutos

**Cuenta:** Líder 1. **Pantalla:** Registros → Nuevo registro.

1. Completar el caso de la sección 3. Reemplazar tanto la tarifa como cualquier otro valor precargado.
2. Esperar la vista previa o pulsar **Actualizar vista previa**. Para diciembre debe mostrar Base **$1.404.000** y MAB **$126.360**.
3. Señalar que la vista previa todavía no guarda el registro. Para los tres meses activos, el Forecast inicial del caso es **$379.080**.
4. Pulsar **Guardar registro**. Anotar el código `OPD-####` asignado.
5. Verificar en la ficha: tipo Oportunidad, estado Pendiente, flujo 1, P = 10 % y C = 90 %.

**Qué decir:** «Los perfiles y tarifas explican la Base. Después distinguimos probabilidad comercial y confiabilidad operativa para obtener la MAB».

**Validación con Jorge:** P01, horas de referencia y fuente de comparación.

### Paso 3 · Avanzar el flujo y observar el cambio · 2 minutos

**Cuenta:** Líder 1. **Pantalla:** ficha → Estado y flujo.

1. En el formulario **Flujo**, elegir **2 · Propuesta en curso**.
2. Usar fecha efectiva **01/12/2026**, primer mes activo del caso sintético, y escribir `Demo: propuesta en preparación con participación de GDN-e` como motivo. Pulsar **Cambiar flujo**.
3. Verificar P = 25 % y MAB de diciembre **$315.900**.
4. Cambiar luego a **3 · Propuesta entregada**, con la misma fecha efectiva y motivo `Demo: propuesta técnica y económica entregada`.
5. Verificar P = 50 % y MAB de diciembre **$631.800**.

**Qué decir:** «La Base sigue igual. Cambia la ponderación por el avance comercial y el sistema conserva el motivo».

Usar **01/12/2026** como fecha efectiva en estos avances y en la adjudicación siguiente. Son fechas de negocio del caso sintético: el estado y el flujo se actualizan al guardar; la P se aplica al cálculo desde su mes de vigencia. No presentar esto como una transición programada para ejecutarse automáticamente en diciembre.

### Paso 4 · Adjudicar sin perder el negocio del Forecast · 2 minutos

**Cuenta:** Líder 1. **Pantalla:** ficha → Estado y flujo → Pasar a.

1. Elegir **Adjudicada**.
2. Fecha efectiva: **01/12/2026**. Motivo: `Demo: adjudicación e incorporación del caso sintético con vigencia en diciembre`.
3. Dejar el motivo de cierre/cancelación vacío y pulsar **Cambiar estado**.
4. Verificar: tipo **Demanda**, estado **Adjudicada**, P fija en **100 %**, C = **90 %** y MAB de diciembre **$1.263.600**.
5. Explicar que el caso permanece en la MAB y se reconoce en la vista de Backlog confirmado; no se suma por segunda vez al Forecast.

**Qué decir:** «Adjudicar no hace desaparecer el ingreso. Seguimos mostrándolo mientras confirmamos su ejecución y su relación con Invoicing».

**Validación con Jorge:** P02 y P03: momento del 100 % y tratamiento posterior de Invoicing.

### Paso 5 · Dejar seguimiento y demostrar trazabilidad · 2 minutos

**Cuenta:** Líder 1. **Pantalla:** ficha → Bitácora / Auditoría.

1. Agregar una entrada de tipo disponible en el selector, con contenido `Demo: servicio adjudicado; coordinar incorporación de tres perfiles`.
2. Próxima acción: `Validar fecha de ingreso y revisar previsión en Invoicing`. Fecha compromiso: **23/11/2026**. Pulsar **Agregar a la bitácora**.
3. Mostrar autor, fecha y seguimiento. Una corrección se agrega como nueva entrada.
4. En **Auditoría** de la ficha, señalar los cambios de estado, tipo y probabilidad, sus valores anterior/nuevo y su motivo.
5. Mostrar **Δ Forecast 12 m** y aclarar que es la diferencia del horizonte de cálculo, no necesariamente la de un solo mes. No sumar los impactos de cada campo de una misma operación: varios eventos pueden describir el mismo cambio total.

**Qué decir:** «La bitácora explica el seguimiento. La auditoría permite reconstruir qué cambió y cuál fue su efecto económico».

### Paso 6 · Encontrar el registro desde el dashboard · 2 minutos

**Cuenta:** Operaciones o Líder 1.

1. Abrir el dashboard, desplegar **Filtrar** y buscar el código OPD anotado. Aplicar.
2. Revisar el detalle de diciembre en la tabla mensual. En el caso adjudicado debe aportar **$1.263.600**.
3. Desde una tarjeta de ingresos, abrir **Registros** y luego la ficha del caso. Desplegar el mes en su cálculo para ver componentes, tarifa, HC y fracción activa.
4. Para comparar tarjetas y tabla en un mismo horizonte, preparar esta dirección con el dominio real y el código obtenido:

   ```text
   URL/?vista=futuro_6m&desde=2026-11&meses=6&q=OPD-XXXX
   ```

   En el selector del gráfico elegir también **A futuro 6 meses**. Así se observa noviembre–abril; este caso solo aporta en diciembre, enero y febrero. Antes de ajustar C, su Forecast total es **$3.790.800**, su MAB es igual y su Backlog contractual es cero.

**Qué decir:** «Desde el consolidado podemos llegar al negocio y a los datos que justifican su monto».

**Cuidado con la meta:** buscar un único registro no reduce la meta a la de ese negocio. Sigue siendo la meta de los líderes y meses de la consulta. No describir esa cobertura como rentabilidad o cumplimiento individual de la oportunidad.

### Paso 7 · Mostrar C con vigencia y permisos · 2 minutos

**Cuenta:** Operaciones. **Pantalla:** ficha del mismo registro → Probabilidad / Confiabilidad.

1. En C %, ingresar **80**.
2. En **Rige desde**, ingresar **01/01/2027**. Motivo: `Demo: riesgo operativo de disponibilidad desde enero`. Pulsar **Cambiar confiabilidad**.
3. Revisar el cálculo mensual: diciembre mantiene **$1.263.600**; enero y febrero pasan a **$1.123.200** cada uno. La Base sigue en $1.404.000.
4. El Forecast del caso para sus tres meses activos pasa de **$3.790.800** a **$3.510.000**: reducción de **$280.800**.
5. Mostrar la historia mensual y el evento auditado. La etiqueta actual de C puede mostrar el nuevo valor; para explicar su vigencia, usar el detalle de cada mes.

**Qué decir:** «El riesgo operativo se aplica desde el mes indicado. Los meses anteriores conservan su confiabilidad».

### Paso 8 · Cerrar con consulta ejecutiva y decisiones · 1–2 minutos

**Cuenta:** Ejecutivo, en su sesión independiente.

1. Buscar el mismo registro: es de Líder 1, a quien está asociado este Ejecutivo.
2. Abrir la ficha y mostrar el mensaje de solo lectura y la ausencia de acciones de edición.
3. Aclarar que la cuenta actual tiene ese alcance de lectura, y confirmar si Jorge necesita una visión ejecutiva global.
4. Volver a la pauta y cerrar P01–P05 con respuestas explícitas, responsables y fechas.

**Cierre sugerido:** «Vimos la oportunidad, su avance, el efecto en ingresos y la explicación de cada cambio. Necesitamos confirmar las horas, cuándo aplica el 100 %, cómo convive con Invoicing, el signo del gap y quién fija las metas».

## 5. Extensiones si queda tiempo

- **En Curso e Invoicing:** con Líder 1, pasar de Adjudicada a En Curso con motivo y fecha. El código coloca flujo 6 y mantiene P = 100 %. Mostrar los indicadores En Staffing / En Invoicing en Datos del registro; marcarlos no integra automáticamente los sistemas ni cambia la bolsa. Si falta Invoicing, conversar sobre la alerta deseada; el semáforo completo no está disponible.
- **Continuidad:** con Operaciones, filtrar Tipo = Continuidad, abrir un registro sintético y mostrar contrato, monto mensual y vigencia. Pertenece al Backlog contractual; no aplicar allí la fórmula ponderada de la MAB.
- **Parámetros MAB:** mostrar la historia de horas y confiabilidad inicial. Si se cambia algo durante una extensión, hacerlo al final, con motivo y vigencia futura: afecta otros registros y altera las cifras del guion. Cambiar C inicial afecta nuevos registros, no los existentes.
- **Metas comerciales por líder:** mostrar el mantenedor actual y confirmar P05. La especificación original indicaba metas por sector, editadas por Operaciones.

## 6. Alcance que debe explicarse con precisión

| Disponible en el código revisado | Limitación o decisión pendiente |
|---|---|
| Alta, perfiles, tarifas, estados, flujo, P/C y cálculo explicado | Horas y momento del 100 % pendientes de validación del sponsor |
| Dashboard, filtros, detalle mensual, bitácora y auditoría | Gap con signo diferente al requisito; gráfico y tarjetas pueden estar en horizontes distintos |
| Continuidades y ficha de contrato | Sin conversión automática de demanda a continuidad |
| Mantenedor de metas por líder | Difiere de metas por sector y permisos de los requerimientos |
| Tres roles y sesiones | Ejecutivo vinculado a un líder; cuentas compartidas de demostración |
| Datos sintéticos y almacenamiento en memoria | Reiniciar pierde cambios, sesiones, bitácora y auditoría de la demo |
| Motor y piezas de IA/simulación en el repositorio | Asistente y simulador no están expuestos en la app principal |
| Indicadores y conteos operativos | Sin cierre mensual/puente, exportación Excel ni panel completo de calidad en la app principal |

La guía antigua [docs/demo.md](demo.md) describe generación JSON, un fixture de cuatro registros y un recorrido sugerido con simulación. Es apoyo técnico; generar esos archivos no los carga automáticamente al servidor web. El flujo principal de esta guía no depende de ellos.

## 7. Si algo falla durante la presentación

| Situación | Acción |
|---|---|
| URL sin respuesta | Comprobar `/health`, dar tiempo al arranque y pasar a la instancia local compartida o a capturas si persiste |
| Sesión vencida | Iniciar sesión otra vez; recuperar el caso por código. Si hubo reinicio, recrearlo desde el caso sintético |
| Cuenta no entra | Revisar correo y clave por canal privado; evitar repetir cinco intentos, porque existe bloqueo temporal |
| Vista previa sin resultado | Completar HC, tarifa y fecha de ingreso; usar **Actualizar vista previa**. Leer el error visible antes de guardar |
| Monto distinto al esperado | Comprobar 180 h, tarifa 2600, dedicación, fechas, P/C vigentes, mes mostrado y filtros |
| Conflicto de versión | Abrir la versión vigente, comparar y revisar el borrador conservado antes de volver a guardar |
| Ejecutivo no encuentra el caso | Confirmar que el owner sea Líder 1 y que se usa su Ejecutivo asociado |
| KPI y tabla no coinciden | Igualar consulta de página y vista del gráfico; comparar primero el mismo mes y los mismos registros |

## 8. Versión abreviada · 7 minutos

1. **1 min:** explicar Forecast = Backlog contractual + MAB y el problema de Invoicing.
2. **2 min:** crear el caso y mostrar Base $1.404.000 / MAB $126.360 en la vista previa.
3. **1 min:** avanzar a Propuesta entregada y mostrar MAB $631.800.
4. **1 min:** adjudicar; mostrar Demanda, P = 100 % y MAB $1.263.600.
5. **1 min:** mostrar bitácora y auditoría del cambio.
6. **1 min:** confirmar horas, P al adjudicar, tratamiento de Invoicing, gap y metas; asignar las respuestas pendientes.

## 9. Evidencia y acciones posteriores

**Verificación local de preparación:** el 20/11/2026 se ejecutaron `tests/integration/test_app.py` y `tests/integration/test_entrega2_observaciones.py`: **32 pruebas aprobadas**. Cubren alta/vista previa, estados, P/C, vigencias, auditoría, parámetros, metas, filtros y permisos. Esto no acredita el funcionamiento del hosting ni sustituye el ensayo en navegador de la URL desplegada.

**Incidencia de preparación:** en una comprobación directa se observó que el primer cambio de P, efectivo en el mismo mes de creación, podía mostrar P actualizada en la ficha y conservar el valor inicial en el cálculo por empate de marcas de tiempo de las vigencias. El guion usa el mes siguiente como vigencia inicial del ejemplo. Registrar y revisar esta incidencia con backend; no afirmar que las pruebas anteriores cubren ese caso.

Después de la reunión:

- Guardar el código OPD, capturas sintéticas y decisiones antes de cualquier reinicio del servicio.
- Completar el registro de acuerdos de la pauta, sin asumir aprobación por falta de comentarios.
- Trasladar las decisiones a requerimientos y tareas; registrar diferencias que exijan cambios de código.
- Registrar quién hará la validación siguiente y la fecha comprometida de acceso online / infraestructura.

**Referencias:** [Entrega 2](../ENTREGA_2.md), [requerimientos](fuentes/requerimientos.md), [rutas de registros](../src/proyecta/interfaces/web/routes/registros.py), [dashboard actual](../src/proyecta/application/use_cases/dashboard.py), [parámetros y metas](../src/proyecta/interfaces/web/routes/admin.py) y [almacenamiento en memoria](../src/proyecta/infrastructure/memoria.py).
