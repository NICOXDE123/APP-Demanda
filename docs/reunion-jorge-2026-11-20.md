# Reunión con Jorge · preguntas y validación de negocio

**Fecha:** 20 de noviembre de 2026.  
**Participantes de referencia:** Jorge Escobar (sponsor / Operaciones) y Alfredo San Juan (PO), con el equipo que participe.  
**Objetivo:** validar que las cifras y el flujo de Proyecta representan la operación, resolver las decisiones que afectan el cálculo y acordar prioridades para la siguiente entrega.  
**Documento complementario:** [Guion de demo online](demo-online-flujo-principal.md).

> Esta es una pauta para conversar y registrar decisiones. Las respuestas están pendientes; tener una regla implementada no equivale a tenerla aprobada por Jorge.

## 1. Contexto para abrir la reunión

En el levantamiento del 15/10, Jorge explicó que Operaciones necesita anticipar ingresos y capacidad a 3, 6 y 12 meses, sin consolidar manualmente planillas. La visión de los primeros tres meses es especialmente relevante. La solución debe permitir entender de dónde viene cada cifra y quién cambió sus supuestos.

Proyecta hoy permite registrar oportunidades, perfiles, HC y tarifas; avanzar estados y flujo; calcular Base, MAB y Forecast; consultar el detalle mensual; y mantener bitácora y auditoría. 

## 3. Preguntas prioritarias

### P01 · ¿Cuántas horas mensuales debemos usar? · S-01 / H-04

**Contexto:** la plantilla tiene montos consistentes con 163 h. Hoy estamos usando 180 h, con un parámetro editable por Operaciones y vigencia mensual. Pasar de 163 a 180 aumenta la Base aproximadamente un 10,43 %, aunque no cambien personas ni tarifa.

**Preguntas para Jorge:**

- ¿Confirmamos 180 h para el MVP o debemos conservar 163 h? ¿Es una convención comercial o depende del cliente, contrato o mes?

**Ejemplo para decidir:** 3 HC × $2.600/h × 163 h = **$1.271.400** de Base; con 180 h = **$1.404.000**. Diferencia: **$132.600 mensuales** antes de P y C.

**Cerrar con:** valor autorizado, alcance, mes de vigencia y persona que lo valida.

### P02 · ¿Cuándo una oportunidad pasa a demanda y a P = 100 %? · H-01 / S-02

**Contexto:** la v1.1 y el código fijan P en 100 % al adjudicar y cambian el tipo a Demanda. La confiabilidad permanece independiente, inicialmente en 90 %. El resumen antiguo menciona 90 % al adjudicar: esa interpretación fue reemplazada en la v1.1, pero aún requiere validación expresa del sponsor.

**Preguntas para Jorge:**

- Si ganamos la venta y aún faltan candidatos, ¿ya corresponde Demanda / Adjudicada con P = 100 %?
- ¿O el 100 % debe esperar a tener perfiles seleccionados y fecha confirmada? ¿Qué evidencia demuestra cada hito?
- ¿Aceptamos «Perfiles seleccionados» como sexta etapa del flujo y qué distingue ese hito de «En Curso»?

**Cerrar con:** evento de adjudicación, evento de confirmación de perfiles y condiciones para iniciar el servicio. Separar certeza de la venta de certeza de ejecución.

### P05 · ¿Quién fija las metas y sobre qué unidad? · S-06

**Contexto:** la especificación pide metas por sector y mes, editadas solo por Operaciones. La aplicación actual mantiene metas por líder, permite al líder editar la propia y suma las metas de los líderes visibles. 

**Preguntas para Jorge:**

- ¿La meta oficial corresponde al sector, al líder o a ambos? ¿Cómo consolidamos a un líder que participa en varios sectores?
- ¿Un líder puede modificar su propia meta o solo proponerla para aprobación de Operaciones?

### P06 · ¿Quién puede ver y editar qué información?

**Contexto:** Operaciones puede mantener registros de todos; cada líder ve y edita los propios. El Ejecutivo de la semilla está asociado a Líder 1 y solo ve sus registros en la web; no accede a las páginas globales de Parámetros ni Auditoría. Esto difiere de la visión ejecutiva consolidada descrita originalmente.

**Preguntas para Jorge:**

- ¿El Ejecutivo necesita una visión global, por sector o únicamente del líder asignado?
- ¿Los líderes deben colaborar por sector o la propiedad individual del registro es suficiente? ¿Cómo se cubren ausencias y traspasos?
- ¿Quién puede consultar la auditoría y quién puede cambiar C, metas y fechas comprometidas?

**Cerrar con:** matriz por rol, alcance de lectura, alcance de edición y dos o tres usuarios de referencia para validarla después. No registrar contraseñas aquí.

### P07 · ¿Cómo incorporamos la continuidad contractual? · S-05

**Contexto:** Continuidad usa una ficha de contrato y aporta al Backlog contractual al 100 %, sin descuento por C. Puede calcularse desde un monto mensual pactado o, si no hay monto, desde los perfiles. No existe conversión automática de Demanda a Continuidad en la interfaz actual.

**Preguntas para Jorge:**

- ¿Qué evento hace que una demanda nueva se considere continuidad? ¿Al siguiente mes, al facturarse o al cumplir otra condición?
- ¿La fuente contractual entrega monto mensual, HC, fecha de inicio, fecha de término y renovaciones? ¿Quién mantiene esos datos?
- Si el monto del contrato difiere de la suma de perfiles, ¿qué cifra manda y cómo explicamos la diferencia?
- ¿Cómo evitamos dejar vigentes una demanda y su continuidad por el mismo servicio y mes?

**Cerrar con:** fuente, dueño, criterio de paso a continuidad y mecanismo para evitar duplicados.

### P08 · ¿Qué debe quedar listo para aceptar la siguiente entrega? · S-12 / S-15

**Contexto:** el plan de E2 fija la siguiente entrega para el **25/11/2026**. Esa es una fecha documentada, no una confirmación de avance. Persistencia, infraestructura y varias funciones siguen pendientes en el código revisado.

**Preguntas para Jorge:**

- ¿Cuáles son los tres resultados indispensables para esa entrega: continuidad/metas, calidad, exportación, cierre mensual u otro?
- ¿Quién de NTT DATA habilita el proyecto GCP, regiones, permisos y referente técnico, y para cuándo?
- ¿Quién probará el flujo por cada rol y qué caso de negocio debe aprobar para considerar aceptado el producto?
- Si una dependencia no llega a tiempo, ¿qué alcance de demostración y validación acordamos?

**Cerrar con:** prioridades ordenadas, responsable de la dependencia, fecha y criterio observable de aceptación.

## 4. Reglas complementarias para confirmar con casos

| Tema | Regla documentada / comportamiento actual | Pregunta concreta |
|---|---|---|
| Confiabilidad · RN-35–38 | Inicial de 90 % para oportunidades y demandas; Operaciones puede cambiarla con motivo y vigencia mensual. El Backlog contractual no se descuenta | ¿Qué riesgos representa C y cómo distinguimos esos riesgos de P? ¿Quién justifica su valor? |
| Vigencias · H-04 / H-06 | Horas, P y C tienen vigencia mensual; tarifas tienen historia por perfil | Si cambiamos C el día 20, ¿debe afectar todo ese mes o solo los días restantes? ¿Se permiten correcciones retroactivas? |
| Prorrateo | Montos según días calendario activos. La fecha fin de perfil es el primer día sin actividad; la fecha fin contractual es el último día cubierto | Si el último día trabajado es el 15, ¿Operaciones espera ingresar 15 o 16 como fin? ¿El criterio calendario coincide con su facturación? |
| HC | El monto prorratea; el HC de cierre cuenta personas activas al fin del mes | Si alguien trabaja medio mes y sale antes del cierre, ¿aceptamos monto parcial y HC de cierre cero? ¿Necesitan además HC promedio? |
| Cierre · S-03 / H-02 | Pérdida, Desestimada y Duplicado salen desde el mes de cierre. Cancelada por cliente y Término de servicio prorratean hasta su fecha | ¿Estos motivos cubren sus casos? ¿«Cerrada» significa término del ciclo o siempre pérdida? |
| StandBy | Sale del cálculo; al reactivar recupera el estado previo. El código actual excluye el registro en toda la consulta mientras está pausado | ¿Deben conservarse los ingresos anteriores a la pausa? ¿Qué fecha y condición permiten reactivarlo? |
| Demanda directa · S-07 | Nace Adjudicada, P = 100 %, flujo 3–5, con perfil y motivo | ¿Una ampliación o renovación se registra así o como continuidad? ¿Qué impide duplicar el negocio anterior? |
| Catálogos · S-04 / S-10 | Hay una propuesta de normalización y catálogos sintéticos; falta validar equivalencias reales | ¿Quién aprueba alias de sectores, managers y clientes? ¿Qué fuente es oficial y qué valores no deben fusionarse? |
| Datos obligatorios | La oportunidad puede nacer sin perfiles, sin aportar Base; para adjudicar se exige al menos un perfil con ingreso | ¿Qué datos mínimos debe tener una oportunidad temprana y cuáles exigimos antes de adjudicar? |
| Seguimiento | Bitácora de solo inserción; cambios relevantes con auditoría y motivo | ¿Necesitan próxima acción y fecha compromiso obligatorias? ¿Quién revisa los pendientes semanalmente? |
| Calidad | Se especifica alerta roja para En Curso sin Invoicing; la interfaz actual no tiene el semáforo completo | ¿Debe advertir o impedir el avance? ¿Quién debe corregirlo y en cuánto tiempo? |
| Cadencia · S-14 | Dashboard en línea y cierre mensual definido en requisitos; cierre y puente aún pendientes en la app | ¿Qué día cierran y quién autoriza una corrección de un período cerrado? |

Estas preguntas buscan validar la regla deseada. Cuando el comportamiento actual difiera, registrar por separado la decisión de negocio y la tarea de implementación.

## 5. Confirmar utilidad y adopción

- ¿Qué decisión tomas hoy con la planilla y deberías poder tomar más rápido con Proyecta?
- ¿Qué tres cifras revisarías primero un lunes? ¿Qué desglose necesitas: sector, líder, cliente, modalidad o tecnología?
- ¿Qué reporte debe poder exportarse para reemplazar un trabajo manual concreto?
- ¿Qué frecuencia de actualización exigirías a los líderes y quién se responsabiliza por información vencida?
- ¿Con quién ensayamos un caso representativo después de esta reunión? Para esta demo se mantienen datos sintéticos; una eventual migración real requiere otra etapa y revisión de Operaciones.

## 6. Registro de acuerdos para completar en vivo

| ID | Decisión o pregunta | Respuesta exacta / regla acordada | Excepciones y vigencia | Responsable | Fecha compromiso | Estado / evidencia |
|---|---|---|---|---|---|---|
| P01 | Horas mensuales | | | | | Pendiente |
| P02 | Adjudicación, P y sexta etapa | | | | | Pendiente |
| P03 | Bolsas e Invoicing | | | | | Pendiente |
| P04 | Fórmula y signo de gap | | | | | Pendiente |
| P05 | Metas y permisos | | | | | Pendiente |
| P06 | Visibilidad por rol | | | | | Pendiente |
| P07 | Continuidad contractual | | | | | Pendiente |
| P08 | Alcance y GCP | | | | | Pendiente |
| R01 | Otras reglas de la sección 4 | | | | | Pendiente |

**Antes de terminar:** leer los acuerdos en voz alta; distinguir «confirmado», «requiere ajuste» y «pendiente de respuesta»; asignar responsable y fecha a cada pendiente. Alfredo debe trasladar después los acuerdos a requerimientos, tareas y criterios de aceptación, sin marcar decisiones abiertas como aprobadas por omisión.

## 7. Fuentes y alcance de la preparación

Revisión del repositorio local al 20/11/2026. No se verificó una instancia online: la URL sigue sin completar en E2.

- [Requerimientos v1.1](fuentes/requerimientos.md): §§8–10 y 14; H-01 a H-07 y Anexo A.
- [Primera reunión con el sponsor](fuentes/resumen_transcripcion_reunion.md): necesidades, probabilidades e Invoicing. Su §9 contiene la interpretación antigua de 90 % al adjudicar, reemplazada por v1.1.
- [Entrega 2](../ENTREGA_2.md): alcance documentado, limitaciones y plan. Algunas descripciones quedaron atrás del código actual.
- Código contrastado: [estados](../src/proyecta/domain/states.py), [bolsas](../src/proyecta/domain/engine/bags.py), [gap del motor](../src/proyecta/domain/engine/gap.py), [dashboard](../src/proyecta/application/use_cases/dashboard.py), [metas y permisos web](../src/proyecta/interfaces/web/routes/admin.py) y [visibilidad de fichas](../src/proyecta/interfaces/web/routes/registros.py).
